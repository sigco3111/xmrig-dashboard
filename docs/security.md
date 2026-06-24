# Security Best Practices

> Mining + a public GitHub repo is a slightly unusual combination.
> This page covers the pitfalls to avoid.

---

## Threat model

| Asset                                | Threat                                                | Severity |
| ------------------------------------ | ----------------------------------------------------- | -------- |
| **Monero wallet seed** (self-custody) | Loss = total loss of funds                            | Critical |
| **Monero wallet address**             | Public exposure reduces pseudonymity                  | High     |
| **Exchange account credentials**      | Account takeover, theft of all coins                  | Critical |
| **Mining machine**                    | Cryptojacking, unauthorized use                       | Medium   |
| **Electricity bill**                  | Runaway miner (bug, misconfiguration)                 | Low      |

This page covers the practical defenses.

---

## Wallet seed (self-custody wallets only)

If you used the official Monero GUI wallet and got a 25-word seed:

```
  DO:
  - Write the seed on paper, with a pen
  - Store the paper in a physically secure location
  - Make one backup copy, stored in a different physical location
  - Verify your backup is readable (not smudged, not faded)

  DO NOT:
  - Photograph the seed (phone backups sync to the cloud)
  - Type the seed into any website, chat, or document
  - Store the seed in a password manager that is itself cloud-synced
  - Email it to yourself
  - Print it on a network printer (printer logs are not private)
```

> **The seed is the wallet.** Anyone with the seed owns the XMR.
> Treat it like the keys to a safe deposit box.

---

## Wallet address privacy

Once a Monero address is **public**, it is **public forever** —
Monero's blockchain records the address permanently, and
blockchain analysis firms correlate them with other data over
time.

### What "public" means for your address

| Where it's published                       | Consequence                                 |
| ------------------------------------------ | ------------------------------------------- |
| Your own xmrig-config.json                 | Safe — it's your file                       |
| A public GitHub repo                       | **Permanent public record**                 |
| A shared doc, chat, or screenshot          | Likely permanent, but you can take it down  |
| The SupportXMR web dashboard               | **Public** — anyone with the address can see your hashrate |
| A coinjoin, exchange, or KYC-required service | Traces back to your identity             |

> The address is **not** the same as the seed. Sharing the
> address lets people send you XMR (or watch your balance). It
> does not let them spend your XMR. But it does break
> pseudonymity if the address ever touches a KYC service.

### How this repo handles it

```
  +--------------------------------------------------------------+
  |  miner-dashboard.py:                                         |
  |    - NO hardcoded wallet address                             |
  |    - NO hardcoded worker name                                |
  |    - NO hardcoded exchange name                              |
  |    - Wallet/worker are loaded from your xmrig-config.json    |
  |      at runtime                                              |
  |                                                              |
  |  .gitignore:                                                 |
  |    - xmrig-config.json is ignored by default                 |
  |    - *.log is ignored (logs can leak addresses too)          |
  |                                                              |
  |  README:                                                     |
  |    - The placeholder example shows "PASTE_YOUR_XMR_ADDRESS"  |
  |    - Never commit your real address to git                   |
  +--------------------------------------------------------------+
```

If you fork this repo and accidentally commit your real
`xmrig-config.json`, **the address is leaked permanently**. To
clean up:

1. `git filter-branch` or `git filter-repo` to remove the file from history
2. Force-push the cleaned history
3. **The address is still leaked** — assume it's public, move to a new address if that matters

---

## Exchange account security

If you used an exchange deposit address:

### 1. Two-factor authentication (2FA)

```
  Enable 2FA in this order of preference:
    1. Hardware security key (YubiKey, Titan)   - strongest
    2. TOTP (Google Authenticator, Authy)       - good
    3. SMS                                       - weak (SIM swap attacks)

  Save the 2FA backup codes in a password manager.
  Test login from a fresh browser BEFORE depositing funds.
```

### 2. Withdrawal address whitelist

Most exchanges let you whitelist withdrawal addresses. If enabled,
XMR can only be withdrawn to addresses you pre-approve. This stops
an attacker who gets your password from draining your account.

### 3. Anti-phishing

```
  +----------------------------------------------------------+
  |  Always navigate to the exchange via bookmark or typed   |
  |  URL. Never click email links that claim to be from the  |
  |  exchange.                                                |
  |                                                           |
  |  Bookmark the real exchange URL in your browser.          |
  |  Use a unique password per exchange.                      |
  |  Set up the exchange's anti-phishing code (if offered).  |
  +----------------------------------------------------------+
```

---

## Mining machine security

### Run XMRig from a dedicated user (Linux)

```
  # Create a low-privilege user
  sudo useradd -m -s /bin/bash miner

  # Switch to that user
  sudo -u miner -i

  # Run XMRig from this user's home
  ~/xmrig --config=~/xmrig-config.json
```

This way, if XMRig ever has a security vulnerability, the
attacker has access to a low-privilege user — not your normal
account.

On macOS, this is harder. The LaunchAgent example runs as your
user, which is fine for a personal machine but not appropriate
for a server.

### Verify the XMRig binary

XMRig's website publishes SHA-256 checksums for every release.
Verify before running:

```
  # Download the official release
  curl -L -o xmrig-6.26.0.tar.gz https://github.com/xmrig/xmrig/releases/download/v6.26.0/xmrig-6.26.0.tar.gz

  # Get the official SHA-256
  curl -L https://github.com/xmrig/xmrig/releases/download/v6.26.0/SHA256SUMS | head -3

  # Verify
  shasum -a 256 xmrig-6.26.0.tar.gz
```

The two hashes must match. If they don't, do NOT run the binary.

> If you installed via Homebrew (`brew install xmrig`), the
> checksum is verified automatically by Homebrew. This is the
> recommended path for macOS users.

### Network exposure

XMRig, by default, **only makes outbound connections** to the
pool. It does not listen for incoming connections. The dashboard
also only makes outbound requests (CoinGecko API). Neither opens
ports on your machine.

> If you want to verify, run `netstat -an` while XMRig is
> running. You should see one established outbound connection
> to the pool IP, and nothing else related to XMRig.

### Watch for cryptojacking

If your hashrate spikes without you starting the miner, or your
CPU is constantly 100% with no obvious cause, you may have a
cryptojacker. Common vectors:

- Compromised browser extensions
- Pirated software with hidden miners
- A website running a JavaScript miner (rare now)

Defenses:
- Browser extension audit (remove anything you don't use)
- Activity Monitor → check "Energy" tab → kill high-CPU processes
- `htop` or Activity Monitor → look for `xmrig`, `minerd`, `cpuminer` in process names

---

## Electricity bill protection

Mining on a desktop for 24 hours uses roughly 1 kWh. On a typical
$0.15/kWh tariff, that's **$0.04/day** in electricity. But bugs
can cause runaway usage:

- XMRig has a `--max-threads` option — set it to limit CPU usage
- The dashboard's `p` key pauses mining instantly
- macOS Users → Energy Saver settings can prevent runaway

If you want a hard limit, edit your XMRig config:

```json
{
  "cpu": {
    "enabled": true,
    "max-threads-hint": 50
  }
}
```

This caps XMRig to 50% of one core's worth of compute. Lower
numbers = lower power = lower hashrate = lower earnings. Pick
the trade-off you want.

---

## What this dashboard does NOT do

For full transparency:

| Behavior                                         | This dashboard? |
| ------------------------------------------------ | --------------- |
| Send your wallet address anywhere                | No              |
| Send your hashrate to a third party              | No              |
| Open a network port on your machine              | No              |
| Write any files (other than the standard config) | No              |
| Modify XMRig's config file                       | No              |
| Run any background process after you quit         | No              |

The only outbound network call is `GET api.coingecko.com` for
the XMR/USD price, every 5 minutes, with the response cached.
You can verify this by running the dashboard with Little Snitch
or similar network monitor.

---

## Reporting a security issue

If you find a security issue in this repo, please email the
maintainer (see GitHub profile) rather than opening a public
issue. Security fixes deserve their own advisory, not a noisy
public thread.
