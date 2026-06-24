#!/usr/bin/env python3
"""
Monero Mining TUI Dashboard
============================
Real-time TUI for XMRig on this Mac.

Reads:
  - XMRig log file (default: ~/.xmrig/xmrig.log, override with XMRIG_LOG env)
  - XMRig config file (default: ~/.xmrig/xmrig-config.json, override with XMRIG_CONFIG env)
  - System metrics via psutil
  - XMR price via CoinGecko (cached, 5 min)

Controls:
  p - pause XMRig
  r - resume XMRig
  q - quit dashboard

The wallet address and worker name are read from your xmrig-config.json at
runtime. No personal info is hardcoded.

Run:
  python3 miner-dashboard.py
"""
from __future__ import annotations

import os
import re
import time
import json
import urllib.request
from collections import deque
from datetime import datetime
from pathlib import Path

import psutil
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.reactive import reactive
from textual.widgets import Static

# ---------- Configuration ----------

# Resolve paths from environment or fall back to standard locations.
# We try a list of candidate paths so the dashboard works for both
# "XMRig in ~/.xmrig/" (recommended setup) and "XMRig in $HOME/" (common default).
_DEFAULT_LOG_CANDIDATES = [
    Path.home() / ".xmrig" / "xmrig.log",
    Path.home() / "xmrig.log",
    Path("/tmp/xmrig.log"),
]
_DEFAULT_CONFIG_CANDIDATES = [
    Path.home() / ".xmrig" / "xmrig-config.json",
    Path.home() / "xmrig-config.json",
]


def _resolve_path(env_var: str, candidates: list, label: str) -> Path:
    """Pick the first existing path from env var or candidate list."""
    env_val = os.environ.get(env_var)
    if env_val:
        return Path(env_val)
    for c in candidates:
        if c.exists():
            return c
    # None of the candidates exist; return the first one anyway so the
    # caller can show a meaningful "not found" path to the user.
    return candidates[0]


XMRIG_LOG = _resolve_path("XMRIG_LOG", _DEFAULT_LOG_CANDIDATES, "log")
XMRIG_CONFIG = _resolve_path("XMRIG_CONFIG", _DEFAULT_CONFIG_CANDIDATES, "config")

# Default values (overridden from config file at startup)
WALLET = "your_monero_wallet_address_here"
WORKER = "your_worker_name"

# Fallback if XMR price API is unreachable
XMR_USD_PRICE = 318.0

# How often to refresh the dashboard (Hz)
REFRESH_HZ = 2

# How many recent log lines to keep in memory
LOG_LINES = 200

# Sparkline history length (60 samples = 30s at 2Hz)
SPARKLINE_SAMPLES = 60

# Approximate Monero network hashrate (in H/s, used for "share of network" calc)
# Updated manually; accurate to ~+/-15% over months. The actual value is on
# the order of 5-6 GH/s (mid-2026). Sources: miningpoolstats.stream, coinwarz.com
MONERO_NETWORK_HASHRATE_HPS = 5.5e9  # 5.5 GH/s — adjust quarterly

# Estimated power draw in watts (Mac mini i5-8500B full load)
ESTIMATED_MINING_WATTS = 45

# Power cost per kWh in USD (~$0.13 US average; adjust for your region)
POWER_COST_PER_KWH = 0.13

# ---------- NMMiner cyberpunk-green palette ----------
# All panel colors derive from these. Tweak in one place.
PALETTE = {
    "bg":          "#001100",  # deep terminal green-black
    "bg_dark":     "#000800",  # status bar background
    "fg":          "#33ff66",  # primary text
    "fg_dim":      "#1f8033",  # dim text (de-emphasized)
    "fg_faint":    "#0e4019",  # very dim (background grid, sparkline axis)
    "accent":      "#00ff9c",  # bright accent (active indicators)
    "warning":     "#ffaa00",  # amber (warnings, idle)
    "error":       "#ff3355",  # red (errors, rejected)
    "highlight":   "#ccffdd",  # near-white (numbers, current values)
}


# ---------- Config loading ----------

def load_xmrig_config(path: Path) -> dict:
    """Load wallet/worker from xmrig config. Returns safe defaults if missing."""
    global WALLET, WORKER
    try:
        if not path.exists():
            return {}
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        # XMRig config: { "pools": [ { "user": "wallet", "pass": "worker", ... } ] }
        pools = data.get("pools", [])
        if pools and isinstance(pools, list):
            first_pool = pools[0]
            if isinstance(first_pool, dict):
                user = first_pool.get("user", "").strip()
                worker_name = first_pool.get("pass", "").strip()
                if user:
                    WALLET = user
                if worker_name:
                    WORKER = worker_name
        return data
    except Exception:
        return {}


# ---------- Metrics collectors ----------

def get_xmr_price() -> float:
    """Fetch XMR/USD from CoinGecko (with 5-min cache)."""
    global _price_cache, _price_cache_time
    try:
        now = time.time()
        if "_price_cache" in globals() and now - _price_cache_time < 300:
            return _price_cache
        req = urllib.request.Request(
            "https://api.coingecko.com/api/v3/simple/price?ids=monero&vs_currencies=usd",
            headers={"User-Agent": "miner-dashboard/1.0"},
        )
        with urllib.request.urlopen(req, timeout=5) as r:
            data = json.loads(r.read())
        price = float(data["monero"]["usd"])
        _price_cache = price
        _price_cache_time = now
        return price
    except Exception:
        return XMR_USD_PRICE


_DEFAULT_STATE = {
    "hashrate_10s": 0.0,
    "hashrate_60s": 0.0,
    "hashrate_15m": 0.0,
    "hashrate_max": 0.0,
    "accepted": 0,
    "rejected": 0,
    "block_height": 0,
    "pool_connected": False,
    "pool_url": "pool.supportxmr.com:5555",
    "pool_latency_ms": 0,
    "threads_ready": 0,
    "threads_total": 0,
    "last_share_time": None,
    "recent_log": deque(maxlen=8),
}


def parse_xmrig_log(path: Path) -> dict:
    """Parse XMRig log file for latest stats."""
    state = {k: (v.copy() if isinstance(v, deque) else v) for k, v in _DEFAULT_STATE.items()}
    if not path.exists():
        return state

    try:
        # Read last ~50KB efficiently
        with path.open("rb") as f:
            f.seek(0, 2)
            size = f.tell()
            f.seek(max(0, size - 50_000))
            tail = f.read().decode("utf-8", errors="ignore")

        for line in tail.splitlines():
            state["recent_log"].append(line)

            # Hashrate: "miner    speed 10s/60s/15m 1313.3 1173.6 n/a H/s max 1320.9 H/s"
            m = re.search(
                r"speed\s+10s/60s/15m\s+([\d.]+)\s+([\d.]+)\s+([\d.n/a]+)\s*H/s\s+max\s+([\d.]+)",
                line,
            )
            if m:
                state["hashrate_10s"] = float(m.group(1))
                state["hashrate_60s"] = float(m.group(2))
                v = m.group(3)
                state["hashrate_15m"] = float(v) if v not in ("n/a", "") else 0.0
                state["hashrate_max"] = float(m.group(4))

            # Accepted: "cpu      accepted (5/0) diff 150000 (278 ms)"
            m = re.search(r"accepted\s+\((\d+)/(\d+)\)", line)
            if m:
                state["accepted"] = int(m.group(1))
                state["rejected"] = int(m.group(2))
                state["last_share_time"] = line[:19]  # timestamp prefix

            # Pool: "net      new job from pool.supportxmr.com:5555 diff 150000 algo rx/0 height 3702952 (3 tx)"
            m = re.search(r"new job from\s+(\S+)\s+diff\s+(\d+)\s+algo\s+(\S+)\s+height\s+(\d+)", line)
            if m:
                state["pool_connected"] = True
                state["pool_url"] = m.group(1)
                state["block_height"] = int(m.group(4))

            # READY: "cpu      READY threads 5/5 (5) huge pages 0% 0/5 memory 10240 KB"
            m = re.search(r"READY\s+threads\s+(\d+)/(\d+)", line)
            if m:
                state["threads_ready"] = int(m.group(1))
                state["threads_total"] = int(m.group(2))

    except Exception as e:
        state["recent_log"].append(f"(parse error) {e}")

    return state


def get_system_metrics() -> dict:
    """Get system metrics via psutil."""
    cpu_pct = psutil.cpu_percent(interval=0.1)
    mem = psutil.virtual_memory()
    # Try to read CPU temperature (best-effort, may not work on all systems)
    temp = None
    try:
        temps = psutil.sensors_temperatures()
        for name, entries in temps.items():
            for e in entries:
                if e.current and 30 < e.current < 110:
                    temp = e.current
                    break
            if temp:
                break
    except Exception:
        pass
    return {
        "cpu_pct": cpu_pct,
        "mem_used_gb": mem.used / 1024**3,
        "mem_total_gb": mem.total / 1024**3,
        "mem_pct": mem.percent,
        "cpu_temp_c": temp,
        "uptime_s": time.time() - psutil.boot_time(),
    }


def estimate_power(cpu_pct: float) -> float:
    """Rough power estimate for a typical desktop (watts)."""
    base = 12  # idle watts for a typical mini desktop
    mining = 35 if cpu_pct > 70 else 0
    return base + mining


# ---------- TUI Widgets ----------

class HashratePanel(Static):
    """Real-time hashrate with progress bars + sparkline."""
    def render(self) -> str:
        s = self.app.state.get("xmrig", _DEFAULT_STATE)
        hr_10 = s.get("hashrate_10s", 0.0)
        hr_60 = s.get("hashrate_60s", 0.0)
        hr_15 = s.get("hashrate_15m", 0.0)
        hr_max = s.get("hashrate_max", 0.0)
        max_hr = max(hr_10, hr_60, 1500)

        def bar(v: float) -> str:
            pct = min(100, int(v / max_hr * 100))
            filled = pct // 5
            return f"{chr(0x2588) * filled}{chr(0x2591) * (20 - filled)} {pct:3d}%"

        def bar_short(v: float) -> str:
            """Compact bar: 10 chars wide instead of 20."""
            pct = min(100, int(v / max_hr * 100))
            filled = pct // 10
            return f"{chr(0x2588) * filled}{chr(0x2591) * (10 - filled)} {pct:3d}%"

        # Dual-line sparkline: hashrate trend (green blocks) with
        # rejected-share markers (red dots) overlaid at the same x position.
        spark = ""
        history = list(self.app._hr_history)
        rejected_hist = list(self.app._rejected_history)
        if history:
            blocks = "▁▂▃▄▅▆▇█"
            mn, mx = min(history), max(history)
            rng = max(mx - mn, 1.0)
            chars = []
            for i, v in enumerate(history):
                block = blocks[min(7, int((v - mn) / rng * 7))]
                has_reject = i < len(rejected_hist) and rejected_hist[i] > 0
                chars.append((block, has_reject))
            spark_parts = []
            for block, has_reject in chars:
                if has_reject:
                    spark_parts.append(f"[bold #ff3355]●[/bold #ff3355]")
                else:
                    spark_parts.append(f"[bold #33ff66]{block}[/bold #33ff66]")
            spark = "".join(spark_parts)

        rej_rate_pct = 0.0
        total_acc = sum(self.app._accepted_history)
        total_rej = sum(self.app._rejected_history)
        if total_acc + total_rej > 0:
            rej_rate_pct = total_rej * 100 / (total_acc + total_rej)

        # Density mode - very aggressive: compact if compact_mode OR screen small
        try:
            screen_h = self.app.size.height
        except Exception:
            screen_h = 80
        if self.app._compact_mode or screen_h < 100:
            use_short = True
        else:
            use_short = False
        b = bar_short if use_short else bar

        if use_short:
            # Compact: 5 lines, no blank lines between rows
            return (
                f"[bold #00ff9c] HASHRATE [/bold #00ff9c]\n"
                f"  10s: [bold #ccffdd]{hr_10:>7,.0f}[/bold #ccffdd]  {b(hr_10)}\n"
                f"  60s: [bold #ccffdd]{hr_60:>7,.0f}[/bold #ccffdd]  {b(hr_60)}\n"
                f"  15m: [bold #ccffdd]{hr_15:>7,.0f}[/bold #ccffdd]  {b(hr_15)}\n"
                f"  trend: {spark}  [dim #1f8033]r:{rej_rate_pct:.1f}%[/dim #1f8033]\n"
            )

        # Full: 7 lines
        h = (
            f"[bold #00ff9c] HASHRATE [/bold #00ff9c]\n\n"
            f"  10s:  [bold #ccffdd]{hr_10:>8,.1f}[/bold #ccffdd] H/s   {b(hr_10)}\n"
            f"  60s:  [bold #ccffdd]{hr_60:>8,.1f}[/bold #ccffdd] H/s   {b(hr_60)}\n"
            f"  15m:  [bold #ccffdd]{hr_15:>8,.1f}[/bold #ccffdd] H/s   {b(hr_15)}\n"
            f"  max:  [bold #ccffdd]{hr_max:>8,.1f}[/bold #ccffdd] H/s\n"
            f"\n  [{PALETTE['fg_faint']}]trend[/{PALETTE['fg_faint']}] {spark}  [dim #1f8033](60s · reject: {rej_rate_pct:.1f}%)[/dim #1f8033]\n"
        )
        return h


class SystemPanel(Static):
    """CPU/RAM/temp/power panel."""
    def render(self) -> str:
        s = self.app.state.get("system", {})
        cpu_pct = s.get("cpu_pct", 0.0)
        mem_used = s.get("mem_used_gb", 0.0)
        mem_total = s.get("mem_total_gb", 0.0)
        mem_pct = s.get("mem_pct", 0.0)
        temp = s.get("cpu_temp_c")
        uptime = s.get("uptime_s", 0.0)
        bar_full = chr(0x2588)
        bar_empty = chr(0x2591)
        # Bars are concatenated as plain text, then wrapped in a single color tag.
        # (Mixing two colors per bar caused Rich markup nesting issues.)
        cpu_filled = int(cpu_pct) // 5
        cpu_empty = 20 - cpu_filled
        cpu_bar = f"[#33ff66]{bar_full * cpu_filled}[/#33ff66][#0e4019]{bar_empty * cpu_empty}[/#0e4019]"
        mem_filled = int(mem_pct) // 5
        mem_empty = 20 - mem_filled
        mem_bar = f"[#33ff66]{bar_full * mem_filled}[/#33ff66][#0e4019]{bar_empty * mem_empty}[/#0e4019]"
        # Temp: green < 70, amber 70-85, red >= 85
        if temp is None:
            temp_str = "[#1f8033]n/a[/#1f8033]"
        elif temp >= 85:
            temp_str = f"[bold #ff3355]{temp:.0f}C[/bold #ff3355]"
        elif temp >= 70:
            temp_str = f"[bold #ffaa00]{temp:.0f}C[/bold #ffaa00]"
        else:
            temp_str = f"[#ccffdd]{temp:.0f}C[/#ccffdd]"
        power = estimate_power(cpu_pct)
        cores = psutil.cpu_count() or 1

        # Density mode
        try:
            screen_h = self.app.size.height
        except Exception:
            screen_h = 80
        if self.app._compact_mode or screen_h < 36:
            # Compact: 5 lines
            return (
                f"[bold #33ff66] SYSTEM [/bold #33ff66]\n"
                f"  CPU [#ccffdd]{cpu_pct:5.1f}%[/#ccffdd] {temp_str}  [#1f8033]Cores {cores}[/#1f8033]\n"
                f"  RAM [#ccffdd]{mem_pct:5.1f}%[/#ccffdd]  [#1f8033]{mem_used:.1f}/{mem_total:.1f} GB[/#1f8033]\n"
                f"  PWR [#ccffdd]~{power:.0f}W[/#ccffdd]  UPTIME [#ccffdd]{int(uptime//3600)}h {int((uptime%3600)//60)}m[/#ccffdd]\n"
            )

        h = (
            f"[bold #33ff66] SYSTEM [/bold #33ff66]\n\n"
            f"  CPU    [#1f8033]{cores}C/{cores}T  ~{cpu_pct*100/100:.0f}% load[/#1f8033]\n"
            f"         {cpu_bar} {cpu_pct:5.1f}%  {temp_str}\n\n"
            f"  RAM    [#1f8033]{mem_used:.1f}/{mem_total:.1f} GB[/#1f8033]\n"
            f"         {mem_bar} {mem_pct:5.1f}%\n\n"
            f"  POWER  [#ccffdd]~{power:.0f}W[/#ccffdd] [#1f8033](estimated)[/#1f8033]\n"
            f"  UPTIME [#ccffdd]{int(uptime//3600)}h {int((uptime%3600)//60)}m[/#ccffdd]\n"
        )
        return h


class PoolPanel(Static):
    """Pool/connection status."""
    def render(self) -> str:
        s = self.app.state.get("xmrig", _DEFAULT_STATE)
        connected = s.get("pool_connected", False)
        if connected:
            status = "[bold #00ff9c]>>> CONNECTED <<<[/bold #00ff9c]"
        else:
            status = "[bold #ffaa00]--- DISCONNECTED ---[/bold #ffaa00]"
        pool_url = s.get("pool_url", "pool.supportxmr.com:5555") or "pool.supportxmr.com:5555"
        block = s.get("block_height", 0)
        threads_r = s.get("threads_ready", 0)
        threads_t = s.get("threads_total", 0)
        threads_pct = int(threads_r * 100 / max(threads_t, 1))
        try:
            screen_h = self.app.size.height
        except Exception:
            screen_h = 80
        if self.app._compact_mode or screen_h < 36:
            # Compact: 3 lines
            return (
                f"[bold #1f8033] POOL [/bold #1f8033]\n"
                f"  [#ccffdd]{pool_url}[/#ccffdd] {status}\n"
                f"  [#1f8033]block[/#1f8033] [#ccffdd]{block:,}[/#ccffdd] [#1f8033]threads[/#1f8033] [#ccffdd]{threads_r}/{threads_t}[/#ccffdd]\n"
            )
        h = (
            f"[bold #1f8033] POOL [/bold #1f8033]\n\n"
            f"  [#1f8033]host[/#1f8033] [#ccffdd]{pool_url}[/#ccffdd]\n"
            f"  [#1f8033]stat[/#1f8033] {status}\n\n"
            f"  [#1f8033]block[/#1f8033]    [#ccffdd]{block:,}[/#ccffdd]\n"
            f"  [#1f8033]threads[/#1f8033]  [#ccffdd]{threads_r}/{threads_t}[/#ccffdd] ready [#1f8033]({threads_pct}%)[/#1f8033]\n"
        )
        return h


class EarningsPanel(Static):
    """Mining stats + earnings estimate + network share + break-even.

    Renders in three density modes:
    - tiny (<=24 lines): essentials only, 6 lines
    - compact (25-40 lines): essentials + break-even, 8 lines
    - full (40+ lines): full forecast breakdown, ~16 lines
    """
    def render(self) -> str:
        import time as _t
        s = self.app.state.get("xmrig", _DEFAULT_STATE)
        e = self.app.state.get("earnings", {"xmr_price": XMR_USD_PRICE})
        hr_10 = s.get("hashrate_10s", 0.0)
        hr_60 = s.get("hashrate_60s", 0.0)
        hr_avg = (hr_60 + hr_10) / 2
        accepted = s.get("accepted", 0)
        rejected = s.get("rejected", 0)
        last_share = s.get("last_share_time")
        price = e.get("xmr_price", XMR_USD_PRICE)
        xmr_per_day = hr_avg / 1000 * 0.0008
        usd_per_day = xmr_per_day * price
        # Reject ratio for color
        if accepted + rejected == 0:
            rej_pct_str = "[#1f8033]--[/#1f8033]"
        else:
            rej_pct = rejected * 100 / (accepted + rejected)
            if rej_pct > 5:
                rej_pct_str = f"[bold #ff3355]{rej_pct:.1f}%[/bold #ff3355]"
            elif rej_pct > 1:
                rej_pct_str = f"[bold #ffaa00]{rej_pct:.1f}%[/bold #ffaa00]"
            else:
                rej_pct_str = f"[#33ff66]{rej_pct:.1f}%[/#33ff66]"

        # === Network share ===
        network_share = hr_avg / MONERO_NETWORK_HASHRATE_HPS * 100
        if network_share < 0.0001:
            share_str = f"[#1f8033]{network_share:.6f}%[/#1f8033]"
        elif network_share < 0.01:
            share_str = f"[#ccffdd]{network_share:.5f}%[/#ccffdd]"
        else:
            share_str = f"[#ccffdd]{network_share:.4f}%[/#ccffdd]"
        net_ghs = MONERO_NETWORK_HASHRATE_HPS / 1e9

        # === Session statistics ===
        session_secs = _t.time() - self.app._session_start
        session_h = int(session_secs // 3600)
        session_m = int((session_secs % 3600) // 60)
        sess_acc = sum(self.app._accepted_history)
        sess_rej = sum(self.app._rejected_history)
        sess_total = sess_acc + sess_rej
        if sess_total > 0 and session_secs > 0:
            sess_per_hour = sess_total / (session_secs / 3600)
        else:
            sess_per_hour = 0

        # === Break-even analysis ===
        daily_kwh = ESTIMATED_MINING_WATTS * 24 / 1000
        daily_power_cost = daily_kwh * POWER_COST_PER_KWH
        if usd_per_day > 0:
            daily_net = usd_per_day - daily_power_cost
            if daily_net < 0:
                net_str = f"[bold #ff3355]${daily_net:.4f}/day (loss)[/bold #ff3355]"
            elif daily_net < 0.01:
                net_str = f"[bold #ffaa00]${daily_net:.4f}/day (break-even)[/bold #ffaa00]"
            else:
                net_str = f"[#33ff66]${daily_net:.4f}/day profit[/#33ff66]"
        else:
            net_str = "[#1f8033]n/a[/#1f8033]"

        # === Density mode (auto-detect from window size + manual override) ===
        # Available height = total screen height minus 2 (status bar) minus 1 (hint) = h-3
        # Each panel row is 3 high (header + 2 spacing in grid), so 2 rows of panels
        # get ~ (h-3) / 2 height each.
        # Heights: <30 tiny, 30-39 compact, 40+ full
        try:
            screen_h = self.app.size.height
        except Exception:
            screen_h = 80
        available = max(20, screen_h - 3) // 3  # approximate per-panel height
        if self.app._compact_mode:
            mode = "compact"
        elif screen_h < 30:
            mode = "tiny"
        elif screen_h < 42:
            mode = "compact"
        else:
            mode = "full"

        if self.app._compact_mode or screen_h < 100:
            # Compact: 6 lines
            return (
                f"[bold #33ff66] MINING STATS [/bold #33ff66]\n"
                f"  [#1f8033]shares[/#1f8033] [#ccffdd]{accepted}[/#ccffdd] ok / [bold #ff3355]{rejected}[/bold #ff3355] bad\n"
                f"  [#1f8033]session[/#1f8033] [#ccffdd]{session_h}h{session_m:02d}m[/#ccffdd] [#1f8033]({sess_per_hour:.1f}/h)[/#1f8033]\n"
                f"  [#1f8033]est/day[/#1f8033] [#ccffdd]${usd_per_day:.4f}[/#ccffdd] [#1f8033]@ ${price:.2f}[/#1f8033]\n"
                f"  [#1f8033]net share[/#1f8033] {share_str} [dim #1f8033]of {net_ghs:.1f}GH/s[/dim #1f8033]\n"
                f"  [#1f8033]break-even[/#1f8033] {net_str}\n"
            )

        # === COMPACT mode: essentials + break-even, 8-10 lines ===
        if mode == "compact":
            return (
                f"[bold #33ff66] MINING STATS [/bold #33ff66]\n\n"
                f"  [#1f8033]accepted[/#1f8033]   [#ccffdd]{accepted:>5d}[/#ccffdd]   [#1f8033]rejected[/#1f8033] [bold #ff3355]{rejected:>5d}[/bold #ff3355]\n"
                f"  [#1f8033]session[/#1f8033]    [#ccffdd]{session_h}h{session_m:02d}m[/#ccffdd] [#1f8033]({sess_per_hour:.1f} shares/h)[/#1f8033]\n"
                f"  [#1f8033]last share[/#1f8033] [#ccffdd]{last_share or 'n/a'}[/#ccffdd]\n\n"
                f"  [bold #ccffdd]EARNINGS[/bold #ccffdd] [#1f8033](XMR: ${price:.2f})[/#1f8033] [#ccffdd]${usd_per_day:.4f}/day[/#ccffdd]\n"
                f"  [#1f8033]net share[/#1f8033]  {share_str} [dim #1f8033]of {net_ghs:.1f}GH/s[/dim #1f8033]\n"
                f"  [#1f8033]break-even[/#1f8033]  {net_str}\n"
                f"  [dim #1f8033]reject rate: {rej_pct_str} | power: -${daily_power_cost:.4f}/day[/dim #1f8033]\n"
            )

        # === FULL mode: complete forecast, ~16 lines ===
        h = (
            f"[bold #33ff66] MINING STATS [/bold #33ff66]\n\n"
            f"  [#1f8033]accepted[/#1f8033]   [#ccffdd]{accepted:>5d}[/#ccffdd]\n"
            f"  [#1f8033]rejected[/#1f8033]   [bold #ff3355]{rejected:>5d}[/bold #ff3355]\n"
            f"  [#1f8033]last share[/#1f8033] [#ccffdd]{last_share or 'n/a'}[/#ccffdd]\n"
            f"  [#1f8033]session[/#1f8033]    [#ccffdd]{session_h}h{session_m:02d}m[/#ccffdd] [#1f8033]({sess_per_hour:.1f} shares/h)[/#1f8033]\n\n"
            f"  [bold #ccffdd]EARNINGS ESTIMATE[/bold #ccffdd] [#1f8033](XMR: ${price:.2f})[/#1f8033]\n"
            f"  [#1f8033]daily[/#1f8033]      [#ccffdd]{xmr_per_day:.6f}[/#ccffdd] XMR  [#1f8033]=[/#1f8033] [#ccffdd]${usd_per_day:.4f}[/#ccffdd]\n"
            f"  [#1f8033]monthly[/#1f8033]    [#ccffdd]{xmr_per_day*30:.4f}[/#ccffdd] XMR  [#1f8033]=[/#1f8033] [#ccffdd]${usd_per_day*30:.2f}[/#ccffdd]\n"
            f"  [#1f8033]yearly[/#1f8033]     [#ccffdd]{xmr_per_day*365:.3f}[/#ccffdd] XMR  [#1f8033]=[/#1f8033] [#ccffdd]${usd_per_day*365:.2f}[/#ccffdd]\n\n"
            f"  [bold #ccffdd]NETWORK[/bold #ccffdd] [#1f8033]({net_ghs:.1f} GH/s approx)[/#1f8033]\n"
            f"  [#1f8033]my share[/#1f8033]    {share_str}\n\n"
            f"  [bold #ccffdd]BREAK-EVEN[/bold #ccffdd] [#1f8033]({ESTIMATED_MINING_WATTS}W · ${POWER_COST_PER_KWH:.2f}/kWh)[/#1f8033]\n"
            f"  [#1f8033]power cost[/#1f8033]  [#ccffdd]${daily_power_cost:.4f}[/#ccffdd]/day [#1f8033]({daily_kwh:.2f} kWh)[/#1f8033]\n"
            f"  [#1f8033]net result[/#1f8033]  {net_str}\n\n"
            f"  [#1f8033]reject rate: {rej_pct_str} | power: -${daily_power_cost:.4f}/day[/#1f8033]\n"
        )
        return h

class LogPanel(Static):
    """Recent XMRig log lines — terminal-green styled."""
    def render(self) -> str:
        s = self.app.state.get("xmrig", _DEFAULT_STATE)
        try:
            screen_h = self.app.size.height
        except Exception:
            screen_h = 80
        # Fewer log lines in small windows to save space
        if self.app._compact_mode or screen_h < 36:
            max_lines = 3
        else:
            max_lines = 5
        lines = list(s.get("recent_log", []))[-max_lines:]
        formatted = []
        for ln in lines:
            ln = ln.replace("[", "(").replace("]", ")")
            if len(ln) > 90:
                ln = ln[-90:]
            formatted.append(ln[:90])
        if not formatted:
            formatted = ["[#1f8033](waiting for log data...)[/#1f8033]"]
        h = (
            f"[bold #0e4019] LAST LOG LINES [/bold #0e4019]\n"
            + "\n".join(f"  [#1f8033] [/#1f8033][#33ff66]{l}[/#33ff66]" for l in formatted)
        )
        return h


class StatusBar(Static):
    """Top status bar — NMMiner cyberpunk green, one-line summary."""
    def render(self) -> str:
        s = self.app.state.get("xmrig", _DEFAULT_STATE)
        sys_m = self.app.state.get("system", {})
        connected = s.get("pool_connected", False)
        # Use brighter accent when mining, dim when idle
        if connected:
            mining = "[bold #00ff9c]>>> MINING <<<[/bold #00ff9c]"
        else:
            mining = "[#ffaa00]--- IDLE ---[/#ffaa00]"
        cpu_pct = sys_m.get("cpu_pct", 0.0)
        hr = s.get("hashrate_10s", 0)
        accepted = s.get("accepted", 0)
        rejected = s.get("rejected", 0)
        rej_color = "#ff3355" if rejected > 0 else "#1f8033"
        mode = "[#ccffdd]COMPACT[/#ccffdd]" if self.app._compact_mode else "[#1f8033]FULL[/#1f8033]"
        h = (
            f"  {mining}  "
            f"[#1f8033]|[/#1f8033] [#ccffdd]{WORKER}[/#ccffdd]  "
            f"[#1f8033]|[/#1f8033] CPU [bold #ccffdd]{cpu_pct:5.1f}%[/bold #ccffdd]  "
            f"[#1f8033]|[/#1f8033] [bold #00ff9c]{hr:,.0f}[/bold #00ff9c] H/s  "
            f"[#1f8033]|[/#1f8033] shares [#ccffdd]{accepted}[/#ccffdd] ok / "
        )
        # Append rejected with its own color (avoid nested same-color markup)
        if rejected > 0:
            h += f"[bold #ff3355]{rejected}[/bold #ff3355] bad  "
        else:
            h += f"[#1f8033]{rejected}[/#1f8033] bad  "
        h += (
            f"[#1f8033]|[/#1f8033] mode {mode}  "
            f"[#1f8033]|[/#1f8033] [#ccffdd]{datetime.now().strftime('%H:%M:%S')}[/#ccffdd]"
        )
        return h


# ---------- Main App ----------

class MinerDashboard(App):
    CSS = f"""
    Screen {{
        background: {PALETTE['bg']};
        color: {PALETTE['fg']};
        padding: 1 2;
    }}
    #main {{
        layout: grid;
        grid-size: 2 3;
        grid-gutter: 1;
        padding: 1 2 1 2;
    }}
    HashratePanel, SystemPanel, PoolPanel, EarningsPanel, LogPanel {{
        border: solid {PALETTE['fg_dim']};
        padding: 0 2;
        background: {PALETTE['bg']};
    }}
    /* All panel borders in cyberpunk green; brightness varies by role */
    HashratePanel {{ border: solid {PALETTE['accent']}; }}
    SystemPanel   {{ border: solid {PALETTE['fg']}; }}
    PoolPanel     {{ border: solid {PALETTE['fg_dim']}; }}
    EarningsPanel {{ border: solid {PALETTE['fg']}; }}
    LogPanel      {{ border: solid {PALETTE['fg_faint']}; }}
    /* Pulse states: alternated by refresh tick to simulate animation */
    HashratePanel.-mining-active {{
        border: solid {PALETTE['accent']};
    }}
    HashratePanel.-mining-active.-pulse-bright {{
        border: solid {PALETTE['highlight']};
    }}
    StatusBar {{
        dock: top;
        height: 1;
        margin: 0 2 1 2;
        background: {PALETTE['bg_dark']};
        color: {PALETTE['fg']};
    }}
    #hint {{
        height: 1;
        margin: 0 2;
        color: {PALETTE['fg_dim']};
        text-align: center;
    }}
    /* Help modal styling */
    HelpModal {{
        background: {PALETTE['bg']};
        border: thick {PALETTE['accent']};
        padding: 1 2;
    }}
    HelpModal Label {{
        color: {PALETTE['fg']};
    }}
    """

    BINDINGS = [
        ("p", "pause", "Pause"),
        ("r", "resume", "Resume"),
        ("q", "quit", "Quit"),
        ("?", "help", "Help"),
        ("c", "compact", "Compact"),
        ("s", "screenshot", "Save"),
    ]

    state = reactive({})

    def __init__(self):
        super().__init__()
        # Pre-populate with default values so widgets can render before first refresh
        self.state = {
            "xmrig": {k: (v.copy() if isinstance(v, deque) else v) for k, v in _DEFAULT_STATE.items()},
            "system": {
                "cpu_pct": 0.0,
                "mem_used_gb": 0.0,
                "mem_total_gb": 0.0,
                "mem_pct": 0.0,
                "cpu_temp_c": None,
                "uptime_s": 0.0,
            },
            "earnings": {"xmr_price": XMR_USD_PRICE},
            "running": True,
        }
        self._last_price_fetch = 0
        # History buffers for sparkline graphs (deque auto-trims to SPARKLINE_SAMPLES)
        self._hr_history: deque = deque(maxlen=SPARKLINE_SAMPLES)
        self._accepted_history: deque = deque(maxlen=SPARKLINE_SAMPLES)
        self._rejected_history: deque = deque(maxlen=SPARKLINE_SAMPLES)
        self._compact_mode: bool = False
        # Tick counter for pulse animation toggle (every 2s)
        self._tick_count: int = 0
        # Session start time (used for 'uptime' display)
        import time as _t
        self._session_start: float = _t.time()

    def compose(self) -> ComposeResult:
        yield StatusBar()
        with Container(id="main"):
            yield HashratePanel()
            yield SystemPanel()
            yield PoolPanel()
            yield EarningsPanel()
            yield LogPanel()
            yield Static(
                "[#1f8033][b]q[/b] quit  |  [b]p[/b] pause  |  [b]r[/b] resume  |  [b]c[/b] compact  |  [b]s[/b] save  |  [b]?[/b] help[/#1f8033]",
                id="hint",
            )

    def on_mount(self) -> None:
        self.title = "Monero Miner Dashboard"
        self.sub_title = WORKER
        self.set_interval(1.0 / REFRESH_HZ, self.refresh_metrics)
        self.set_interval(300.0, self.fetch_price)  # every 5 min
        self.fetch_price()

    def fetch_price(self) -> None:
        self.state["earnings"]["xmr_price"] = get_xmr_price()

    def refresh_metrics(self) -> None:
        # Update price every 5 min in this function too
        now = time.time()
        if now - self._last_price_fetch > 300:
            self.fetch_price()
            self._last_price_fetch = now

        new_state = parse_xmrig_log(XMRIG_LOG)
        # Push current hashrate into history for sparkline
        hr_10 = new_state.get("hashrate_10s", 0.0)
        if hr_10 > 0:
            self._hr_history.append(hr_10)
        # Count accepted/rejected deltas for sparkline
        new_accepted = new_state.get("accepted", 0)
        new_rejected = new_state.get("rejected", 0)
        old_xmrig = self.state.get("xmrig", {})
        old_accepted = old_xmrig.get("accepted", 0)
        old_rejected = old_xmrig.get("rejected", 0)
        accepted_delta = max(0, new_accepted - old_accepted)
        rejected_delta = max(0, new_rejected - old_rejected)
        self._accepted_history.append(accepted_delta)
        self._rejected_history.append(rejected_delta)
        self.state["xmrig"] = new_state
        self.state["system"] = get_system_metrics()

        # Toggle mining-active class on HashratePanel for pulse animation
        # (every 2s tick alternates the class to keep the animation cycling
        # even when there's no state change)
        self._tick_count += 1
        if self._tick_count % 2 == 0:
            try:
                panel = self.query_one(HashratePanel)
                connected = self.state["xmrig"].get("pool_connected", False)
                # Two classes: -mining-active (base) + -pulse-bright (alternates)
                if connected and not panel.has_class("-mining-active"):
                    panel.add_class("-mining-active")
                elif not connected and panel.has_class("-mining-active"):
                    panel.remove_class("-mining-active")
                # Pulse: toggle -pulse-bright on alternating ticks for "breathing" effect
                if self._tick_count % 4 == 0:
                    panel.add_class("-pulse-bright")
                else:
                    panel.remove_class("-pulse-bright")
            except Exception:
                pass

        # Force re-render
        for w in self.query(Static):
            if w.id not in ("hint",):
                w.refresh()
        self.query_one(StatusBar).refresh()

    def action_pause(self) -> None:
        import subprocess
        subprocess.run(["pkill", "-STOP", "-f", "xmrig --config"], check=False)
        self.notify("Mining paused", severity="information")

    def action_resume(self) -> None:
        import subprocess
        subprocess.run(["pkill", "-CONT", "-f", "xmrig --config"], check=False)
        self.notify("Mining resumed", severity="information")

    def action_compact(self) -> None:
        """Toggle compact mode (less padding, fewer log lines, no bars)."""
        self._compact_mode = not self._compact_mode
        mode_name = "COMPACT" if self._compact_mode else "FULL"
        self.notify(f"Mode: {mode_name}", severity="information")
        # Re-render all panels
        for w in self.query(Static):
            if w.id not in ("hint",):
                w.refresh()
        self.query_one(StatusBar).refresh()

    def action_help(self) -> None:
        """Show help modal with all keybindings."""
        from textual.widgets import Label
        from textual.containers import Vertical as V
        from textual.screen import ModalScreen

        class HelpModal(ModalScreen):
            BINDINGS = [("escape,q,?", "dismiss", "Close")]

            def compose(self):
                yield V(
                    Label("[bold #00ff9c]XMRig Dashboard — Keys[/bold #00ff9c]"),
                    Label(""),
                    Label("[#33ff66]p[/#33ff66]   Pause mining (SIGSTOP)"),
                    Label("[#33ff66]r[/#33ff66]   Resume mining (SIGCONT)"),
                    Label("[#33ff66]c[/#33ff66]   Toggle COMPACT / FULL mode"),
                    Label("[#33ff66]s[/#33ff66]   Save snapshot to disk"),
                    Label("[#33ff66]?[/#33ff66]   Show this help"),
                    Label("[#33ff66]q[/#33ff66]   Quit dashboard"),
                    Label(""),
                    Label("[#1f8033]XMRig keeps running when dashboard quits.[/#1f8033]"),
                    Label("[#1f8033]Press ESC or q to close.[/#1f8033]"),
                    id="help-modal",
                )

            def action_dismiss(self):
                self.dismiss()

        self.push_screen(HelpModal())

    def action_screenshot(self) -> None:
        """Save a snapshot of the current dashboard state to disk."""
        import json
        from pathlib import Path
        snap_dir = Path.home() / ".xmrig" / "snapshots"
        snap_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        snap_path = snap_dir / f"snapshot-{ts}.json"
        snapshot = {
            "timestamp": ts,
            "xmrig": dict(self.state.get("xmrig", {})),
            "system": dict(self.state.get("system", {})),
            "earnings": dict(self.state.get("earnings", {})),
            "hr_history": list(self._hr_history),
        }
        with snap_path.open("w") as f:
            json.dump(snapshot, f, indent=2, default=str)
        self.notify(f"Saved: {snap_path.name}", severity="information")

    def action_quit(self) -> None:
        self.notify("Goodbye!", severity="information")
        self.exit()


def main() -> None:
    # Resolve paths first so the user sees where we're looking
    print(f"XMRig log:        {XMRIG_LOG}  {'[OK]' if XMRIG_LOG.exists() else '[NOT FOUND]'}")
    print(f"XMRig config:     {XMRIG_CONFIG}  {'[OK]' if XMRIG_CONFIG.exists() else '[NOT FOUND]'}")
    print()

    # Load wallet/worker from xmrig config
    load_xmrig_config(XMRIG_CONFIG)

    # Sanity warnings (non-fatal)
    if not XMRIG_CONFIG.exists():
        print(f"WARNING: XMRig config not found at {XMRIG_CONFIG}")
        print(f"  Tried: {[str(c) for c in _DEFAULT_CONFIG_CANDIDATES]}")
        print(f"  Set XMRIG_CONFIG env var to the correct path,")
        print(f"  or symlink your config into one of the above locations.")
        print()

    if not XMRIG_LOG.exists():
        print(f"WARNING: XMRig log not found at {XMRIG_LOG}")
        print(f"  Tried: {[str(c) for c in _DEFAULT_LOG_CANDIDATES]}")
        print(f"  Set XMRIG_LOG env var to the correct path,")
        print(f"  or start XMRig first.")
        print(f"  The dashboard will still start, but XMRig-related panels")
        print(f"  (hashrate, pool, stats, logs) will stay empty until the log")
        print(f"  file appears.")
        print()

    app = MinerDashboard()
    app.run()


if __name__ == "__main__":
    main()
