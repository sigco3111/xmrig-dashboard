# Getting Started with Monero (XMR) Mining

> A complete walkthrough from zero to a working miner + dashboard.
> Goal: have a CPU miner that earns (almost) nothing, but runs reliably
> while you watch a pretty TUI.

---

## What you'll need

| Requirement    | Notes                                                  |
| -------------- | ------------------------------------------------------ |
| A computer     | Any modern x86 or ARM CPU works; this guide assumes macOS. |
| Python 3.8+    | Already on macOS, or `brew install python@3.11`        |
| XMRig          | `brew install xmrig` (macOS) or download from xmrig.com |
| A Monero wallet address | See step 1 — receive only, ~95 chars       |
| ~30 minutes    | Most of it waiting on log files to populate           |

---

## The flow at a glance

```
  +-----------------+       +-----------------+       +-----------------+
  |  Step 1         |       |  Step 2         |       |  Step 3         |
  |  Get a wallet   | ----> |  Configure      | ----> |  Run + monitor  |
  |  (receive XMR)  |       |  XMRig          |       |  via TUI        |
  +-----------------+       +-----------------+       +-----------------+
         |                        |                         |
         v                        v                         v
    docs/wallets.md         docs/xmrig-setup.md       docs/dashboard.md
```

---

## Step 1 — Get a Monero wallet address

You have two paths: an **exchange wallet** (fast, custodial) or a
**self-custody wallet** (slower, sovereign). Pick one based on how
much you trust yourself vs. an exchange.

### Path A — Exchange wallet (5 minutes)

Any major exchange that lists Monero (XMR) can give you a deposit
address. The list of exchanges supporting XMR changes over time
as regulatory requirements shift, so this guide uses the **generic
flow** that works on any of them. A non-exhaustive list at the
time of writing includes (in alphabetical order): Binance, Bybit,
Kraken, KuCoin, MEXC, and OKX. **The dashboard works with any of
them** — it does not care which exchange holds the funds.

#### Generic flow (works on any exchange)

```
  +----------------------------------------------------------+
  |  1.  Sign up + complete KYC (passport, selfie, address)  |
  |  2.  Enable 2FA (Google Authenticator, with backup code) |
  |  3.  Navigate:  Wallet  ->  Deposit                     |
  |  4.  Search for:  XMR  or  Monero                       |
  |  5.  Select:  "Monero (XMR)"   (NOT any "wrapped" XMR)  |
  |  6.  Network:  XMR  (do NOT pick ERC20, BEP20, etc.)     |
  |  7.  Copy the address — should start with 4 or 8         |
  |  8.  Verify length is 95-106 characters                 |
  +----------------------------------------------------------+
```

> **Exchange choice tips:**
> - Pick one that has **active XMR deposit support** for your country.
>   Some exchanges (especially those serving US or Korean users)
>   have periodically disabled XMR deposits.
> - If your first choice does not list XMR, try another — the list
>   above is non-exhaustive.

#### Spotting the fake XMR tokens (CRITICAL)

If you search for "XMR" in the exchange's token search, you will see
**multiple entries** — most of them are **scam tokens** on other
chains. Here is how to pick the real one:

| Signal                  | Real XMR                              | Fake XMR (scam)                        |
| ----------------------- | ------------------------------------- | -------------------------------------- |
| **Name**                | `Monero (XMR)`                        | `XMR`, `Wrapped Monero`, `MONERO`      |
| **Network**             | `Monero` or `XMR`                     | `Solana`, `Ethereum`, `BSC`, `Base`    |
| **Price**               | ~$300 (matches CoinGecko)             | $0.00001 - $0.10                       |
| **Address format**      | 95-106 chars, starts with `4` or `8`  | 32-44 chars, starts with `0x` or `6`   |
| **Liquidity**           | Hundreds of millions USD              | $0 - $50K                              |
| **Daily volume**        | $100M+                                | $0 - $5K                               |

> **The single most reliable check:** the address you copy must
> start with `4` or `8` and be 95+ characters long. If it does not,
> you copied a fake.

### Path B — Self-custody wallet (10 minutes, recommended long-term)

For true ownership, install the official Monero wallet. The exchange
holding your funds can disappear; the official wallet is yours.

```
  +----------------------------------------------------------+
  |  1.  Visit https://www.getmonero.org/downloads/         |
  |  2.  Download "Monero GUI" for your OS                  |
  |  3.  Install and launch                                  |
  |  4.  Choose:  "Create a new wallet"                     |
  |  5.  Write down the 25-word seed phrase ON PAPER        |
  |      (not in a text file, not in a screenshot)           |
  |  6.  Set a strong wallet password                        |
  |  7.  Wait for the daemon to sync the blockchain          |
  |  8.  Go to:  Receive  ->  Copy your primary address     |
  +----------------------------------------------------------+
```

```
  ┌────────────────────────────────────────────────────────┐
  │  WARNING:  The 25-word seed is the ONLY way to        │
  │  recover your wallet. If you lose it, your XMR is     │
  │  gone forever. If someone else gets it, your XMR is   │
  │  gone forever. Write it on paper, store it somewhere  │
  │  physically safe. Do not photograph it. Do not type   │
  │  it into any website, chat, or cloud document.        │
  └────────────────────────────────────────────────────────┘
```

### Which path should I pick?

| Scenario                            | Path            |
| ----------------------------------- | --------------- |
| Want to try mining this afternoon   | A (exchange)    |
| Plan to keep mining for months      | B (self-custody) |
| Mining more than ~$50 worth of XMR  | B (self-custody) |
| Just curious / learning             | A (exchange)    |

You can always move from A to B later: mine to your exchange address,
withdraw to your self-custody wallet once the dust settles.

---

## Step 2 — Configure XMRig

### Install XMRig

**macOS (Homebrew):**
```bash
brew install xmrig
```

**Other platforms:** see <https://xmrig.com/download>

### Create the config file

Place a file at `~/.xmrig/xmrig-config.json` (or wherever you prefer):

```bash
mkdir -p ~/.xmrig
nano ~/.xmrig/xmrig-config.json
```

Paste this template, then **replace the wallet address and worker name**:

```json
{
  "autosave": true,
  "cpu": true,
  "opencl": false,
  "cuda": false,
  "pools": [
    {
      "url": "pool.supportxmr.com:5555",
      "user": "PASTE_YOUR_XMR_ADDRESS_HERE",
      "pass": "my-mac-mini",
      "keepalive": true,
      "tls": false,
      "nicehash": false
    }
  ]
}
```

#### Field reference

| Field          | Meaning                                                     |
| -------------- | ----------------------------------------------------------- |
| `url`          | Mining pool address (host:port)                             |
| `user`         | Your wallet address (95+ chars, starts with `4` or `8`)     |
| `pass`         | Worker name — anything that identifies this machine         |
| `keepalive`    | Reconnect automatically if pool drops                       |
| `tls`          | Encrypted connection to pool (slower, more private)         |
| `nicehash`     | Set `true` if mining via NiceHash, otherwise `false`        |

### Choose a mining pool

The default above points to **SupportXMR**, a well-established Monero
pool. Other popular options:

| Pool                | URL                            | Fee   | Notes                                   |
| ------------------- | ------------------------------ | ----- | --------------------------------------- |
| **SupportXMR**      | `pool.supportxmr.com:5555`     | 0.6%  | Default. Large, stable, beginner-friendly |
| MoneroOcean         | `gulf.moneroocean.stream:10128`| 0%    | Auto-switches algorithms                |
| P2Pool              | `p2pool.io:3333`               | 0%    | Fully decentralized, no pool operator   |
| HashVault           | `pool.hashvault.pro:3333`      | 0.9%  | Good for solo miners                    |
| ViaBTC              | `viabtc.com:3333`              | 2%    | Large, multi-coin                       |

> For this dashboard, **any pool works** — it just reads the log
> file. Pick the one whose URL looks most comfortable to you.

---

## Step 3 — Run and monitor

### Start the miner

```bash
xmrig --config=~/.xmrig/xmrig-config.json
```

You should see something like:

```
 * ABOUT        XMRig 6.26.0
 * CPU          Intel(R) Core(TM) i5-8500B
 * POOL #1      pool.supportxmr.com:5555
 * READY threads 5/5
```

> **Heads-up:** mining is CPU-intensive. Your machine will run warmer
> and the fan will spin up. This is normal. If you want to keep the
> machine responsive for other work, see the **pause/resume** section
> in the main README.

### Start the dashboard

In a separate terminal:

```bash
git clone https://github.com/sigco3111/xmrig-dashboard
cd xmrig-dashboard
python3 -m pip install --user textual psutil
python3 miner-dashboard.py
```

The dashboard auto-discovers `~/.xmrig/xmrig-config.json` and
`~/.xmrig/xmrig.log` by default. If your files live elsewhere:

```bash
XMRIG_LOG=/path/to/xmrig.log XMRIG_CONFIG=/path/to/config.json \
  python3 miner-dashboard.py
```

### What to look for

```
  +--------------------------------------------------------+
  |  Wait for "READY" in the XMRig console (10-15 sec)     |
  |                                                        |
  |  Wait for "accepted" lines (1-2 per minute typical)    |
  |     -> This means the pool accepted your share         |
  |     -> A "share" is a piece of proof-of-work            |
  |     -> Many shares = small fraction of block reward     |
  |                                                        |
  |  Watch the dashboard's HASHRATE panel                   |
  |     -> 1.0-1.5 KH/s on a modern desktop CPU = normal    |
  |     -> "max" is the best you've achieved this session   |
  |                                                        |
  |  Earnings panel is informational only                   |
  |     -> At 1 KH/s, you'd earn ~$0.04/day                |
  |     -> That's enough to buy a coffee... in 3 months     |
  +--------------------------------------------------------+
```

---

## Optional: run the miner in the background on macOS

If you want the miner to keep running after you close the terminal
(or auto-start on boot), use a LaunchAgent. See
[`xmrig.plist.example`](../xmrig.plist.example) in the repo root.

---

## What to do next

- [docs/xmrig-setup.md](xmrig-setup.md) — advanced XMRig configuration
- [docs/dashboard.md](dashboard.md) — using the dashboard
- [docs/security.md](security.md) — keeping your setup safe

---

## FAQ

**Q: My hashrate is 0 H/s after 30 seconds.**
A: Check that XMRig wrote to the log file the dashboard reads. Run
`tail -f ~/.xmrig/xmrig.log` in another terminal — you should see
"READY" and then "accepted" lines.

**Q: "Connection refused" errors.**
A: Your network or firewall is blocking the pool. Try a different
pool URL from the table above.

**Q: Mining is killing my battery / making my laptop hot.**
A: Pause with `p` in the dashboard, or `pkill -STOP -f "xmrig --config"`
to send SIGSTOP. Resume with `r` or `pkill -CONT`.

**Q: Can I mine to multiple addresses at once?**
A: Yes, but not with this dashboard. Add multiple pools to your
XMRig config. The dashboard only shows the first pool.

**Q: My antivirus flags XMRig.**
A: Some AVs flag miners as "PUA" (potentially unwanted app). This
is a known false positive for the legitimate XMRig binary from
<https://xmrig.com>. If you downloaded from xmrig.com or installed
via Homebrew, you're safe. If you got it from somewhere else, verify
the SHA-256 checksum.
