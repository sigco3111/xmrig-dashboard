# miner-dashboard

> A Textual-based TUI for monitoring XMRig (Monero CPU miner) in real time.

![status: experimental](https://img.shields.io/badge/status-experimental-yellow)
![python: 3.8+](https://img.shields.io/badge/python-3.8%2B-blue)
![license: MIT](https://img.shields.io/badge/license-MIT-green)

A real-time TUI dashboard for XMRig CPU mining. Reads your existing
`xmrig-config.json` for wallet/worker settings, then shows live hashrate,
system metrics, pool status, and earnings estimates — all in a single
terminal window.

```
+--------------------+--------------------+
|   HASHRATE         |   SYSTEM           |
|   10s: 1189 H/s    |   CPU  89%  72C    |
|   60s: 1173 H/s    |   RAM  15/32 GB    |
|   15m: 1179 H/s    |   Power  ~47W      |
+--------------------+--------------------+
|   POOL             |   MINING STATS     |
|   pool.supportxmr  |   Accepted:  4     |
|   connected        |   Rejected:  0     |
|   Block: 3702952   |   ~$0.04/day       |
+--------------------+--------------------+
|   LAST LOG LINES   |   p pause r resume |
+--------------------+--------------------+
```

## Why this exists

- **Real-time feedback** — see hashrate fluctuate, watch accepted shares tick up
- **No browser tab** — stays in your terminal alongside the miner
- **No telemetry** — reads local log file + public CoinGecko price only
- **Zero config** — discovers wallet/worker from your `xmrig-config.json`

## Quick start

### 1. Install dependencies

```bash
python3 -m pip install --user textual psutil
```

Tested with `textual==6.2.1` and `psutil==7.x`. Python 3.8 or newer required.

### 2. Run

```bash
python3 miner-dashboard.py
```

The dashboard expects:

- XMRig log file at `~/.xmrig/xmrig.log`
- XMRig config at `~/.xmrig/xmrig-config.json`

If your files live elsewhere, point the dashboard at them with environment
variables:

```bash
XMRIG_LOG=/path/to/xmrig.log XMRIG_CONFIG=/path/to/config.json \
  python3 miner-dashboard.py
```

### 3. Optional: standalone launch script

If you want a single-command launcher that bypasses the auto-detected
Python and forces a known interpreter:

```bash
cat > ~/bin/miner-dashboard <<'EOF'
#!/bin/bash
exec /usr/local/bin/python3 /path/to/miner-dashboard.py
EOF
chmod +x ~/bin/miner-dashboard
```

Then just run `miner-dashboard`.

## Controls

| Key | Action                        |
| --- | ----------------------------- |
| `p` | Pause mining (sends SIGSTOP)  |
| `r` | Resume mining (sends SIGCONT) |
| `q` | Quit dashboard                |

The pause/resume keys target the process whose command line matches
`xmrig --config`, so other XMRig instances are not affected.

## What it shows

| Panel | Source                                    | Refresh  |
| ----- | ----------------------------------------- | -------- |
| Hashrate (10s/60s/15m/max) | `xmrig.log` regex parse        | 2 Hz     |
| CPU %, RAM, temperature    | `psutil`                      | 2 Hz     |
| Power estimate             | CPU % heuristic (12W idle)     | 2 Hz     |
| Pool connection, block height | `xmrig.log` regex parse     | 2 Hz     |
| Accepted/rejected shares   | `xmrig.log` regex parse        | 2 Hz     |
| Earnings estimate          | Hashrate x 0.0008 XMR/day/KH/s | 2 Hz     |
| XMR/USD price              | CoinGecko (5-min cache)        | 5 min    |
| Recent log lines           | `xmrig.log` tail (last 50KB)   | 2 Hz     |

## Configuration

The dashboard itself has no config file. All settings come from:

1. **XMRig config** (`$XMRIG_CONFIG` or `~/.xmrig/xmrig-config.json`)
   — `pools[0].user` becomes `WALLET`, `pools[0].pass` becomes `WORKER`.
2. **Environment variables** (all optional):
   - `XMRIG_LOG` — path to XMRig log file
   - `XMRIG_CONFIG` — path to XMRig config JSON

Example `xmrig-config.json` excerpt that the dashboard reads:

```json
{
  "pools": [
    {
      "url": "pool.supportxmr.com:5555",
      "user": "4YourMoneroWalletAddressHere95Chars",
      "pass": "your-worker-name",
      "keepalive": true,
      "tls": false
    }
  ]
}
```

## Platform notes

- **macOS** — works out of the box; temperature reading depends on the
  system reporting it via `psutil.sensors_temperatures()` (Apple Silicon
  Mac minis usually do not).
- **Linux** — works; temperature depends on `psutil` and `lm-sensors`.
- **Windows** — should work but is untested; XMRig path differs.

## Privacy

This dashboard does not send your wallet address, worker name, or any
other personal data anywhere. The only outbound network call is to
`api.coingecko.com` for the XMR/USD price (5-minute cache).

Your wallet/worker are read from `xmrig-config.json` at runtime, never
hardcoded.

## Limitations

- **Earnings estimate is rough.** The 0.0008 XMR/day per KH/s figure is a
  rough average based on current network conditions. Real payouts depend
  on pool luck, network difficulty, and fees.
- **CPU temperature on Apple Silicon is usually unavailable.** `psutil`
  on M-series Macs generally returns no temperature sensors; the panel
  will show `n/a`.
- **Pause/resume uses `pkill`.** It matches against `xmrig --config`,
  so other XMRig instances started with different command lines are not
  affected. If you run multiple miners, double-check with `pgrep -fl
  xmrig` first.

## Troubleshooting

**Dashboard shows `IDLE` even though XMRig is running.**

The log parser hasn't seen a `new job from <pool>` line yet. Wait a few
seconds; the dashboard refreshes twice per second.

**`WARNING: XMRig log not found` on startup.**

Set `XMRIG_LOG` to the actual path, e.g.:

```bash
export XMRIG_LOG="$HOME/xmrig.log"
export XMRIG_CONFIG="$HOME/xmrig-config.json"
```

**Garbled Unicode characters in panels.**

Your terminal may not support the box-drawing characters used for the
progress bars. Try iTerm2 (macOS), Alacritty, or Ghostty — all handle
them correctly.

**Key bindings don't work.**

Make sure the dashboard window has focus (click into it). Textual keys
are intercepted by the focused widget, not the OS terminal.

## License

MIT. See `LICENSE` for the full text.

---

# miner-dashboard (한국어)

> XMRig(Monero CPU 채굴기)를 실시간으로 모니터링하는 Textual 기반 TUI.

XMRig CPU 채굴을 위한 실시간 TUI 대시보드입니다. 기존 `xmrig-config.json`에서
지갑/워커 설정을 읽어와서, 라이브 hashrate, 시스템 메트릭, 풀 상태, 채굴량
추정을 단일 터미널 창에 보여줍니다.

## 왜 만들었나

- **실시간 피드백** — hashrate 변동, accepted shares 증가를 즉시 확인
- **브라우저 탭 불필요** — 채굴기와 같은 터미널에 머무름
- **텔레메트리 없음** — 로컬 로그 파일 + 공개 CoinGecko 가격만 사용
- **설정 제로** — `xmrig-config.json`에서 지갑/워커 자동 발견

## 빠른 시작

### 1. 의존성 설치

```bash
python3 -m pip install --user textual psutil
```

`textual==6.2.1`, `psutil==7.x` 기준 검증. Python 3.8 이상 필요.

### 2. 실행

```bash
python3 miner-dashboard.py
```

대시보드 기본 경로:
- XMRig 로그: `~/.xmrig/xmrig.log`
- XMRig 설정: `~/.xmrig/xmrig-config.json`

다른 경로에 있다면 환경변수로:

```bash
XMRIG_LOG=/path/to/xmrig.log XMRIG_CONFIG=/path/to/config.json \
  python3 miner-dashboard.py
```

## 조작

| 키 | 동작 |
| --- | --- |
| `p` | 채굴 일시정지 (SIGSTOP) |
| `r` | 채굴 재개 (SIGCONT) |
| `q` | 대시보드 종료 |

## 표시 항목

| 패널 | 소스 | 갱신 주기 |
| --- | --- | --- |
| Hashrate (10s/60s/15m/max) | `xmrig.log` regex 파싱 | 2 Hz |
| CPU %, RAM, 온도 | `psutil` | 2 Hz |
| 전력 추정 | CPU % 휴리스틱 (12W idle) | 2 Hz |
| 풀 연결, 블록 높이 | `xmrig.log` regex 파싱 | 2 Hz |
| 수락/거부 share | `xmrig.log` regex 파싱 | 2 Hz |
| 채굴량 추정 | Hashrate x 0.0008 XMR/day/KH/s | 2 Hz |
| XMR/USD 가격 | CoinGecko (5분 캐시) | 5분 |
| 최근 로그 라인 | `xmrig.log` tail (마지막 50KB) | 2 Hz |

## 설정

대시보드 자체의 설정 파일은 없습니다. 모든 설정은 다음에서 옴:

1. **XMRig 설정** (`$XMRIG_CONFIG` 또는 `~/.xmrig/xmrig-config.json`)
   — `pools[0].user`는 `WALLET`, `pools[0].pass`는 `WORKER`가 됨.
2. **환경변수** (모두 선택):
   - `XMRIG_LOG` — XMRig 로그 파일 경로
   - `XMRIG_CONFIG` — XMRig 설정 JSON 경로

## 프라이버시

이 대시보드는 지갑 주소, 워커명, 기타 개인 데이터를 어디에도 전송하지
않습니다. 외부로 나가는 네트워크 호출은 오직 XMR/USD 가격을 위한
`api.coingecko.com` (5분 캐시)뿐.

지갑/워커는 런타임에 `xmrig-config.json`에서 읽지, 코드에 하드코딩되지
않습니다.

## 제한사항

- **채굴량 추정은 대략적.** 0.0008 XMR/day per KH/s 수치는 현재 네트워크
  상태 기반의 평균 추정. 실제 지급액은 풀 운, 네트워크 난이도, 수수료에
  따라 다름.
- **Apple Silicon CPU 온도는 보통 사용 불가.** M시리즈 Mac에서 `psutil`은
  일반적으로 온도 센서를 반환하지 않음; 패널이 `n/a`로 표시.
- **일시정지/재개는 `pkill` 사용.** `xmrig --config`로 매칭하므로, 다른
  명령줄로 시작된 XMRig 인스턴스는 영향받지 않음. 여러 채굴기를 돌리면
  먼저 `pgrep -fl xmrig`로 확인할 것.

## 라이선스

MIT. 전문은 `LICENSE` 참조.
