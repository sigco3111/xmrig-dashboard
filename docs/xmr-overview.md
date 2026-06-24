# What is XMR (Monero)?

> A complete guide to Monero's history, technology, comparisons,
> real-world use, and FAQ. Everything you should know before
> starting to mine.

---

## One-paragraph summary

**Monero (XMR) is a privacy-focused cryptocurrency launched in 2014**
that, unlike Bitcoin's transparent blockchain, **hides the sender,
receiver, and amount of every transaction by default.** It forked
from Bytecoin (itself a Bitcoin Cash-style hard fork) and differs
most from Bitcoin in having **no hard cap on supply** (Bitcoin
caps at 21 million). Today it has become synonymous with
dark-web payments and regulatory avoidance, but it also serves
legitimate privacy needs (charitable donations, union dues,
political refugees, etc.).

---

## History — how it started

```
  ┌────────────────────────────────────────────────────────┐
  │  2012      CryptoNote (technical paper)                 │
  │            └─> proposes ring signatures, stealth addrs   │
  │                                                        │
  │  2014.04  Bytecoin launched (CryptoNote-based)         │
  │            └─> 80% of supply pre-mined (suspected scam)  │
  │                                                        │
  │  2014.04  Monero launched (hard fork from Bytecoin)     │
  │            └─> clean chain, fresh start                 │
  │            └─> name: Esperanto for "coin"              │
  │                                                        │
  │  2017.01  RingCT introduced (encrypted amounts)         │
  │                                                        │
  │  2018.10  Kovri project started (network-level privacy)│
  │                                                        │
  │  2019.10  RandomX algorithm (CPU-friendly)              │
  │            └─> strengthened ASIC resistance, weakened GPU│
  │                                                        │
  │  2024+    mining botnets + regulatory pressure (Binance/│
  │            OKX partial delistings)                      │
  └────────────────────────────────────────────────────────┘
```

**Key milestones**:
- **2017 RingCT** — encrypted transaction amounts
- **2019 RandomX** — block ASICs, let regular users mine with CPUs (this is what XMRig uses)

---

## Technology — how privacy is implemented

The magic of Monero is the combination of three technologies:

### Ring Signatures — hiding the sender

```
  Real sender: Alice

  Ring Signature group:
  ┌─────────────────────────────────────────────┐
  │  Alice   ◀─── real sender (verifier can't tell)│
  │  Bob                                         │
  │  Carol                                       │
  │  David                                       │
  │  Eve                                         │
  └─────────────────────────────────────────────┘

  Outside observer: "Someone in this 5-person ring sent it" (20% each)
  Recipient knows: "Alice sent it to me"
```

### Stealth Addresses — hiding the recipient

```
  Bob sends 1 XMR to Alice:

  Bob knows: Alice's public address (can derive via view key)
  Blockchain records: one-time address (e.g. 5AbCd...9xYz)

  Alice's wallet: uses her view key + spend key to auto-detect incoming
  Outside observer: "Someone at 5AbCd...9xYz received it" (not Alice)
```

### RingCT — hiding the amount

```
  Public blockchain: amount = ??? (Pedersen commitment encrypted)
  Network consensus:  amount is non-zero, non-negative, no double-spend

  Outside observer: "Some amount around 1 XMR moved" (not exact)
```

### RandomX — CPU-friendly proof of work

```
  Bitcoin (SHA-256):    ASICs 100x faster, GPUs 10x faster
  Ethereum (Ethash):    GPU dominant, ASICs emerging
  Monero (RandomX):     Random CPU + RAM execution
                        → ASIC/GPU advantage under 2x
                        → Desktop CPU viable
                        → Laptops/phones can mine too
```

> **Why this matters**: Bitcoin mining is industrialized; "51% attacks"
> are in ASIC holders' hands. Monero lets ordinary users participate,
> preserving decentralization.

---

## Comparing with other coins

### Bitcoin vs Monero

| Aspect | Bitcoin (BTC) | Monero (XMR) |
| ------ | ------------- | ------------ |
| **Purpose** | Digital gold (store of value) | Privacy currency (anonymous payments) |
| **Transaction transparency** | Fully public (who, to whom, how much) | All hidden |
| **Supply cap** | 21 million (mined out by 2140) | **Uncapped** (~0.6 XMR/min forever) |
| **Block time** | 10 min | 2 min |
| **Mining algorithm** | SHA-256 (ASIC only) | RandomX (CPU friendly) |
| **Energy efficiency** | Low (mining arms race) | High (regular PC works) |
| **Legality** | Legal in most countries | 🇺🇸🇰🇷 some exchanges delisted (regulatory pressure) |
| **Tx traceability** | Possible (chain analysis) | Theoretically impossible |

### Monero vs other privacy coins

| Coin | Launched | Privacy tech | Tx speed | Mineable | Activity |
|------|----------|--------------|----------|----------|----------|
| **Monero (XMR)** | 2014 | Ring sig + Stealth + RingCT | 2 min | ✅ (RandomX) | ⭐⭐⭐⭐⭐ |
| Zcash (ZEC) | 2016 | zk-SNARKs (optional) | 75 s | ✅ (Equihash) | ⭐⭐⭐ |
| Dash | 2014 | PrivateSend (mixing, optional) | 2.5 min | ✅ | ⭐⭐ |
| Pirate Chain (ARRR) | 2018 | zk-SNARKs (mandatory) | 1 min | ✅ | ⭐⭐ |
| Verge (XVG) | 2014 | Tor + I2P | 30 s | ✅ | ⭐ |

> **Monero's key differentiator**: other privacy coins are
> **"opt-in"** (transparent by default); Monero is **"opt-out"**
> (private by default). Users cannot accidentally disable privacy.

### Monero vs Tornado Cash (Ethereum mixer)

| Aspect | Monero | Tornado Cash |
| ------ | ------ | ------------ |
| **Platform** | Own chain | App on Ethereum |
| **Trust model** | Mathematical (cryptography) | Smart contract (US sanctioned 2022) |
| **Users** | Anyone | MetaMask users only |
| **Sanctionable** | The chain itself (hard) | Smart contract address (easy) |

> **Monero's advantage**: Tornado Cash was sanctioned by the US
> Treasury in 2022, blocking its front-end. Monero's distributed
> full nodes span the world; single sanctions are difficult.

---

## Real-world use — who actually uses it

### Legitimate uses

```
  ┌────────────────────────────────────────────────────────┐
  │  🏥 Medical     - STD diagnosis, psychiatric care       │
  │  🎗️ Charity     - union, refugee, political donations   │
  │                  (protects donor identity)               │
  │  🛡️ Whistleblow - corporate fraud reporters             │
  │  🏴‍☠️ Dissent     - journalists, activists in autocracies │
  │  🛒 Consumer    - "I don't want my spending recorded    │
  │                  forever"                                │
  └────────────────────────────────────────────────────────┘
```

### Misuse

```
  ┌────────────────────────────────────────────────────────┐
  │  💀 Ransomware   - 2020 WannaCry (XMR ransom demands)   │
  │  🌑 Dark markets - 2017 AlphaBay (XMR accepted)        │
  │  🎣 Phishing     - hard to trace addresses misused     │
  │  🏦 Money laundry - few legal on-ramps → some detour    │
  └────────────────────────────────────────────────────────┘
```

> **Balanced view**: Monero itself is a neutral tool. Cash is also
> used in drug deals, but legitimate uses dominate. Same for Monero:
> legitimate privacy use vastly outweighs abuse. But the fact
> **regulators are nervous** is real.

---

## Regulatory environment (2026)

| Country/region | XMR status |
| -------------- | ---------- |
| 🇺🇸 USA | Legal (taxable by IRS); some exchanges delisted (Binance.US 2024) |
| 🇰🇷 Korea | Legal (taxable); top 5 exchanges (Upbit/Bithumb/Coinone/Korbit/Gopax) do not list XMR |
| 🇪🇺 EU | Legal; AML/TFR regulations tightening |
| 🇯🇵 Japan | Legal; some exchanges list (DMM Bitcoin, etc.) |
| 🇦🇺 Australia | Legal; AUSTRAC-registered exchanges only |
| 🇨🇳 China | All crypto illegal |

> **How to obtain XMR from Korea**:
> - ✅ Mine it (this guide's XMRig + withdraw to overseas exchange like KuCoin)
> - ✅ Overseas exchange P2P (KuCoin, MEXC, Kraken)
> - ❌ Domestic top 5 exchanges (not listed)
> - ✅ Direct P2P (peer trade)

---

## Four ways to obtain XMR

| Method | Difficulty | Cost | Privacy |
| ------ | ---------- | ---- | ------- |
| **⛏️ Mining (XMRig)** | Easy | Electricity | Best (create directly) |
| 💱 Exchange buy | Easy | Premium | Low (KYC) |
| 🤝 P2P trade | Medium | Market | Medium |
| 🎁 Airdrops/rewards | Hard | Time | High |

> **Safest and most private: mining.** That is why this guide
> starts with XMRig. Buying from an exchange leaves a "who sent
> what to whom" receipt.

---

## FAQ

**Q: Will XMR replace Bitcoin?**
A: No. Different purposes. BTC is "digital gold" (store of value);
XMR is "digital cash" (private payment). They coexist.

**Q: Why are exchanges delisting XMR?**
A: The EU's TFR (Travel Rule) and US FinCEN regulations are
tightening; exchanges are self-removing "high-risk assets." Binance
stopped new XMR listings in the EU in 2024 — a representative case.

**Q: Is XMR really untraceable?**
A: **Theoretically very hard, but not absolutely impossible.** In
2020 Chainalysis announced a Monero tracing tool, though efficacy
is debated. "Untraceable for most users" is the accurate phrasing.

**Q: Is mining XMR legal?**
A: In Korea, mining itself is legal (electricity use may need to be
reported). Selling/using mined XMR is a regular asset transaction
subject to tax.

**Q: Without a supply cap, isn't XMR highly inflationary?**
A: **Disinflation** structure — about 0.87%/year as of 2024. Over
time emission decreases, asymptotically approaching zero (like
Bitcoin). Sometimes called an "inflation hedge cryptocurrency."

**Q: Is it like a 21st-century gold standard?**
A: Opinions differ. Proponents: "BTC is digital gold, XMR is digital
cash, both needed." Critics: "Governments will eventually regulate
it out."

---

## Limits and future

### Monero's weaknesses

```
  ┌────────────────────────────────────────────────────────┐
  │  📊 Scalability   - 1.5-2 KB per tx (10x BTC), chain   │
  │                    size grows fast (pruning helps)       │
  │                                                        │
  │  ⚡ Throughput    - ~4-5 tx/s (similar to BTC)         │
  │                    Visa-grade needs L2/layer           │
  │                                                        │
  │  📱 UX            - wallet sync needs tens of GB       │
  │                    (light wallet in development)        │
  │                                                        │
  │  ⚖️ Reg risk      - delisting, sanctions may expand     │
  │                    (EU TFR 2024, more regulations coming)│
  └────────────────────────────────────────────────────────┘
```

### Roadmap (2026)

- **Triptych** — larger ring sizes, stronger privacy
- **FCMP++** — Full Chain Membership Proofs
- **Seraphis** — next-gen transaction protocol (refactor)

---

## Conclusion — who needs XMR

```
  People who really need XMR:
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ✅ "I don't want my spending recorded forever"
  ✅ Union/charity/political donors who want privacy
  ✅ Dissidents, whistleblowers, journalists
  ✅ Sensitive medical payments (STDs, psychiatry)
  ✅ Anyone who prioritizes legitimate privacy rights

  People who don't really need XMR:
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ❌ "Just long-term investment" → BTC, ETH, ETF
  ❌ "I want to earn DeFi interest" → ETH L2
  ❌ "Smart contracts" → ETH, SOL
  ❌ "I want to buy NFTs" → ETH

  Conclusion: XMR is a tool with a clear use case ("privacy
  currency"). It doesn't replace other coins — it coexists.
```

---

## Related docs

- [docs/getting-started.md](getting-started.md) — start mining Monero
- [docs/exchanges.md](exchanges.md) — exchange selection guide
- [docs/security.md](security.md) — security best practices
- [docs/dashboard.md](dashboard.md) — TUI dashboard usage
