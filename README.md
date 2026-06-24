# xmrig-dashboard

> A real-time TUI dashboard for XMRig (Monero CPU miner). Live
> hashrate, system metrics, pool status, and earnings — all in
> your terminal.

[![status: experimental](https://img.shields.io/badge/status-experimental-yellow)](#)
[![python: 3.8+](https://img.shields.io/badge/python-3.8%2B-blue)](#)
[![license: MIT](https://img.shields.io/badge/license-MIT-green)](#)
[![made with: textual](https://img.shields.io/badge/made%20with-textual-cyan)](#)

```
   +----------------------+----------------------+
   |   HASHRATE           |   SYSTEM             |
   |   10s:  1,189 H/s    |   CPU  89%  72C      |
   |   60s:  1,173 H/s    |   RAM  15/32 GB      |
   |   15m:  1,180 H/s    |   Power  ~47W        |
   +----------------------+----------------------+
   |   POOL               |   MINING STATS       |
   |   supportxmr.com     |   Accepted:  142     |
   |   connected          |   Rejected:    0     |
   |   Block: 3,702,952   |   ~$0.04/day         |
   +----------------------+----------------------+
   |   LOG LINES          |   p pause r resume   |
   +----------------------+----------------------+
```

---

## Why

- **Real-time feedback** — see your hashrate react instantly
- **No browser tab** — stays in the terminal alongside the miner
- **No telemetry** — reads local log + public CoinGecko price only
- **Zero config** — wallet/worker pulled from your `xmrig-config.json`

---

## Quick start (60 seconds)

```bash
# 1. Install dependencies
python3 -m pip install --user textual psutil

# 2. Install XMRig (if you don't have it)
brew install xmrig                                  # macOS
# OR: see https://xmrig.com/download for other platforms

# 3. Make sure your xmrig config exists at the default path
mkdir -p ~/.xmrig
ls ~/.xmrig/xmrig-config.json                      # should exist

# 4. Start XMRig (in one terminal)
xmrig --config=~/.xmrig/xmrig-config.json

# 5. Start the dashboard (in another terminal)
git clone https://github.com/sigco3111/xmrig-dashboard
cd xmrig-dashboard
python3 miner-dashboard.py
```

> Need help with XMRig setup, getting a wallet address, or
> choosing a pool? Start with [docs/getting-started.md](docs/getting-started.md).

---

## What it does

| Panel          | Source                          | Update   |
| -------------- | ------------------------------- | -------- |
| **Hashrate** (10s/60s/15m/max) | `xmrig.log` regex | 2 Hz |
| **System** (CPU/RAM/temp/power) | `psutil`          | 2 Hz |
| **Pool** (URL, status, block)   | `xmrig.log` regex | 2 Hz |
| **Stats** (accepted/rejected)   | `xmrig.log` regex | 2 Hz |
| **Earnings** (daily/monthly/yearly) | hash × XMR price | 2 Hz |
| **XMR price**                   | CoinGecko (cached 5 min) | 5 min |
| **Log lines** (last 8)          | `xmrig.log` tail  | 2 Hz |

Full panel reference: [docs/dashboard.md](docs/dashboard.md).

---

## Controls

```
  p   pause mining  (sends SIGSTOP to XMRig)
  r   resume mining (sends SIGCONT)
  q   quit dashboard  (XMRig keeps running)
```

---

## Configuration

The dashboard has no config file. It reads from:

| Source                                | What it provides              |
| ------------------------------------- | ----------------------------- |
| `~/.xmrig/xmrig-config.json`          | wallet address, worker name   |
| `~/.xmrig/xmrig.log`                  | live metrics                  |
| `$XMRIG_CONFIG` env var               | override config path          |
| `$XMRIG_LOG` env var                  | override log path             |

The config file is the same one XMRig uses. The dashboard reads
`pools[0].user` and `pools[0].pass` from it. See
[docs/getting-started.md](docs/getting-started.md) for the
expected format.

---

## Documentation

| Doc                                       | What's in it                              |
| ----------------------------------------- | ----------------------------------------- |
| [docs/getting-started.md](docs/getting-started.md) | Wallet setup, XMRig config, first run |
| [docs/dashboard.md](docs/dashboard.md)             | Panel-by-panel reference             |
| [docs/exchanges.md](docs/exchanges.md)             | Choosing an exchange, getting a real XMR address, avoiding scam tokens |
| [docs/supportxmr.md](docs/supportxmr.md)           | Using SupportXMR (and pool choice)  |
| [docs/security.md](docs/security.md)               | Threat model, best practices         |

---

## Privacy

This dashboard does not transmit your wallet address, worker
name, or any other personal data. The only outbound network call
is `GET https://api.coingecko.com/api/v3/simple/price?ids=monero`
(5-minute cache) for the XMR/USD price.

Wallet and worker are read from `xmrig-config.json` at runtime;
nothing is hardcoded. See [docs/security.md](docs/security.md).

---

## Limitations

- **Earnings are estimates.** The dashboard's formula assumes
  current network hashrate and XMR price stay constant. They
  won't. Use the dashboard's number as a sanity check, not a
  prediction.
- **CPU temperature is often `n/a`.** `psutil` on Apple Silicon
  Mac minis usually returns no temperature sensors.
- **No config UI.** Edit the XMRig config and restart XMRig to
  change wallet/worker/pool. The TUI is read-only by design.
- **Pause targets `xmrig --config`.** Other XMRig instances
  started with different command lines are not affected.

---

## Contributing

Issues and PRs welcome. For non-trivial changes, please open an
issue first to discuss the design.

Code style: Python 3.8+ compatible (no walrus, no match
statements). Black formatting preferred but not enforced.
Type hints encouraged.

---

## License

MIT. See [LICENSE](LICENSE) for the full text.

---

# xmrig-dashboard (한국어)

> XMRig(Monero CPU 채굴기)용 실시간 TUI 대시보드. 라이브
> hashrate, 시스템 메트릭, 풀 상태, 채굴량을 터미널에서.

## 왜 만들었나

- **실시간 피드백** — hashrate 변화를 즉시 확인
- **브라우저 탭 불필요** — 채굴기와 같은 터미널에 머무름
- **텔레메트리 없음** — 로컬 로그 + 공개 CoinGecko 가격만 사용
- **설정 제로** — `xmrig-config.json`에서 지갑/워커 자동 추출

## 빠른 시작 (60초)

```bash
# 1. 의존성 설치
python3 -m pip install --user textual psutil

# 2. XMRig 설치 (없는 경우)
brew install xmrig                                  # macOS
# 다른 플랫폼: https://xmrig.com/download

# 3. xmrig 설정 파일이 표준 경로에 있는지 확인
mkdir -p ~/.xmrig
ls ~/.xmrig/xmrig-config.json

# 4. XMRig 시작 (터미널 1)
xmrig --config=~/.xmrig/xmrig-config.json

# 5. 대시보드 시작 (터미널 2)
git clone https://github.com/sigco3111/xmrig-dashboard
cd xmrig-dashboard
python3 miner-dashboard.py
```

> 지갑 받기, XMRig 설정, 풀 선택은
> [docs/getting-started.md](docs/getting-started.md) (한국어 번역은 곧) 참조.

## 표시 항목

| 패널 | 소스 | 갱신 주기 |
| --- | --- | --- |
| Hashrate (10s/60s/15m/max) | `xmrig.log` 파싱 | 2 Hz |
| System (CPU/RAM/온도/전력) | `psutil` | 2 Hz |
| Pool (URL, 상태, 블록) | `xmrig.log` 파싱 | 2 Hz |
| Stats (수락/거부) | `xmrig.log` 파싱 | 2 Hz |
| Earnings (일/월/연) | 해시레이트 × XMR 가격 | 2 Hz |
| XMR 가격 | CoinGecko (5분 캐시) | 5분 |
| 로그 라인 (최근 8개) | `xmrig.log` tail | 2 Hz |

## 조작

```
  p   채굴 일시정지  (XMRig에 SIGSTOP)
  r   채굴 재개     (XMRig에 SIGCONT)
  q   대시보드 종료 (XMRig는 계속 실행)
```

## 설정

대시보드 자체 설정 파일 없음. 다음에서 읽음:

| 소스 | 내용 |
| --- | --- |
| `~/.xmrig/xmrig-config.json` | 지갑 주소, 워커명 |
| `~/.xmrig/xmrig.log` | 라이브 메트릭 |
| `$XMRIG_CONFIG` 환경변수 | 설정 경로 override |
| `$XMRIG_LOG` 환경변수 | 로그 경로 override |

## 문서

| 문서 | 내용 |
| --- | --- |
| [docs/getting-started.ko.md](docs/getting-started.ko.md) | 지갑/설정/첫 실행 (한국어) |
| [docs/getting-started.md](docs/getting-started.md) | 같은 내용 (영어) |
| [docs/dashboard.ko.md](docs/dashboard.ko.md) | 패널별 상세 (한국어) |
| [docs/dashboard.md](docs/dashboard.md) | 같은 내용 (영어) |
| [docs/exchanges.ko.md](docs/exchanges.ko.md) | 거래소 선택, XMR 주소, 스캠 구분 (한국어) |
| [docs/exchanges.md](docs/exchanges.md) | 같은 내용 (영어) |
| [docs/supportxmr.ko.md](docs/supportxmr.ko.md) | SupportXMR 사용법 (한국어) |
| [docs/supportxmr.md](docs/supportxmr.md) | 같은 내용 (영어) |
| [docs/security.ko.md](docs/security.ko.md) | 보안 모범 사례 (한국어) |
| [docs/security.md](docs/security.md) | 같은 내용 (영어) |

> 모든 문서는 한/영 모두 제공됩니다. 한국어가 더 편하시면 `.ko.md` 버전을,
> 영어가 편하시면 원본을 사용하세요. 두 버전의 내용은 동일합니다.

## 프라이버시

이 대시보드는 지갑 주소, 워커명, 개인 데이터를 어디에도 전송하지
않습니다. 외부 네트워크 호출은 오직 XMR/USD 가격을 위한
`GET https://api.coingecko.com/api/v3/simple/price?ids=monero`
(5분 캐시)뿐.

## 라이선스

MIT. 전문은 [LICENSE](LICENSE) 참조.
