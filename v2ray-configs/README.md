# V2Ray / VLESS configs (Germany)

> Personal scratch space. Not part of the short-stories site.

Collected on **2026-10-02** from public free-config aggregators on GitHub.
Only **encrypted** VLESS configs (Reality or TLS) are included, and only ones
whose server IP geolocates to **Germany** (CDN edge IPs excluded).

## Files

| File | What it is |
|---|---|
| `germany-vless.txt` | 45 configs, one `vless://` link per line. Copy the whole file, then in your client use **Import from clipboard**. |
| `germany-vless-base64.txt` | The same list base64-encoded (subscription format). |
| `subscriptions.txt` | Live public subscription links that refresh automatically. Use these when the static list dies. |

## Use it as a subscription

Add this URL as a subscription in v2rayNG / v2rayN / Hiddify / Streisand / NekoBox:

```
https://raw.githubusercontent.com/sepehrsheykhzade25/My-Short-stories/ccr-04933d2d-6lc4h7/v2ray-configs/germany-vless-base64.txt
```

(If raw.githubusercontent.com is blocked for you, copy-paste `germany-vless.txt` instead.)

## How to pick a working one

1. Import everything.
2. Run **Test all real delay** (v2rayNG: ⋮ menu → *Test all configurations real delay*; v2rayN: *Test real delay*). This tests through *your* network, which is the only test that matters.
3. Sort by delay, and remove the ones showing `-1` / timeout.
4. Prefer, in this order:
   - **Reality-TCP-Vision** (DE-01 … DE-25): usually the fastest and the hardest to detect.
   - **Reality-GRPC / XHTTP** (DE-26 … DE-35): alternatives if plain TCP Reality gets throttled.
   - **TLS-WS / XHTTP** (DE-36 … DE-45): can work when Reality is blocked on your ISP.
5. Run a speed test (e.g. fast.com) on the best two or three, and keep the fastest.

## Configs

| # | Type | Port | SNI | Hosting provider |
|---|---|---|---|---|
| DE-01 | Reality-TCP-Vision | 443 | ger.raketa-balance.com | FDCservers.net |
| DE-02 | Reality-TCP-Vision | 443 | germ2.serverslocal.ru | Hostes LLC |
| DE-03 | Reality-TCP-Vision | 443 | www.apple.com | IONOS SE |
| DE-04 | Reality-TCP-Vision | 443 | 4.oncloudnineservicestreang.com | netcup GmbH |
| DE-05 | Reality-TCP-Vision | 443 | www.apple.com | VpsQuan L.L.C. |
| DE-06 | Reality-TCP-Vision | 443 | de.sishka.network | Gabriele Sabatino |
| DE-07 | Reality-TCP-Vision | 443 | de.sishka.network | Gabriele Sabatino |
| DE-08 | Reality-TCP-Vision | 443 | de.sishka.network | Gabriele Sabatino |
| DE-09 | Reality-TCP-Vision | 443 | de.sishka.network | Gabriele Sabatino |
| DE-10 | Reality-TCP-Vision | 443 | 0cc0f6a1.vless-reality-sni.staticedge-delivery.net | Hetzner Online GmbH |
| DE-11 | Reality-TCP-Vision | 443 | tickets.betust.net | UAB Cherry Servers |
| DE-12 | Reality-TCP-Vision | 443 | tickets.betust.net | UAB Cherry Servers |
| DE-13 | Reality-TCP-Vision | 443 | sheets.google.com | Hetzner Online AG |
| DE-14 | Reality-TCP-Vision | 443 | www.tencent.com | Hetzner Online GmbH |
| DE-15 | Reality-TCP-Vision | 443 | hh.ru | EdgeSec Technologies Limited |
| DE-16 | Reality-TCP-Vision | 443 | de3.global-cdn.org | Qwins LTD |
| DE-17 | Reality-TCP-Vision | 443 | eh.vk.com | Digital Hosting Provider LLC |
| DE-18 | Reality-TCP-Vision | 443 | gag.fl.iki-servers.com | xorek.cloud International LTD |
| DE-19 | Reality-TCP-Vision | 443 | api-prod.nova.nvidia.com | Tranquila-Host ltd. |
| DE-20 | Reality-TCP-Vision | 443 | www.samsung.com | Hetzner Online GmbH |
| DE-21 | Reality-TCP-Vision | 443 | mx42.hat.onl | PowerRDP Network LTD |
| DE-22 | Reality-TCP-Vision | 443 | cdn-apple.com | Hetzner Online GmbH |
| DE-23 | Reality-TCP-Vision | 443 | delivery.mp.microsoft.com | G-Core Labs S.A. |
| DE-24 | Reality-TCP-Vision | 443 | germanz.ruletka.study | Play2go - Fzco |
| DE-25 | Reality-TCP-Vision | 443 | blog.api.www.cloudflare.com | SERV.HOST GROUP LTD |
| DE-26 | Reality-GRPC | 443 | www.apple.com | Miglovets Egor Andreevich |
| DE-27 | Reality-TCP | 443 | www.cloudflare.com | Google LLC |
| DE-28 | Reality-XHTTP | 443 | thumbs.medic-ml.ru | Eternity International Limited |
| DE-29 | Reality-XHTTP | 443 | deti-online.com | Collin Schneeweiss trading as Unesty Company |
| DE-30 | Reality-TCP | 443 | www.samsungebiz.com | Hetzner Online AG |
| DE-31 | Reality-GRPC | 443 | files.noneok.com | UAB Cherry Servers |
| DE-32 | Reality-XHTTP | 443 | www.google.com | Spacecore Solution LTD |
| DE-33 | Reality-TCP | 443 | play.google.com | Arvancloud Global Technologies L.L.C |
| DE-34 | Reality-GRPC | 443 | tgju.org | Hetzner Online GmbH |
| DE-35 | Reality-TCP | 443 | tgju.org | Hetzner Online GmbH |
| DE-36 | TLS-WS | 443 | x.zahar.top | SERV.HOST GROUP LTD |
| DE-37 | TLS-WS | 443 | cli-q.bosx.net | FDCservers.net |
| DE-38 | TLS-WS | 443 | fcs013.getdcz.me | BitCommand LLC |
| DE-39 | TLS-XHTTP | 443 | deu683.lackerdeu.org | Hostes es |
| DE-40 | TLS-WS | 443 | hk.152568.xyz | Sculk Ltd |
| DE-41 | TLS-WS | 443 | vpn47.cc.cd | DigitalOcean, LLC |
| DE-42 | TLS-WS | 443 | vpn47.cc.cd | Hetzner Online GmbH |
| DE-43 | TLS-WS | 443 | vpn47.cc.cd | netcup GmbH |
| DE-44 | TLS-WS | 443 | vpn47.cc.cd | DigitalOcean, LLC |
| DE-45 | TLS-WS | 443 | vpn47.cc.cd | DigitalOcean, LLC |

## Important caveats

- **Not verified from your location.** These configs were only checked from a
  cloud server, and that check was partial. Whether one works on your ISP (and
  how fast it is) can only be known by testing it on your own device.
- **Free public configs die quickly** (hours to days) and are shared by many
  people, so speed varies. When most of these stop working, use `subscriptions.txt`.
- **Privacy:** these servers are run by unknown third parties who can see your
  traffic metadata (and any unencrypted traffic). Only use HTTPS sites, and
  don't log into banking or other sensitive accounts through them.
- **This repo is public** (and the site may be on GitHub Pages), so anyone can see these.
