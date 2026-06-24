# Using the TUI Dashboard

> A reference for every panel, key, and configuration knob in
> `miner-dashboard.py`.

The dashboard uses an **NMMiner-style cyberpunk green** color
theme: deep terminal-green background (`#001100`) with bright
green text (`#33ff66`) and accent highlights (`#00ff9c`). All
panels share the same visual language.

---

## What you see at a glance

The dashboard is a 2-column, 3-row grid:

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

A status bar runs along the top:

```
  >>> MINING <<<  |  heejeong_kucoin_macmini  |  CPU 100.0%  |  1,096 H/s  |  shares 76 ok / 0 bad  |  mode FULL  |  10:42:18
```

The status bar uses different colors for each segment:
- **`>>> MINING <<<`** in bright accent green when connected, amber when idle
- **CPU/Hash/Shares** numbers in near-white (`#ccffdd`) for legibility
- **Rejected shares** turn red when > 0, dim when 0
- **`mode FULL`** / **`mode COMPACT`** shows the current density

---

## Panel reference

### HASHRATE (top-left)

```
  HASHRATE

   10s:  1,189.3 H/s   ##########░░░░░  79%
   60s:  1,173.6 H/s   ##########░░░░░  78%
   15m:  1,180.0 H/s   ##########░░░░░  78%
   max:  1,320.9 H/s

  trend ▂▃▅▆▇▆▅▆▇█▇▆▅▆▇█▆▆▇▆▅▆▇▆▆▇█  (60s)
```

| Field   | Source                                          | Meaning                                                |
| ------- | ----------------------------------------------- | ------------------------------------------------------ |
| `10s`   | XMRig's 10-second sliding window                | Instantaneous hashrate; fluctuates most                |
| `60s`   | XMRig's 60-second sliding window                | Smoother; good "what am I really getting" number        |
| `15m`   | XMRig's 15-minute sliding window                | Hourly/daily average; reflects sustained performance   |
| `max`   | Highest hashrate seen since miner started       | Sanity check; if current ≈ max, system is happy        |
| `trend` | Last 60 samples of `10s` hashrate (30s @ 2Hz)   | Sparkline; visualizes fluctuation, peaks, dips         |

The progress bars compare against `max(10s, 60s, 1500)`, so a
perfectly running miner fills the bar most of the way.

The **sparkline** uses Unicode block characters
`▁▂▃▄▅▆▇█` (lowest to highest), one character per sample.
The vertical extent is auto-scaled to the min/max of the
window, so you can spot a sudden hashrate drop or spike at
a glance — even if the absolute numbers haven't changed
much.

The HASHRATE border **pulses** (border color alternates
between accent green and near-white) when the miner is
actively connected to a pool. The pulse is driven by the
2Hz refresh cycle, not CSS animation (Textual 6.x doesn't
support `animation` CSS property).

### SYSTEM (top-right)

```
  SYSTEM

  CPU    6C/6T  ~89% load
         ##########░░░░░  89.5%  72C

  RAM    15.1/32.0 GB
         ##########░░░░░  47.2%

  POWER  ~47W (estimated)
  UPTIME 2h 18m
```

| Field          | Source              | Notes                                  |
| -------------- | ------------------- | -------------------------------------- |
| CPU cores/threads | `psutil.cpu_count` | Auto-detected                          |
| CPU load       | `psutil.cpu_percent` | 0-100% across all cores               |
| CPU temperature| `psutil.sensors_temperatures` | Color-coded: green < 70°C, amber 70-85°C, red ≥ 85°C. Often `n/a` on Apple Silicon. |
| RAM used/total | `psutil.virtual_memory` | Includes everything, not just miner |
| Power estimate | Heuristic            | 12W idle + 35W when mining (rough)    |
| Uptime         | `psutil.boot_time`   | Since last system reboot, not since miner started |

> **Power estimate disclaimer:** this is a rough guess. Real
> power draw depends on your specific CPU, the XMRig threads
> setting, and whether other apps are running. For accurate
> measurement, use a plug-in power meter.

### POOL (middle-left)

```
  POOL

  pool.supportxmr.com:5555
  [+] connected

  Block:  3,702,952
  Threads: 5/5 ready
```

| Field     | Source (XMRig log line)                          |
| --------- | ------------------------------------------------ |
| Pool URL  | `new job from <url> ...`                         |
| Status    | `connected` if any `new job` line seen, else `disconnected` |
| Block     | `height <N>` from latest job line                |
| Threads   | `READY threads X/Y` from startup line            |

> If the panel shows `disconnected` but XMRig is clearly running,
> check the LOG LINES panel for the most recent error.

### MINING STATS (middle-right)

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

| Field            | Source                                |
| ---------------- | ------------------------------------- |
| Accepted/Rejected| `accepted (A/R)` log lines (cumulative) |
| Last share       | Timestamp of most recent `accepted` line |
| XMR price        | CoinGecko API (5-min cache)           |
| Daily/Monthly/Yearly | Hashrate × 0.0008 XMR/day/KH/s    |

> **The earnings formula is intentionally simple.** It assumes
> the current network hashrate stays constant and the current
> XMR price stays constant. Both will change. The number is for
> "if everything stayed the same" reference, not a prediction.

### LOG LINES (bottom-left)

```
  LAST LOG LINES

  (miner  speed 10s/60s/15m 1189.3 1173.6 1180.0 H/s max 1320.9 H/s
  (net    new job from pool.supportxmr.com:5555 diff 150000 algo rx
  (cpu    accepted (142/0) diff 75000 (267 ms)
  (cpu    READY threads 5/5 (5) huge pages 0% 0/5 memory 10240 KB
  (net    new job from pool.supportxmr.com:5555 diff 150000 algo rx
```

| Note | What it means |
| ---- | ------------- |
| `(...)` not `[...]` | Square brackets in log lines are converted to parens to avoid Rich markup conflicts |
| 90-char truncation | Long lines are clipped on the right; the rightmost info is most-recent |
| Most recent at bottom | Oldest at top, newest at bottom (deque tail behavior) |

---

## Status bar

```
  [*] MINING  |  Worker: mac-mini  |  CPU: 89.5%  |  Hash: 1,189 H/s  |  Shares: 142 ok / 0 bad  |  09:18:42
```

This is your one-line summary. Designed to be glanceable from
across the room:

```
  GREEN bar   =  mining
  YELLOW bar  =  paused (sent SIGSTOP to XMRig)
  RED bar     =  XMRig not running or not connected
```

---

## Key bindings

| Key | Action             | What it does                                              |
| --- | ------------------ | --------------------------------------------------------- |
| `p` | **Pause** mining   | Sends `SIGSTOP` to XMRig. Process keeps running, just stops hashing. CPU drops to 0%. |
| `r` | **Resume** mining  | Sends `SIGCONT` to XMRig. Hashing resumes.                |
| `c` | **Compact** mode   | Toggle between FULL and COMPACT density. Drops bars, fewer log lines, tighter layout. |
| `s` | **Save** snapshot  | Writes current state to `~/.xmrig/snapshots/snapshot-YYYYMMDD-HHMMSS.json` (json). |
| `?` | **Help**           | Opens a modal listing all keybindings. `Esc` or `q` to close. |
| `q` | **Quit** dashboard | Closes the TUI. Does NOT stop XMRig (it keeps mining in the background). |

> **SIGSTOP vs SIGTERM:** the pause key uses `SIGSTOP`, which is
> reversible. The miner process stays alive but does no work,
> using 0% CPU. Use `r` to resume. If you want to actually kill
> the miner, use `pkill xmrig` outside the dashboard.

### Compact mode

Pressing `c` toggles between two densities:

| Mode   | What changes                                              |
| ------ | --------------------------------------------------------- |
| FULL   | All bars, all log lines, full forecast breakdown (default) |
| COMPACT | Drops CPU/RAM progress bars, reduces log lines from 8 → 3, collapses the daily/monthly/yearly earnings into a single line, drops system load average. Useful for small terminal windows or when you want more info per screen. |

The current mode is shown in the status bar (`mode FULL` or
`mode COMPACT`). Press `c` again to switch back.

### Snapshot

Pressing `s` writes a JSON file capturing the current XMRig
state, system metrics, and the hashrate sparkline history. The
file goes to `~/.xmrig/snapshots/` with a timestamped name.

```json
{
  "timestamp": "20260624-104218",
  "xmrig": {"hashrate_10s": 1096.0, "accepted": 76, ...},
  "system": {"cpu_pct": 100.0, "mem_pct": 47.5, ...},
  "earnings": {"xmr_price": 318.0},
  "hr_history": [1180.0, 1175.3, ...]
}
```

Useful for comparing runs, debugging regressions, or just
keeping a record of "how the system was at time X".

### What does NOT have a key

- No way to change the wallet/worker from the TUI (edit the config file and restart XMRig)
- No way to switch pools (same as above)
- No scrolling through log history (only the last 3-8 lines are kept)
- No way to change XMRig's CPU thread count

These are intentional — the TUI is read-only by design, so
nothing you do in the dashboard can accidentally change your
mining setup.

---

## Configuration

The dashboard has **no config file of its own**. All settings
come from:

### 1. XMRig's config file (for wallet/worker)

| Variable (in code) | Source                                  |
| ------------------ | --------------------------------------- |
| `WALLET`           | `pools[0].user` in `xmrig-config.json` (or `$XMRIG_CONFIG`) |
| `WORKER`           | `pools[0].pass` in the same file        |

If the config file is missing, the dashboard uses placeholder
text and a warning on startup:

```
  WARNING: XMRig config not found at /Users/you/.xmrig/xmrig-config.json
    Tried: ['/Users/you/.xmrig/xmrig-config.json', '/Users/you/xmrig-config.json']
    Set XMRIG_CONFIG env var to the correct path,
    or symlink your config into one of the above locations.
```

### 2. Environment variables (for paths)

| Variable       | Default (with fallback)                  |
| -------------- | ---------------------------------------- |
| `XMRIG_LOG`    | env var → `~/.xmrig/xmrig.log` → `~/xmrig.log` → `/tmp/xmrig.log` |
| `XMRIG_CONFIG` | env var → `~/.xmrig/xmrig-config.json` → `~/xmrig-config.json`     |

**Path resolution order** (first one that exists wins):

```
  1. The value of the XMRIG_LOG / XMRIG_CONFIG env var (if set)
  2. ~/.xmrig/xmrig.log (or xmrig-config.json)   ← recommended
  3. ~/xmrig.log       (or xmrig-config.json)    ← common default
  4. /tmp/xmrig.log                             ← last-resort fallback
```

If none of the candidates exist, the dashboard still starts (no
crash), but XMRig-related panels stay empty until the log file
appears. Set `XMRIG_LOG` explicitly to point at the right place.

The resolved paths are printed at startup:

```
  XMRig log:        /Users/you/xmrig.log  [OK]
  XMRig config:     /Users/you/xmrig-config.json  [OK]
```

The `[OK]` / `[NOT FOUND]` indicator tells you immediately
whether the dashboard is wired to the right files.

### 3. Command-line (none)

The dashboard takes no arguments. Edit environment variables or
the XMRig config to change behavior.

---

## Refresh rate

The dashboard polls XMRig's log file **twice per second** (2 Hz).
This is fast enough to feel live but slow enough to use
negligible CPU.

If you want to change the rate, edit `REFRESH_HZ` at the top of
`miner-dashboard.py`:

```python
REFRESH_HZ = 2  # 2 = 2x per second; 1 = 1x per second; 5 = 5x per second
```

Higher values look smoother but generate more I/O on the log
file. Lower values look choppier but use less CPU. 2 Hz is a
sensible default.

---

## Customization

### Color scheme

All colors are defined in the `PALETTE` dict near the top of
`miner-dashboard.py`. Tweak in one place and every panel
updates.

```python
PALETTE = {
    "bg":          "#001100",  # deep terminal green-black
    "bg_dark":     "#000800",  # status bar background
    "fg":          "#33ff66",  # primary text
    "fg_dim":      "#1f8033",  # dim text
    "fg_faint":    "#0e4019",  # very dim
    "accent":      "#00ff9c",  # bright accent
    "warning":     "#ffaa00",  # amber
    "error":       "#ff3355",  # red
    "highlight":   "#ccffdd",  # near-white
}
```

The palette is used both in CSS (panel borders) and in Rich
markup (text colors). The visual hierarchy:

- **Bright green** (`accent`) — active/mining state, ">>> MINING <<<"
- **Standard green** (`fg`) — primary text, numbers
- **Near-white** (`highlight`) — current values, sparkline
- **Dim green** (`fg_dim`) — labels, separator pipes
- **Very dim** (`fg_faint`) — axis labels, background hints
- **Amber** (`warning`) — idle state, mid temperature, 1-5% reject
- **Red** (`error`) — high temperature, >5% reject, errors

### Panel border colors

Panel borders use a tiered scheme so you can see what role
each panel plays at a glance:

| Panel        | Border color  | Why                                  |
| ------------ | ------------- | ------------------------------------ |
| HASHRATE     | bright accent | Most important; pulses when mining  |
| SYSTEM       | standard      | Solid reference                      |
| POOL         | dim           | Quiet when connected                 |
| MINING STATS | standard      | Solid reference                      |
| LOG LINES    | very dim      | Background context                   |

### Sparkline length

The HASHRATE sparkline keeps the last 60 samples (30s at 2Hz).
Change `SPARKLINE_SAMPLES` at the top of `miner-dashboard.py`:

```python
SPARKLINE_SAMPLES = 60  # 30s at 2Hz; 120 = 1 minute; 30 = 15s
```

Longer values = smoother curve but slower visual response.
Shorter = more responsive but noisier.

### Panel layout

The grid is also in `CSS`:

```python
#main {
    layout: grid;
    grid-size: 2 3;     # 2 columns, 3 rows
    grid-gutter: 1;     # spacing between cells
    padding: 1;
}
```

Change to `grid-size: 1 6` for a single-column layout, or
`grid-size: 3 2` for 3 columns × 2 rows.

### Earnings formula

The estimate uses a fixed `0.0008 XMR/day per KH/s` constant:

```python
xmr_per_day = hr_avg / 1000 * 0.0008
```

This is a reasonable average. For a more accurate estimate, you
could query a mining calculator API and cache the result. But
the simple formula is good enough for a "is it worth leaving it
on?" sanity check.

---

## Troubleshooting

### "XMRig config not found" on startup

Either:
- Create `~/.xmrig/xmrig-config.json`, or
- Set `XMRIG_CONFIG=/path/to/your/config.json` before launching.

### "XMRig log not found" on startup

When you see `[NOT FOUND]` next to `XMRig log:` in the startup
output, the dashboard started but cannot find your XMRig log
file. The HASHRATE, POOL, MINING STATS, and LAST LOG LINES
panels will stay empty.

**To fix**, do one of:

1. **Start XMRig first** if it isn't running yet — the log file
   appears once XMRig writes to it.
2. **Set `XMRIG_LOG` explicitly** to point at the right file:
   ```bash
   export XMRIG_LOG=/path/to/your/xmrig.log
   ~/bin/run-miner-dashboard.sh
   ```
3. **Symlink** the log into one of the standard locations:
   ```bash
   mkdir -p ~/.xmrig
   ln -sf /path/to/your/xmrig.log ~/.xmrig/xmrig.log
   ```
4. **Restart the dashboard** to re-run the path resolution after
   moving the log.

The startup output lists all candidate paths that were tried —
use that to figure out which one matches your setup.

### Dashboard shows `IDLE` even though XMRig is running

The log parser hasn't seen a `new job from <pool>` line yet. This
happens if the log file is fresh and XMRig is still initializing.
Wait 5-10 seconds; the panel will switch to `MINING` automatically.

### Hasrate shows 0 H/s

Possible causes:
1. XMRig is paused (sent `SIGSTOP` from `p` key or manually). Resume with `r`.
2. The log file is empty because XMRig writes to a different path. Check the startup output for `[NOT FOUND]` next to `XMRig log:`.
3. The log file is being parsed but is too short to contain a `miner speed` line yet. Wait 10-15 seconds after XMRig starts.
4. The miner is connected to a different pool than the dashboard parses. Both should still work, but the URL in the POOL panel will reflect whatever XMRig actually used.

### Garbled Unicode

Some terminal emulators don't render the box-drawing characters
used in the progress bars (`█` and `░`). Try iTerm2, Alacritty,
or Ghostty. The default macOS Terminal.app also works on recent
macOS versions.

### Key bindings don't work

Click into the dashboard window first. Textual intercepts keys
only when the TUI has focus. If a system hotkey (like `Cmd+Tab`)
is being captured, click in the dashboard once and try again.
