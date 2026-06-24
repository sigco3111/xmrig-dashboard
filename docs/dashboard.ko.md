# 대시보드 사용법

> `miner-dashboard.py`의 모든 패널, 키, 설정 옵션에 대한 참조.

대시보드는 **NMMiner 스타일 사이버펑크 그린** 색상 테마를 사용해요:
진한 터미널 그린 배경(`#001100`)에 밝은 그린 텍스트(`#33ff66`)와
액센트 하이라이트(`#00ff9c`). 모든 패널이 같은 시각 언어를 공유.

---

## 한눈에 보는 화면

대시보드는 2열 × 3행 그리드:

```
  +-----------------+-----------------+
  |   HASHRATE      |   SYSTEM        |
  |                 |                 |
  +-----------------+-----------------+
  |   POOL          |   MINING STATS  |
  |                 |                 |
  +-----------------+-----------------+
  |   LOG LINES     |   (hint bar)    |
  |                 |                 |
  +-----------------+-----------------+
```

상단에 상태 바:

```
  >>> MINING <<<  |  heejeong_kucoin_macmini  |  CPU 100.0%  |  1,096 H/s  |  shares 76 ok / 0 bad  |  mode FULL  |  10:42:18
```

상태 바의 각 구간은 다른 색상으로 표시돼요:
- **`>>> MINING <<<`** 연결 중일 땐 밝은 액센트 그린, 유휴 시엔 앰버
- **CPU/Hash/Shares** 숫자는 거의 흰색(`#ccffdd`)으로 가독성 ↑
- **거부된 share** 0보다 크면 빨강, 0이면 어두움
- **`mode FULL`** / **`mode COMPACT`** 현재 밀도 표시

---

## 패널 참조

### HASHRATE (좌상단)

```
  HASHRATE

   10s:  1,189.3 H/s   ##########░░░░░  79%
   60s:  1,173.6 H/s   ##########░░░░░  78%
   15m:  1,180.0 H/s   ##########░░░░░  78%
   max:  1,320.9 H/s

  trend ▂▃▅▆▇▆▅▆▇█▇▆▅▆▇█▆▆▇▆▅▆▇▆▆▇█  (60s)
```

| 필드    | 소스                                            | 의미                                                  |
| ------- | ----------------------------------------------- | ----------------------------------------------------- |
| `10s`   | XMRig 10초 슬라이딩 윈도우                       | 즉각 hashrate; 가장 많이 변동                          |
| `60s`   | XMRig 60초 슬라이딩 윈도우                       | 더 매끄러움; "내가 실제로 받는" 수치                   |
| `15m`   | XMRig 15분 슬라이딩 윈도우                      | 시간/일 평균; 지속적 성능 반영                        |
| `max`   | 채굴기 시작 후 최고 hashrate                     | sanity check; 현재 ≈ max면 시스템이 행복               |
| `trend` | 최근 60개 `10s` hashrate 샘플 (2Hz에서 30초)   | 스파크라인; 변동, 피크, 디프를 시각화                  |

진행 바는 `max(10s, 60s, 1500)`와 비교하므로, 완벽하게 돌아가는 채굴기는
바의 대부분이 채워져요.

**스파크라인**은 유니코드 블록 문자 `▁▂▃▄▅▆▇█` (낮음→높음)를
사용해서 샘플당 한 글자씩 표시해요. 세로 크기는 윈도우의
min/max에 맞춰 자동 스케일되므로, 절대 수치 변화가 적어도
급격한 hashrate 변동을 한눈에 볼 수 있어요.

HASHRATE border는 **펄스** 효과 (액센트 그린과 거의 흰색 사이를
번갈아 표시)를 줘서 채굴기가 풀에 연결 중임을 알 수 있어요. 이
펄스는 2Hz refresh 사이클로 구동되며, CSS animation이 아닌
클래스 토글 방식 (Textual 6.x가 `animation` CSS 속성 미지원)
이에요.

### SYSTEM (우상단)

```
  SYSTEM

  CPU    6C/6T  ~89% load
         ##########░░░░░  89.5%  72C

  RAM    15.1/32.0 GB
         ##########░░░░░  47.2%

  POWER  ~47W (estimated)
  UPTIME 2h 18m
```

| 필드           | 소스                | 비고                                  |
| -------------- | ------------------- | ------------------------------------- |
| CPU 코어/쓰레드 | `psutil.cpu_count`  | 자동 감지                              |
| CPU 부하       | `psutil.cpu_percent` | 모든 코어 0-100%                     |
| CPU 온도       | `psutil.sensors_temperatures` | 색상 코딩: 70°C 미만 그린, 70-85°C 앰버, 85°C 이상 빨강. Apple Silicon에서는 자주 `n/a` |
| RAM 사용/전체  | `psutil.virtual_memory` | 채굴기뿐 아니라 모든 것 포함      |
| 전력 추정      | 휴리스틱            | 12W idle + 35W 채굴 시 (대략)         |
| 업타임         | `psutil.boot_time`  | 마지막 시스템 재부팅 기준 (채굴기 시작 X) |

> **전력 추정 면책:** 이건 대략적인 추정이에요. 실제 전력 소모는
> 특정 CPU, XMRig 쓰레드 설정, 다른 앱 실행 여부에 따라 다릅니다.
> 정확한 측정은 플러그형 전력 측정기를 사용하세요.

### POOL (좌중간)

```
  POOL

  pool.supportxmr.com:5555
  [+] connected

  Block:  3,702,952
  Threads: 5/5 ready
```

| 필드      | 소스 (XMRig 로그 라인)                          |
| --------- | ---------------------------------------------- |
| 풀 URL    | `new job from <url> ...`                       |
| 상태      | `new job` 라인 발견 시 `connected`, 아니면 `disconnected` |
| 블록      | 최신 job 라인의 `height <N>`                   |
| 쓰레드    | 시작 라인의 `READY threads X/Y`                |

> 패널이 `disconnected`인데 XMRig이 분명히 돌아간다면,
> LOG LINES 패널에서 최근 에러를 확인하세요.

### MINING STATS (우중간)

```
  MINING STATS

  Accepted:     142
  Rejected:       0
  Last share: [2026-06-24 09:18:0

  EARNINGS ESTIMATE (XMR: $318.00)
  Daily:      0.000116 XMR  ($0.0368)
  Monthly:    0.003480 XMR  ($1.11)
  Yearly:     0.042340 XMR  ($13.46)

  Power cost: ~$1.50/mo - net: -$0.30/mo
```

| 필드             | 소스                                |
| ---------------- | ----------------------------------- |
| Accepted/Rejected| `accepted (A/R)` 로그 라인 (누적)   |
| Last share       | 가장 최근 `accepted` 라인의 타임스탬프 |
| XMR 가격         | CoinGecko API (5분 캐시)            |
| 일/월/연         | Hashrate × 0.0008 XMR/day/KH/s     |

> **수익 공식은 의도적으로 단순합니다.** 현재 네트워크 hashrate와
> XMR 가격이 일정하다고 가정해요. 둘 다 변할 거예요. 이 숫자는
> "모든 게 그대로라면" 참조용이지 예측이 아니에요.

### LOG LINES (좌하단)

```
  LAST LOG LINES

  (miner  speed 10s/60s/15m 1189.3 1173.6 1180.0 H/s max 1320.9 H/s
  (net    new job from pool.supportxmr.com:5555 diff 150000 algo rx
  (cpu    accepted (142/0) diff 75000 (267 ms)
  (cpu    READY threads 5/5 (5) huge pages 0% 0/5 memory 10240 KB
  (net    new job from pool.supportxmr.com:5555 diff 150000 algo rx
```

| 비고 | 의미 |
| ---- | ---- |
| `(...)` not `[...]` | 로그 라인의 대괄호는 Rich 마크업 충돌을 피하기 위해 괄호로 변환됨 |
| 90자 잘림 | 긴 라인은 오른쪽이 잘림; 가장 최근 정보가 오른쪽 |
| 최근이 아래에 | 위는 오래된 것, 아래는 최근 (deque tail 동작) |

---

## 상태 바

```
  [*] MINING  |  Worker: mac-mini  |  CPU: 89.5%  |  Hash: 1,189 H/s  |  Shares: 142 ok / 0 bad  |  09:18:42
```

이건 한 줄 요약이에요. 방 건너에서도 볼 수 있도록 설계:

```
  녹색 바   =  채굴 중
  노란 바   =  일시정지 (XMRig에 SIGSTOP 보냄)
  빨간 바   =  XMRig 실행 안 됨 또는 연결 안 됨
```

---

## 키 바인딩

| 키 | 동작             | 하는 일                                                 |
| -- | ---------------- | ------------------------------------------------------- |
| `p` | **일시정지** 채굴 | XMRig에 `SIGSTOP` 전송. 프로세스는 살아있지만 해시 중단. CPU 0%로 떨어짐. |
| `r` | **재개** 채굴    | XMRig에 `SIGCONT` 전송. 해시 재개.                      |
| `c` | **컴팩트** 모드  | FULL ↔ COMPACT 밀도 토글. 진행 바 제거, 로그 줄 8 → 3, 수익 예측 한 줄로 축소. |
| `s` | **저장** 스냅샷  | 현재 상태를 `~/.xmrig/snapshots/snapshot-YYYYMMDD-HHMMSS.json`에 저장. |
| `?` | **도움말**      | 모든 키 바인딩을 보여주는 modal. `Esc` 또는 `q`로 닫기.  |
| `q` | **종료** 대시보드 | TUI 닫기. XMRig은 백그라운드에서 계속 채굴.            |

> **SIGSTOP vs SIGTERM:** 일시정지 키는 `SIGSTOP`을 사용해요.
> 가역적이에요. 채굴기 프로세스는 살아있지만 작업 안 함, CPU 0% 사용.
> 재개하려면 `r`. 실제로 채굴기를 죽이려면 대시보드 밖에서
> `pkill xmrig` 사용.

### 컴팩트 모드

`c`를 누르면 두 가지 밀도 사이를 토글해요:

| 모드      | 변경 사항                                              |
| --------- | ----------------------------------------------------- |
| FULL      | 모든 진행 바, 모든 로그 줄, 전체 일/월/연 예측 (기본값) |
| COMPACT   | CPU/RAM 진행 바 제거, 로그 줄 8 → 3, 일/월/연 예측 한 줄로, 시스템 부하 평균 제거. 작은 터미널 창이나 화면당 더 많은 정보를 보고 싶을 때 유용. |

현재 모드는 상태 바에 표시돼요 (`mode FULL` 또는 `mode COMPACT`).
`c`를 다시 누르면 돌아가요.

### 스냅샷

`s`를 누르면 현재 XMRig 상태, 시스템 메트릭, hashrate 스파크라인
히스토리를 JSON 파일로 저장해요. 파일은 `~/.xmrig/snapshots/`에
타임스탬프 이름으로 저장돼요.

```json
{
  "timestamp": "20260624-104218",
  "xmrig": {"hashrate_10s": 1096.0, "accepted": 76, ...},
  "system": {"cpu_pct": 100.0, "mem_pct": 47.5, ...},
  "earnings": {"xmr_price": 318.0},
  "hr_history": [1180.0, 1175.3, ...]
}
```

여러 실행 비교, 회귀 디버깅, "그 당시 시스템 상태" 기록에 유용.

### 키가 없는 것

- TUI에서 지갑/워커 변경 불가 (config 파일 편집 후 XMRig 재시작)
- 풀 전환 불가 (위와 동일)
- 로그 히스토리 스크롤 불가 (마지막 3~8줄만 유지)
- XMRig CPU 쓰레드 수 변경 불가

이건 의도적이에요 — TUI는 read-only로 설계되어, 대시보드에서
실수로 채굴 설정을 바꿀 수 없어요.

---

## 설정

대시보드는 **자체 설정 파일이 없어요**. 모든 설정은 다음에서 옴:

### 1. XMRig 설정 파일 (지갑/워커용)

| 변수 (코드) | 소스                                  |
| ----------- | ------------------------------------- |
| `WALLET`    | `xmrig-config.json`(또는 `$XMRIG_CONFIG`)의 `pools[0].user` |
| `WORKER`    | 같은 파일의 `pools[0].pass`           |

설정 파일이 없으면 대시보드는 placeholder 텍스트를 사용하고 시작 시 경고:

```
  WARNING: XMRig config not found at /Users/you/.xmrig/xmrig-config.json
    Tried: ['/Users/you/.xmrig/xmrig-config.json', '/Users/you/xmrig-config.json']
    Set XMRIG_CONFIG env var to the correct path,
    or symlink your config into one of the above locations.
```

### 2. 환경변수 (경로용)

| 변수          | 기본값 (fallback 포함)                                 |
| ------------- | ------------------------------------------------------ |
| `XMRIG_LOG`   | env var → `~/.xmrig/xmrig.log` → `~/xmrig.log` → `/tmp/xmrig.log` |
| `XMRIG_CONFIG`| env var → `~/.xmrig/xmrig-config.json` → `~/xmrig-config.json`     |

**경로 해결 순서** (존재하는 첫 번째 항목 사용):

```
  1. XMRIG_LOG / XMRIG_CONFIG 환경변수 값 (설정된 경우)
  2. ~/.xmrig/xmrig.log (또는 xmrig-config.json)   ← 권장
  3. ~/xmrig.log       (또는 xmrig-config.json)    ← 흔한 기본값
  4. /tmp/xmrig.log                             ← 최후의 fallback
```

어떤 후보도 존재하지 않으면 대시보드는 여전히 시작해요 (크래시 안 함),
하지만 로그 파일이 나타날 때까지 XMRig 관련 패널은 비어있어요.
`XMRIG_LOG`를 명시적으로 설정해서 올바른 위치를 가리키세요.

해결된 경로는 시작 시 출력돼요:

```
  XMRig log:        /Users/you/xmrig.log  [OK]
  XMRig config:     /Users/you/xmrig-config.json  [OK]
```

`[OK]` / `[NOT FOUND]` 표시가 대시보드가 올바른 파일에 연결됐는지
즉시 알려줘요.

### 3. 명령행 (없음)

대시보드는 인자를 받지 않아요. 환경변수나 XMRig 설정을 편집해서
동작을 바꾸세요.

---

## 갱신 주기

대시보드는 XMRig 로그 파일을 **초당 2회** (2 Hz) 폴링해요. 실시간으로
느껴질 만큼 빠르지만 무시할 수 있는 CPU를 사용할 만큼 느려요.

주기를 바꾸려면 `miner-dashboard.py` 상단의 `REFRESH_HZ`를 편집:

```python
REFRESH_HZ = 2  # 2 = 초당 2회; 1 = 초당 1회; 5 = 초당 5회
```

높을수록 부드럽지만 로그 파일에 더 많은 I/O. 낮을수록 끊기지만
CPU 적게 사용. 2 Hz가 합리적 기본값이에요.

---

## 커스터마이징

### 색상 스킴

모든 색상은 `miner-dashboard.py` 상단의 `PALETTE` dict에 정의돼 있어요.
한 곳에서 조정하면 모든 패널이 업데이트돼요.

```python
PALETTE = {
    "bg":          "#001100",  # 진한 터미널 그린-블랙
    "bg_dark":     "#000800",  # 상태 바 배경
    "fg":          "#33ff66",  # 기본 텍스트
    "fg_dim":      "#1f8033",  # 어두운 텍스트
    "fg_faint":    "#0e4019",  # 매우 어두움
    "accent":      "#00ff9c",  # 밝은 액센트
    "warning":     "#ffaa00",  # 앰버
    "error":       "#ff3355",  # 빨강
    "highlight":   "#ccffdd",  # 거의 흰색
}
```

팔레트는 CSS(패널 border)와 Rich markup(텍스트 색상) **양쪽**에
사용돼요. 시각 계층:

- **밝은 그린** (`accent`) — 활성/채굴 중, ">>> MINING <<<"
- **표준 그린** (`fg`) — 기본 텍스트, 숫자
- **거의 흰색** (`highlight`) — 현재 값, 스파크라인
- **어두운 그린** (`fg_dim`) — 라벨, 구분자 파이프
- **매우 어두움** (`fg_faint`) — 축 라벨, 배경 힌트
- **앰버** (`warning`) — 유휴 상태, 중간 온도, 1-5% 거부율
- **빨강** (`error`) — 고온, 5% 초과 거부율, 에러

### 패널 border 색상

패널 border는 계층적 스킴을 사용해서 각 패널의 역할을 한눈에
볼 수 있어요:

| 패널         | border 색상     | 이유                                  |
| ------------ | --------------- | ------------------------------------- |
| HASHRATE     | 밝은 액센트     | 가장 중요; 채굴 중 펄스               |
| SYSTEM       | 표준           | 안정적인 참조                         |
| POOL         | 어두움         | 연결 시 조용함                        |
| MINING STATS | 표준           | 안정적인 참조                         |
| LOG LINES    | 매우 어두움     | 배경 컨텍스트                         |

### 스파크라인 길이

HASHRATE 스파크라인은 최근 60개 샘플(2Hz에서 30초)을 유지해요.
`miner-dashboard.py` 상단의 `SPARKLINE_SAMPLES` 변경:

```python
SPARKLINE_SAMPLES = 60  # 2Hz에서 30초; 120 = 1분; 30 = 15초
```

큰 값 = 더 매끄러운 곡선, 더 느린 시각 반응. 작은 값 = 더 반응적이지만
노이즈 많음.

### 패널 레이아웃

그리드도 `CSS`에 있어요:

```python
#main {
    layout: grid;
    grid-size: 2 3;     # 2열, 3행
    grid-gutter: 1;     # 셀 간격
    padding: 1;
}
```

`grid-size: 1 6` (1열) 또는 `grid-size: 3 2` (3열 × 2행)로 변경 가능.

### 수익 공식

추정치는 고정 `0.0008 XMR/day per KH/s` 상수를 사용:

```python
xmr_per_day = hr_avg / 1000 * 0.0008
```

이건 합리적인 평균이에요. 더 정확한 추정을 원한다면 채굴 계산기 API를
쿼리하고 결과를 캐시할 수 있어요. 하지만 단순 공식은 "이거 켜둘 만한가?"
sanity check로는 충분해요.

---

## 문제 해결

### 시작 시 "XMRig config not found"

다음 중 하나:
- `~/.xmrig/xmrig-config.json` 생성, 또는
- `XMRIG_CONFIG=/path/to/your/config.json` 설정 후 실행.

### 시작 시 "XMRig log not found"

시작 출력에서 `XMRig log:` 옆에 `[NOT FOUND]`가 보이면, 대시보드는
시작했지만 XMRig 로그 파일을 찾을 수 없어요. HASHRATE, POOL, MINING
STATS, LAST LOG LINES 패널은 비어있게 됩니다.

**해결 방법** 중 하나:

1. **XMRig이 아직 안 돌고 있으면 먼저 시작** — XMRig이 로그 파일에
   쓰기 시작하면 파일이 나타나요.
2. **`XMRIG_LOG`를 명시적으로 설정**:
   ```bash
   export XMRIG_LOG=/path/to/your/xmrig.log
   ~/bin/run-miner-dashboard.sh
   ```
3. **심볼릭 링크**로 표준 위치 중 하나에 연결:
   ```bash
   mkdir -p ~/.xmrig
   ln -sf /path/to/your/xmrig.log ~/.xmrig/xmrig.log
   ```
4. 로그를 옮긴 후 **대시보드 재시작**해서 경로 해결을 다시 실행.

시작 출력에 시도한 모든 후보 경로가 나열돼요 — 그걸 보고 어떤 경로가
우리 환경에 맞는지 확인하세요.

### XMRig이 도는데 대시보드가 `IDLE` 표시

가능한 원인:
1. XMRig이 일시정지됨 (`p` 키 또는 수동으로 SIGSTOP). `r`로 재개.
2. 로그 파일이 비어있음 — XMRig이 다른 경로에 로깅 중. 시작 출력의
   `XMRig log:` 옆에 `[NOT FOUND]`가 있는지 확인.
3. 로그 파일은 파싱되지만 아직 `miner speed` 라인을 포함할 만큼 길지
   않음. XMRig 시작 후 10~15초 대기.
4. 채굴기가 대시보드가 파싱하는 것과 다른 풀에 연결. 둘 다 작동하지만,
   POOL 패널의 URL은 XMRig이 실제로 사용한 것을 반영.

### 깨진 유니코드

일부 터미널 에뮬레이터가 진행 바에 사용된 박스 드로잉 문자(`█`와 `░`)를
렌더링 못 함. iTerm2, Alacritty, Ghostty 시도. 최근 macOS의 기본
Terminal.app도 작동.

### 키 바인딩 안 됨

먼저 대시보드 창을 클릭. Textual은 TUI에 포커스가 있을 때만 키를
가로채요. 시스템 단축키(Cmd+Tab 등)가 캡처되면 대시보드를 한 번
클릭하고 다시 시도.
