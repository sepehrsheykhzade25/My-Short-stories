# WireGuard / Cloudflare WARP

All of these use **Cloudflare WARP**, a free service that runs on WireGuard.
Plain WireGuard is easy for DPI to spot, so in Iran it usually only works
with "noise" (junk packets sent before the handshake) or WARP-in-WARP.
Options 1 and 2 both do that.

## Option 1: Hiddify + IRCF WARP subscription (recommended)

From [ircfspace/warpsub](https://github.com/ircfspace/warpsub), made by IRCF for
users in Iran. The Hiddify app creates its own WARP account on your device
(`warp://auto`), so no shared keys are needed, and it adds noise packets.

1. Install **Hiddify** (Android, iOS, Windows, macOS, Linux; GitHub: hiddify/hiddify-app).
2. **New profile** → **Add from URL**, then paste:
   ```
   https://raw.githubusercontent.com/ircfspace/warpsub/main/export/warp
   ```
3. Pick one and connect:
   - `WarpInWarp 🇩🇪`: WARP inside WARP, **exits in Germany**. Usually the best one to try first.
   - `Warp 🇮🇷` / `Warp2` / `Warp3`: single WARP with different noise settings.
4. If it connects but is slow or drops, go to Hiddify **Config options → WARP**,
   use **Endpoint scanner** (or change the endpoint), then try the next profile.

`hiddify-warp-subscription.txt` is a copy of that subscription as of
2026-10-02. Prefer the URL above, because IRCF updates it.

## Option 2: WireGuard links with noise (v2rayNG / Hiddify / MahsaNG)

`wireguard-links.txt` has 3 shared WARP accounts from a Telegram collector.
Two of them include noise settings (`wnoise`, `wnoisecount`, …).
Copy the file's contents and use **Import from clipboard** in v2rayNG or Hiddify.

## Option 3: the official WireGuard app

`warp-1.conf`, `warp-2.conf`, `warp-3.conf` are the same 3 accounts as plain
`.conf` files. In the WireGuard app: **+** → **Import from file**.
The WireGuard app can't send noise packets, so on filtered networks these may
not connect. They're here because that's the app you used before.

If one connects but has no internet, change the `Endpoint` line to another
Cloudflare WARP IP and port, e.g. `162.159.192.1:2408`, `162.159.195.1:908`,
`188.114.98.224:1701` or `188.114.96.1:878`. Many ports and IPs work, and
filtering differs by ISP.

## Option 4: Oblivion (WARP made for Iran)

**Oblivion** (Android) / **Oblivion Desktop** (Windows/macOS/Linux) by
bepass-org (GitHub: bepass-org/oblivion, bepass-org/oblivion-desktop) is a
one-tap WARP client built for Iran, with WARP-in-WARP ("gool") and a Psiphon
mode, and you can pick the exit country (Germany included). No configs needed.

## Notes

- The keys in `wireguard-links.txt` and `warp-*.conf` are already public and
  shared by many people, so speed can drop or Cloudflare can disable them.
  Option 1 or 4 generates your own account instead.
- WARP's exit location depends on Cloudflare routing. Only WarpInWarp 🇩🇪 /
  Oblivion let you aim for Germany.
