# V2Ray / VLESS configs

> Personal scratch space. Not part of the short-stories site.

Collected **2026-10-02** from public free-config collectors. Only encrypted
VLESS (Reality / TLS) configs are included. The first 45 configs posted
here all failed for you, so they were removed from these lists.

## Files

| File | Count | What it is |
|---|---|---|
| `iran-telegram-fresh.txt` | 315 | **Try this first.** Fresh configs gathered from Iranian Telegram channels, any location. ☁️ = goes through Cloudflare CDN (often the only kind that works when foreign IPs are filtered). Others are labelled with their server country. |
| `germany-vless.txt` | 380 | Configs whose server is in Germany. Many are on Hetzner/OVH IP ranges, which are often filtered. |
| `*-base64.txt` | | Same lists in subscription format. |
| `subscriptions.txt` | | Auto-updating public subscription links. |

## Subscription URLs

```
https://raw.githubusercontent.com/sepehrsheykhzade25/My-Short-stories/ccr-04933d2d-6lc4h7/v2ray-configs/iran-telegram-fresh-base64.txt
https://raw.githubusercontent.com/sepehrsheykhzade25/My-Short-stories/ccr-04933d2d-6lc4h7/v2ray-configs/germany-vless-base64.txt
```

If raw.githubusercontent.com does not load for you, open the `.txt` file on
GitHub, copy all of it, and use **Import from clipboard**.

## Testing

1. Import a whole list. Large lists are fine, since the test runs in parallel.
2. v2rayNG: ⋮ → **Test all configurations real delay** (not "TCPing"). Wait
   until it finishes; it can take a minute or two with 300+ configs.
3. ⋮ → **Sort by test results**. Working ones show a number like `350ms`;
   dead ones show `-1` / timeout. Then ⋮ → **Remove invalid configs**.

### If *everything* shows 0ms / -1

When every single config fails, the cause is usually on the device rather
than in the configs:

- Update the app (v2rayNG ≥ 1.9 or Hiddify / v2rayN latest). Old cores don't
  understand Reality/XHTTP, and every test fails.
- Turn off any other VPN or proxy app, and Private DNS (Android settings).
- Settings → enable **Allow insecure** if your app has it (needed for some TLS configs).
- Real-delay test URL: if it's `google.com/generate_204`, try changing it to
  `https://cp.cloudflare.com/generate_204` (v2rayNG: Settings → "Real delay test URL").
- Try a different network (mobile data vs. home Wi-Fi). Filtering differs a lot between ISPs.

## Caveats

- Not verified from your location; only your own real-delay test can say what works.
- Free configs die within hours or days; re-pull from `subscriptions.txt`.
- Servers are run by unknown third parties. Use HTTPS only, and avoid sensitive logins.
- This repo is public.
