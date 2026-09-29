#!/usr/bin/env bash
# High-quality master: 1080x1920 at 60fps, rendered to lossless PNG frames,
# encoded once to high-bitrate H.264, then the soundtrack is added.
set -euo pipefail
cd "$(dirname "$0")"

python prepare_assets.py
rm -rf media/images/amurdat_intro
AMURDAT_FPS=60 manim -qh --format png --disable_caching amurdat_intro.py AmurdatIntro

ffmpeg -y -loglevel error -framerate 60 -pattern_type glob -i 'media/images/amurdat_intro/*.png' \
  -c:v libx264 -preset slow -crf 14 -tune animation -pix_fmt yuv420p \
  -profile:v high -level 4.2 -movflags +faststart amurdat_intro.mp4

python make_sound.py amurdat_intro.mp4
