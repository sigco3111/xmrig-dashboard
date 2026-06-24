# Choosing a Monero Exchange

> How to pick an exchange that lists XMR, get a deposit address,
> and avoid the scam tokens that fake Monero's name.

---

## Why this is harder than it should be

Monero (XMR) is one of the few major cryptocurrencies with strong
built-in privacy. That makes it a frequent target for:

- **Regulatory pressure.** Some countries and exchanges have
  delisted XMR, restricted it to certain users, or disabled
  deposits/withdrawals.
- **Scam tokens.** Because Monero's brand is recognizable, dozens
  of fake "XMR" or "MONERO" tokens exist on Solana, Ethereum, and
  other chains. They are not Monero.

This page helps you pick a real exchange, get a real XMR address,
and avoid the traps.

---

## Quick decision tree

```
  +--------------------------+
  |  Do you already have an  |
  |  account on a major      |
  |  exchange (Binance,      |
  |  Coinbase, Kraken, etc.) |
  +-----------+--------------+
              |
              v
  +---------------------+    YES    +--------------------+
  |  Does that exchange |  -------> |  Use it (if XMR    |
  |  list XMR for your  |           |  deposit is        |
  |  country?           |           |  available)        |
  +--------+------------+           +--------------------+
           | NO
           v
  +----------------------+
  |  Pick one from the   |
  |  comparison table     |
  |  below. Sign up.     |
  +----------------------+
```

---

## Exchange comparison (as of 2026)

| Exchange | XMR deposit | KYC required | Korea | Notes                          |
| -------- | ----------- | ------------ | ----- | ------------------------------ |
| Binance  | Yes (region-dependent) | Yes    | Yes   | Largest by volume; check your region |
| Kraken   | Yes         | Yes          | Limited | Strong US/EU presence; strict KYC |
| KuCoin   | Yes         | Yes          | Yes   | Beginner-friendly, no KYC for small amounts |
| Bybit    | Yes         | Yes          | Yes   | Good derivatives, XMR spot available |
| MEXC     | Yes         | No (small)   | Yes   | No KYC for limited withdrawal  |
| OKX      | Yes         | Yes          | Yes   | Global, derivatives focus      |

> **Status of XMR support changes frequently.** Check the
> exchange's deposit page before signing up. If the deposit page
> doesn't show "Monero (XMR)" with network = XMR, the exchange
> does not support XMR for you.

---

## How to verify a "Monero" entry is real

The single most important step. On any exchange, when you search
"XMR" or "Monero" in the deposit page, **multiple entries will
appear**. Most are scam tokens. The real one is identifiable by
these properties:

### Real Monero (XMR) deposit

| Property       | Real XMR                                              |
| -------------- | ----------------------------------------------------- |
| Name           | `Monero` or `Monero (XMR)`                            |
| Network        | `Monero` or `XMR` (NOT any "ERC20", "BEP20", "Solana") |
| Ticker         | `XMR`                                                 |
| Price          | Matches CoinGecko: ~$300 (varies by market)           |
| Address format | 95-106 characters, starts with `4` or `8`             |
| Daily volume   | $50M+ on the real one                                 |

### Fake XMR tokens (scams)

| Property       | Fake XMR token (on Solana / Ethereum / etc.)         |
| -------------- | ----------------------------------------------------- |
| Name           | `XMR`, `Wrapped Monero`, `MONERO` (just the word)     |
| Network        | `Solana`, `Ethereum`, `BSC`, `Base`                  |
| Ticker         | `XMR` or `WXMR` or `MONERO`                          |
| Price          | $0.00001 - $0.10 (way off from real XMR)             |
| Address format | 32-44 characters, starts with `0x` (Ethereum) or `6`/`7`/`8`/`9`/`A`/`B`/`C`/`D`/`E`/`F`/`G`/`H`/`J`/`K`/`L`/`M`/`N`/`P`/`Q`/`R`/`S`/`T`/`U`/`V`/`W`/`X`/`Y`/`Z` (Solana) |
| Daily volume   | $0 - $50K (tiny)                                      |

> **The address format is the definitive test.** A real Monero
> address is **95+ characters** and starts with `4` or `8`. If
> the address you copy is shorter than 60 characters, or starts
> with `0x` or any digit other than `4`/`8`, **it is not Monero**.
> Do not mine to that address. Your earnings will be lost.

---

## Step-by-step: getting your XMR deposit address

This flow is essentially identical across exchanges. The exact
button names vary, but the order is the same.

```
  +------------------------------------------------------------+
  |  Step 1:  Sign up                                           |
  |          - Email or phone number                            |
  |          - Strong password (uppercase + lowercase + digit   |
  |            + special char, 8+ chars)                        |
  +------------------------------------------------------------+
                              |
                              v
  +------------------------------------------------------------+
  |  Step 2:  Complete KYC (Know Your Customer)                |
  |          - Government ID (passport, driver's license, etc.) |
  |          - Selfie or short video                            |
  |          - Address (sometimes automatic)                    |
  |          - Takes 1-5 minutes, sometimes up to 24h           |
  +------------------------------------------------------------+
                              |
                              v
  +------------------------------------------------------------+
  |  Step 3:  Enable 2-Factor Authentication (2FA)             |
  |          - Strongly recommended: TOTP (Google              |
  |            Authenticator, Authy)                           |
  |          - Best: hardware security key (YubiKey)            |
  |          - Save the 2FA backup codes somewhere safe         |
  +------------------------------------------------------------+
                              |
                              v
  +------------------------------------------------------------+
  |  Step 4:  Navigate to deposit page                         |
  |          - Usually:  Wallet  ->  Deposit                   |
  |          - Or:  Assets  ->  Receive                        |
  +------------------------------------------------------------+
                              |
                              v
  +------------------------------------------------------------+
  |  Step 5:  Find Monero                                      |
  |          - Search for:  XMR  or  Monero                    |
  |          - See the comparison table above to identify       |
  |            the real one                                     |
  +------------------------------------------------------------+
                              |
                              v
  +------------------------------------------------------------+
  |  Step 6:  Verify the network                               |
  |          - The ONLY valid network is "Monero" or "XMR"      |
  |          - If you see a network selector, pick "XMR"       |
  |          - DO NOT pick any "ERC20", "BEP20", "Solana"      |
  +------------------------------------------------------------+
                              |
                              v
  +------------------------------------------------------------+
  |  Step 7:  Copy your deposit address                        |
  |          - 95-106 characters                                |
  |          - Starts with 4 or 8                               |
  |          - Use the copy button, don't try to select it     |
  |            manually (it's easy to miss characters)          |
  +------------------------------------------------------------+
                              |
                              v
  +------------------------------------------------------------+
  |  Step 8:  Paste into your xmrig-config.json                |
  |          - This is the "user" field in your pool config    |
  |          - Whitespace at start/end is OK; XMRig trims it   |
  +------------------------------------------------------------+
```

---

## What if your exchange disabled XMR after signup?

This happens. Some exchanges disable XMR for new users or for
users in certain countries after you sign up but before you
deposit.

**What to do:**

1. Withdraw any funds you already deposited (back to wherever
   you sent them from)
2. If the exchange holds fiat, withdraw to your bank
3. Open an account on a different exchange from the table above
4. If **all** exchanges have disabled XMR for you, use the
   self-custody wallet path from
   [docs/getting-started.md](getting-started.md) instead

---

## What to do if you accidentally mined to a fake address

If you pasted the wrong address into your XMRig config and it
mined for a while, the XMR is gone. The block reward went to the
fake token's smart contract, not to you. There is no recovery.

**The good news:** if you only ran XMRig for a few minutes, you
probably earned almost nothing anyway (CPU mining yields fractions
of a cent per hour on a desktop).

**The lesson:** always verify the address format (95+ chars, `4`/`8`
prefix) before starting XMRig.

---

## Quick-reference: real vs fake at a glance

```
  REAL XMR                              FAKE XMR (DO NOT USE)
  --------------------                 -------------------------
  Monero (XMR)                          XMR
  Network: Monero                       Network: Solana
  Starts with: 4... or 8...             Starts with: 6..., 7..., 8..., 9...
  Length: 95-106 chars                  Length: 32-44 chars
  Price: ~$300                          Price: $0.0001
  Volume: $50M+                         Volume: <$5K
```

When in doubt, paste the address into a Monero block explorer
(like `xmrchain.net`) **before mining to it**. A real address
will show a balance page (or "no transactions yet" for a new
address). A fake address (which is actually a Solana wallet) will
either error out or show a totally different chain's data.

---

## See also

- [docs/getting-started.md](getting-started.md) — full
  wallet/Monero setup, including the self-custody path
- [docs/supportxmr.md](supportxmr.md) — using the default mining pool
- [docs/security.md](security.md) — keeping your setup safe
