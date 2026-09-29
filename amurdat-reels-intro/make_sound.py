"""Synthesize the intro's soundtrack and mux it onto the rendered video.

Everything is generated here (no samples), kept soft and low: a quiet
open pad and wind while the days pass, muffled wooden thuds on the three
cuts, a faint pen scratch while the lines draw, a small chime as the book
appears, a light shimmer as the script writes, and a warm chord that
resolves under the final logo and fades out by the end. All pitched
sounds sit in D.

Run after rendering:
    python make_sound.py [video.mp4]      # default: amurdat_intro.mp4
Writes assets/soundtrack.wav and replaces the video's audio track.
"""

import subprocess
import sys
import wave

import numpy as np
from scipy.signal import butter, sosfilt

SR = 48000
LENGTH = 10.0
TARGET_LUFS = -24.0            # quiet; platforms normalise louder anyway

# Event times (seconds), matching amurdat_intro.py's frame timeline.
CUTS = (89 / 30, 116 / 30, 138 / 30)       # each topple starts at midnight
LINES = (153 / 30, 195 / 30)               # lines draw
BOOK = 195 / 30                            # book fades in
SCRIPT = (207 / 30, 225 / 30)              # script writes
LOGO = 225 / 30                            # tagline and wordmark settle

rng = np.random.default_rng(7)
t = np.arange(int(SR * LENGTH)) / SR


def hz(note):
    """MIDI note number -> Hz."""
    return 440.0 * 2 ** ((note - 69) / 12)


def env(points):
    """Piecewise-linear envelope through (time, level) points."""
    ts, vs = zip(*points)
    return np.interp(t, ts, vs)


def band(noise, lo, hi, order=2):
    return sosfilt(butter(order, [lo, hi], btype="band", fs=SR, output="sos"), noise)


def lowpass(x, f, order=2):
    return sosfilt(butter(order, f, btype="low", fs=SR, output="sos"), x)


def pad(notes, amp_env, detune=0.25):
    """Soft pad: each note a sine plus a slightly detuned twin per channel
    and a faint octave, so it breathes without any edge."""
    left, right = np.zeros_like(t), np.zeros_like(t)
    for n in notes:
        f = hz(n)
        ph = rng.uniform(0, 2 * np.pi, 4)
        left += np.sin(2 * np.pi * f * t + ph[0]) + 0.6 * np.sin(2 * np.pi * (f + detune) * t + ph[1])
        right += np.sin(2 * np.pi * f * t + ph[2]) + 0.6 * np.sin(2 * np.pi * (f - detune) * t + ph[3])
        left += 0.08 * np.sin(4 * np.pi * f * t)
        right += 0.08 * np.sin(4 * np.pi * f * t)
    scale = amp_env / len(notes)
    return left * scale, right * scale


def thud(at):
    """Muffled wooden knock: a low tone that sags in pitch, plus a short,
    dark noise tick. Soft attack so it never snaps."""
    s = t - at
    on = s >= 0
    s = np.where(on, s, 0)
    f = 95 + 55 * np.exp(-s * 30)
    body = np.sin(2 * np.pi * np.cumsum(np.where(on, f, 0)) / SR) * np.exp(-s * 14)
    tick = lowpass(rng.standard_normal(t.size), 900) * np.exp(-s * 55)
    attack = np.clip(s / 0.006, 0, 1)
    return (body * 0.9 + tick * 0.35) * attack * on


def chime(at, note, amp):
    """Small bell: a few inharmonic partials with long, gentle decays."""
    s = t - at
    on = s >= 0
    s = np.where(on, s, 0)
    f = hz(note)
    x = np.zeros_like(t)
    for ratio, level, decay in ((1.0, 1.0, 1.6), (2.76, 0.28, 3.2), (5.4, 0.08, 5.0)):
        x += level * np.sin(2 * np.pi * f * ratio * s) * np.exp(-s * decay)
    return x * np.clip(s / 0.012, 0, 1) * on * amp


def main():
    L, R = np.zeros_like(t), np.zeros_like(t)

    # Opening pad, open Dsus2 (D3 A3 E4): under the days passing, then held
    # quietly under the drawing until the final chord resolves it.
    pl, pr = pad([50, 57, 64], env([(0, 0), (0.6, 0.22), (4.6, 0.22), (5.2, 0.12),
                                    (6.8, 0.12), (7.9, 0)]))
    L += pl
    R += pr

    # Wind: breathy noise that swells as time speeds up, then settles.
    wind_env = env([(0, 0.0), (0.8, 0.05), (2.8, 0.16), (4.7, 0.22), (5.4, 0)])
    wobble = 1 + 0.25 * np.sin(2 * np.pi * 0.35 * t) * np.sin(2 * np.pi * 0.13 * t + 1)
    L += band(rng.standard_normal(t.size), 250, 1400) * wind_env * wobble * 0.5
    R += band(rng.standard_normal(t.size), 250, 1400) * wind_env * wobble[::-1] * 0.5

    # Three soft cuts.
    for at in CUTS:
        x = thud(at) * 0.26
        L += x
        R += x

    # Pen scratch: quiet, papery, in uneven strokes while the lines draw.
    a, b = LINES
    strokes = 0.35 + np.clip(np.sin(2 * np.pi * 3.1 * t) + 0.4 * np.sin(2 * np.pi * 5.3 * t + 1), 0, None)
    scratch_env = env([(a, 0), (a + 0.2, 0.06), (b - 0.2, 0.06), (b, 0)]) * strokes
    scratch = band(rng.standard_normal(t.size), 2200, 6000) * scratch_env
    L += scratch
    R += scratch * 0.8

    # Book appears: a small chime on A5, a touch to the right.
    c = chime(BOOK, 81, 0.16)
    L += c * 0.8
    R += c

    # Script: a light shimmer of tiny high notes from D pentatonic.
    a, b = SCRIPT
    for i, note in enumerate((86, 90, 93, 88, 95, 91, 98)):
        at = a + (b - a) * i / 7 + rng.uniform(-0.02, 0.02)
        s = chime(at, note, 0.04)
        pan = 0.3 + 0.4 * (i / 6)
        L += s * (1 - pan) * 1.4
        R += s * pan * 1.4

    # Final logo: D major (D3 A3 D4 F#4 A4) resolves in and fades out by 10s.
    pl, pr = pad([50, 57, 62, 66, 69],
                 env([(LOGO - 0.4, 0), (LOGO + 0.6, 0.3), (8.6, 0.3), (9.9, 0)]), detune=0.18)
    L += pl
    R += pr

    # Keep everything soft: tame the top end and roll off sub rumble.
    mix = np.stack([L, R])
    mix = lowpass(mix, 9000)
    mix = sosfilt(butter(2, 40, btype="high", fs=SR, output="sos"), mix)
    fade = np.clip(t / 0.05, 0, 1) * np.clip((LENGTH - t) / 0.05, 0, 1)
    mix *= fade
    mix /= np.abs(mix).max()

    write_wav("assets/soundtrack.wav", mix)
    gain = TARGET_LUFS - measure_lufs("assets/soundtrack.wav")
    mix *= 10 ** (gain / 20)
    write_wav("assets/soundtrack.wav", mix)

    video = sys.argv[1] if len(sys.argv) > 1 else "amurdat_intro.mp4"
    out = video.replace(".mp4", "_sound.mp4")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", video, "-i", "assets/soundtrack.wav",
                    "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-b:a", "256k",
                    "-shortest", "-movflags", "+faststart", out], check=True)
    subprocess.run(["mv", out, video], check=True)
    print(f"integrated {measure_lufs('assets/soundtrack.wav'):.1f} LUFS, "
          f"peak {20 * np.log10(np.abs(mix).max()):.1f} dBFS")


def write_wav(path, stereo):
    pcm = (np.clip(stereo.T, -1, 1) * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def measure_lufs(path):
    out = subprocess.run(["ffmpeg", "-hide_banner", "-i", path, "-af", "ebur128", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    summary = out[out.rindex("Integrated loudness"):]
    return float(summary.split("I:")[1].split("LUFS")[0])


if __name__ == "__main__":
    main()
