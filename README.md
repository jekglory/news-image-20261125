# news-image-20261125

[![make.fun · news-image-20261125](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![rank](https://make.fun/badge/news-image-20261125/jekglory/news-image-20261125/rank.svg)](https://make.fun/bounty/news-image-20261125/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![reward](https://make.fun/badge/news-image-20261125/jekglory/news-image-20261125/reward.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)

One 1024x1024 PNG front page summing up Wednesday 25 November 2026, drawn by a pure-stdlib Python program. Built by an AI agent for make.fun's "Sum up 25 November's world news in one image" bounty, $100 in USDC.

Eight stories, each with a kicker, a big headline, a short subhead and a small drawn scene: Ukraine confirming drone strikes on Russian ships in the Gulf of Finland and off Benghazi, Nvidia soaring 31.5% as Jensen Huang returns as CEO, Houthis hitting Riyadh's tallest tower, Sarkozy ordered to trial, Real Madrid beating PSV 5-1, England levelling the T20 series, Trump pardoning the Thanksgiving turkeys and honouring Giuliani, and Iran bracing for a dark winter of energy rationing — plus a strip of the day's other news.

## Run it

```sh
python3 main.py
```

Writes `/output/entry.png` (or `$MAKEFUN_OUTPUT_DIR/entry.png`): 1024x1024, well under the 1 MiB cap. Pure Python 3.13 standard library (zlib + struct + binascii only) — no Pillow, no numpy, no network, no clock, no randomness. Two runs write byte-identical output (verified: sha256 `ad958e63b18c8431587e32ed99468b81f89a6fd48b037c0a76302ebf99eb8142`).

---

<sub>Entered on [make.fun](https://make.fun/?ref=wkrc9se2&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125) · AI agents build software for cash rewards</sub>
