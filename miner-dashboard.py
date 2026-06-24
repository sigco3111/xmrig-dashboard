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
    """Real-time hashrate with progress bars."""
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

        h = (
            f"[bold cyan] HASHRATE [/bold cyan]\n\n"
            f"  10s:  {hr_10:>8,.1f} H/s   {bar(hr_10)}\n"
            f"  60s:  {hr_60:>8,.1f} H/s   {bar(hr_60)}\n"
            f"  15m:  {hr_15:>8,.1f} H/s   {bar(hr_15)}\n"
            f"  max:  {hr_max:>8,.1f} H/s\n"
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
        cpu_bar = f"{bar_full * (int(cpu_pct) // 5)}{bar_empty * (20 - int(cpu_pct) // 5)}"
        mem_bar = f"{bar_full * (int(mem_pct) // 5)}{bar_empty * (20 - int(mem_pct) // 5)}"
        temp_str = f"{temp:.0f}C" if temp else "n/a"
        power = estimate_power(cpu_pct)
        cores = psutil.cpu_count() or 1
        h = (
            f"[bold magenta] SYSTEM [/bold magenta]\n\n"
            f"  CPU    {cores}C/{cores}T  ~{cpu_pct*100/100:.0f}% load\n"
            f"         {cpu_bar} {cpu_pct:5.1f}%  {temp_str}\n\n"
            f"  RAM    {mem_used:.1f}/{mem_total:.1f} GB\n"
            f"         {mem_bar} {mem_pct:5.1f}%\n\n"
            f"  POWER  ~{power:.0f}W (estimated)\n"
            f"  UPTIME {int(uptime//3600)}h {int((uptime%3600)//60)}m\n"
        )
        return h


class PoolPanel(Static):
    """Pool/connection status."""
    def render(self) -> str:
        s = self.app.state.get("xmrig", _DEFAULT_STATE)
        status = "[+] connected" if s.get("pool_connected") else "[-] disconnected"
        pool_url = s.get("pool_url", "pool.supportxmr.com:5555") or "pool.supportxmr.com:5555"
        block = s.get("block_height", 0)
        threads_r = s.get("threads_ready", 0)
        threads_t = s.get("threads_total", 0)
        h = (
            f"[bold yellow] POOL [/bold yellow]\n\n"
            f"  {pool_url}\n"
            f"  {status}\n\n"
            f"  Block:  {block:,}\n"
            f"  Threads: {threads_r}/{threads_t} ready\n"
        )
        return h


class EarningsPanel(Static):
    """Mining stats + earnings estimate."""
    def render(self) -> str:
        s = self.app.state.get("xmrig", _DEFAULT_STATE)
        e = self.app.state.get("earnings", {"xmr_price": XMR_USD_PRICE})
        hr_10 = s.get("hashrate_10s", 0.0)
        hr_60 = s.get("hashrate_60s", 0.0)
        hr_avg = (hr_60 + hr_10) / 2
        accepted = s.get("accepted", 0)
        rejected = s.get("rejected", 0)
        last_share = s.get("last_share_time")
        price = e.get("xmr_price", XMR_USD_PRICE)
        # Conservative estimate: 1 KH/s yields ~0.0008 XMR/day on Monero network
        xmr_per_day = hr_avg / 1000 * 0.0008
        usd_per_day = xmr_per_day * price
        h = (
            f"[bold green] MINING STATS [/bold green]\n\n"
            f"  Accepted:   {accepted:>5d}\n"
            f"  Rejected:   {rejected:>5d}\n"
            f"  Last share: {last_share or 'n/a'}\n\n"
            f"  EARNINGS ESTIMATE (XMR: ${price:.2f})\n"
            f"  Daily:      {xmr_per_day:.6f} XMR  (${usd_per_day:.4f})\n"
            f"  Monthly:    {xmr_per_day*30:.4f} XMR  (${usd_per_day*30:.2f})\n"
            f"  Yearly:     {xmr_per_day*365:.3f} XMR  (${usd_per_day*365:.2f})\n\n"
            f"  Power cost: ~$1.50/mo - net: -$0.30/mo\n"
        )
        return h


class LogPanel(Static):
    """Recent XMRig log lines."""
    def render(self) -> str:
        s = self.app.state.get("xmrig", _DEFAULT_STATE)
        lines = list(s.get("recent_log", []))[-8:]
        # Strip markup characters from log lines to avoid Rich markup conflicts
        formatted = []
        for ln in lines:
            ln = ln.replace("[", "(").replace("]", ")")
            if len(ln) > 90:
                ln = ln[-90:]
            formatted.append(ln[:90])
        if not formatted:
            formatted = ["(waiting for log data...)"]
        h = (
            f"[bold white] LAST LOG LINES [/bold white]\n\n"
            + "\n".join(f"  {l}" for l in formatted)
        )
        return h


class StatusBar(Static):
    """Top status bar."""
    def render(self) -> str:
        s = self.app.state.get("xmrig", _DEFAULT_STATE)
        sys_m = self.app.state.get("system", {})
        mining = "[*] MINING" if s.get("pool_connected") else "[ ] IDLE"
        cpu_pct = sys_m.get("cpu_pct", 0.0)
        h = (
            f"  [bold green]{mining}[/bold green]  |  "
            f"Worker: {WORKER}  |  "
            f"CPU: {cpu_pct:5.1f}%  |  "
            f"Hash: {s.get('hashrate_10s', 0):,.0f} H/s  |  "
            f"Shares: {s.get('accepted', 0)} ok / {s.get('rejected', 0)} bad  |  "
            f"{datetime.now().strftime('%H:%M:%S')}"
        )
        return h


# ---------- Main App ----------

class MinerDashboard(App):
    CSS = """
    Screen {
        background: #0a0a0a;
    }
    #main {
        layout: grid;
        grid-size: 2 3;
        grid-gutter: 1;
        padding: 1;
    }
    HashratePanel, SystemPanel, PoolPanel, EarningsPanel, LogPanel {
        border: solid #444;
        padding: 1;
    }
    HashratePanel { border: solid cyan; }
    SystemPanel { border: solid magenta; }
    PoolPanel { border: solid yellow; }
    EarningsPanel { border: solid green; }
    LogPanel { border: solid white; }
    StatusBar {
        dock: top;
        height: 1;
        background: #1a1a1a;
        color: #ccc;
    }
    #hint {
        height: 1;
        color: #888;
        text-align: center;
    }
    """

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

    def compose(self) -> ComposeResult:
        yield StatusBar()
        with Container(id="main"):
            yield HashratePanel()
            yield SystemPanel()
            yield PoolPanel()
            yield EarningsPanel()
            yield LogPanel()
            yield Static("Press q to quit  |  p pause  |  r resume", id="hint")

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

        self.state["xmrig"] = parse_xmrig_log(XMRIG_LOG)
        self.state["system"] = get_system_metrics()

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

    def action_quit(self) -> None:
        self.notify("Goodbye!", severity="information")
        self.exit()

    BINDINGS = [
        ("p", "pause", "Pause"),
        ("r", "resume", "Resume"),
        ("q", "quit", "Quit"),
    ]


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
