# Using SupportXMR (and similar Monero pools)

> This guide focuses on SupportXMR, the default pool recommended in
> the main README. The dashboard itself works with **any pool** — the
> only thing that changes between pools is the URL in your XMRig
> config and the web dashboard you visit to check your stats.

---

## What is a mining pool?

A solo miner trying to find a Monero block on a desktop CPU has
roughly a 1-in-several-million chance per day. A **mining pool**
combines the work of many miners, finds blocks faster, and splits
the reward proportionally.

```
  Solo mining                Pool mining
  +-----------+              +-----------+
  |   You     |              |   You     |---+
  |  1 KH/s   |              |  1 KH/s   |   |
  +-----------+              +-----------+   |  Many
        |                          |         |  miners
        v                          v         v  pooled
  Find a block in              +-------------------+
  ~1 year                      |     Pool          |
  (and get all ~$300)          |  (combines work)  |
                               +-------------------+
                                        |
                                        v
                                 Find a block in
                                 ~2 minutes
                                 (split ~$300 among
                                  thousands of miners
                                  based on contribution)
```

You earn less per block, but you earn it consistently. On a CPU
mining 1 KH/s, you might earn 0.0001 XMR every few days. That adds
up to a coffee a year. The point is not the money — it's the
monitoring.

---

## Setting up SupportXMR

### 1. Create an account (optional but recommended)

Without an account, you can still mine — the pool tracks you by
wallet address. **With an account**, you get a web dashboard, email
notifications, and configurable payout thresholds.

```
  +--------------------------------------------------------+
  |  1.  Visit https://supportxmr.com/                    |
  |  2.  Click "Sign Up" (top right)                       |
  |  3.  Enter email + strong password                     |
  |  4.  Verify email                                      |
  |  5.  Log in                                            |
  +--------------------------------------------------------+
```

### 2. Add your wallet address to the dashboard

Once logged in, you can register one or more wallet addresses. This
lets the pool show statistics per address without you having to type
the address every time you want to look at your stats.

```
  +--------------------------------------------------------+
  |  1.  Log in                                            |
  |  2.  Go to:  My Account  ->  Wallet Settings           |
  |  3.  Click "Add wallet"                                |
  |  4.  Paste your XMR address (the one you used in the   |
  |      xmrig-config.json "user" field)                   |
  |  5.  Save                                              |
  +--------------------------------------------------------+
```

> You can add multiple addresses, but only the first is used for
> the dashboard's "look up stats" flow below.

### 3. Configure your XMRig

This part is already done if you followed the main README. Confirm
the pool URL in your config:

```json
{
  "pools": [
    {
      "url": "pool.supportxmr.com:5555",
      "user": "your-xmr-address-here",
      "pass": "any-worker-name"
    }
  ]
}
```

The `pass` field is just a label for your worker. Use something
identifiable if you have multiple machines: `mac-mini-living-room`,
`desktop-home`, etc.

---

## Reading the SupportXMR web dashboard

### Main stats page

Once your miner is running, navigate to:

```
  https://supportxmr.com/
```

In the search/lookup box, paste your wallet address. You'll see a
page like this (paraphrased):

```
  +----------------------------------------------------------------+
  |  Hashrate (last 1h)         |    1,189 H/s                    |
  |  Hashrate (last 24h)        |    1,173 H/s                    |
  |  Hashrate (last 7d)         |    1,180 H/s                    |
  +----------------------------------------------------------------+
  |  Pending balance            |    0.000085 XMR  ($0.027)       |
  |  Confirmed balance          |    0.000012 XMR  ($0.004)       |
  |  Total paid                 |    0.000000 XMR  ($0.000)       |
  +----------------------------------------------------------------+
  |  Shares (valid / invalid)   |    142 / 0  (100% accepted)     |
  |  Last share                 |    2026-06-24 09:18:00 UTC      |
  +----------------------------------------------------------------+
```

#### What each metric means

| Metric                  | What it tells you                                         |
| ----------------------- | --------------------------------------------------------- |
| **Hashrate (1h/24h/7d)** | How much work your miner is doing, averaged               |
| **Pending balance**      | Earnings not yet confirmed by enough blocks to pay out     |
| **Confirmed balance**    | Earnings ready to pay out                                 |
| **Total paid**           | Lifetime payouts to your wallet                           |
| **Shares (valid/invalid)**| Network latency vs. pool's expected solution time          |
| **Last share**           | When the pool last heard from your miner                   |

> The `accepted` count in the TUI dashboard matches the "valid
> shares" count here. They are the same number reported in two
> places.

### Worker breakdown

If you click on a specific worker (or scroll to the bottom), you
see a per-worker breakdown:

```
  +----------------------------------------------------------------+
  |  Worker               |  Hashrate  |  Shares  |  Last share   |
  |  -------------------- | ---------- | -------- | ------------- |
  |  mac-mini-living-room |  1,189 H/s |    142   |  2 min ago    |
  +----------------------------------------------------------------+
```

> If you have multiple workers (e.g. several machines), the
> SupportXMR page shows all of them in one table.

---

## Payouts

### When do I get paid?

The pool pays out automatically when your **confirmed balance**
reaches the **minimum payout threshold**. By default this is
**0.004 XMR** (~$1.30 at current prices). On a desktop CPU, that
takes weeks to months to reach. The dashboard's TUI estimate
shows this in real time.

### How do I change the payout threshold?

```
  +--------------------------------------------------------+
  |  1.  Log in to supportxmr.com                          |
  |  2.  Go to:  My Account  ->  Wallet Settings           |
  |  3.  Adjust the "Minimum payout" field                 |
  |  4.  Save                                              |
  +--------------------------------------------------------+
```

You can set it as low as 0.001 XMR (~$0.32) for faster (but more
network-fee-heavy) payouts, or higher for fewer payouts and lower
per-payout fees.

### Where does the payout go?

The pool pays to the wallet address you used in XMRig. If you used
an **exchange** deposit address, the XMR lands in your exchange
account. If you used a **self-custody** address, it lands in your
local wallet.

> **Important:** if you used an exchange address, double-check that
> the exchange still supports XMR deposits. Some exchanges have
> disabled XMR for new users in certain regions. If they have, the
> payout will fail and the XMR will sit in the pool indefinitely.

---

## What if the pool is down?

If SupportXMR has an outage, XMRig will retry automatically
(thanks to `keepalive: true` in the config). Your local mining
**keeps working** — you just don't get any shares accepted until
the pool comes back. Your hash rate still counts when the pool
returns.

To check if SupportXMR is up:

```
  https://supportxmr.com/   ->  if the page loads, the pool is up
```

If you want a backup pool to fail over to, edit your XMRig config
to include a second pool:

```json
{
  "pools": [
    {
      "url": "pool.supportxmr.com:5555",
      "user": "your-xmr-address",
      "pass": "worker-1",
      "keepalive": true
    },
    {
      "url": "gulf.moneroocean.stream:10128",
      "user": "your-xmr-address",
      "pass": "worker-1",
      "keepalive": true
    }
  ]
}
```

XMRig will try them in order, falling back automatically. The TUI
dashboard will show whichever pool is currently active.

---

## SupportXMR's fee structure

| Item              | Fee                                                     |
| ----------------- | ------------------------------------------------------- |
| Pool fee          | 0.6% of block rewards                                   |
| Payout fee        | Network transaction fee (paid to Monero network, not the pool) |
| Account fee       | None                                                    |
| Withdrawal fee    | None (payouts are automatic)                            |

The pool does not charge for inactivity, for having multiple
workers, or for the web dashboard.

---

## API access (advanced)

SupportXMR exposes a JSON API you can query from scripts. The TUI
dashboard uses the same API to show real-time prices (it uses
CoinGecko for that, but SupportXMR has its own).

```
  GET https://supportxmr.com/api/miner/<your-wallet-address>/stats
```

Returns a JSON document with all the same numbers shown on the web
page. Useful for your own monitoring scripts.

---

## Other pools (briefly)

| Pool                | When to pick it                                            |
| ------------------- | ---------------------------------------------------------- |
| **SupportXMR**      | Default. Beginner-friendly, large hashrate, stable.        |
| **MoneroOcean**     | Want to support smaller coins; auto-algorithm-switching.   |
| **P2Pool**          | Want zero centralization; technical comfort required.      |
| **HashVault**       | Solo-mining feel; pool pays out the full block reward when you find one. |
| **ViaBTC**          | Already a ViaBTC user for other coins.                    |

The TUI dashboard works with all of them. To switch, just change
the `url` in your XMRig config and restart XMRig.
