# Citadel — AI-Proof Infrastructure for Creators

A platform that protects artists from unauthorized AI training by embedding cryptographic signals into their images and recording tamper-proof commitments on the Base Sepolia blockchain.

---

## Files

| File | Description |
|------|-------------|
| `app.py` | Streamlit demo app (3 tabs: Image Protection, AI Detection, Dashboard) |
| `citadel_signal.py` | Radioactive Signal injection via CLIP ViT-B/32 |
| `citadel_detector.py` | Black-box statistical detection + court-ready report generation |
| `blockchain.py` | Base Sepolia on-chain commitment (commit-reveal scheme) |
| `precomputed_detection.json` | Precomputed detection statistics (Mann-Whitney U, Cohen's d) |

---

## Setup

```bash
pip install -r requirements.txt
```

> `torch` and `open_clip_torch` are required for real signal injection.
> Without them, the app runs in simulation mode automatically.

### Environment Variables

Create a `.env` file in the project root:

```
CITADEL_PRIVATE_KEY=0xyour_base_sepolia_private_key
```

Required for real Base Sepolia transactions. Without this, blockchain commits will fail.

---

## Run

```bash
streamlit run app.py
```

---

## Demo Walkthrough

**Tab 1 — Image Protection**
Upload an image → Citadel injects a Radioactive Signal → SHA-256 commitment is recorded on Base Sepolia → download protected image.

**Tab 2 — AI Detection**
Load precomputed detection stats → view Mann-Whitney U test results (p < 10⁻⁶³, Cohen's d = 3.01) → generate court-ready evidence report with on-chain commit-reveal verification.
> ⚠️ Detection statistics are simulated values based on Radioactive Data (Sablayrolles et al., ICML 2020). Not derived from an actually trained model.

**Tab 3 — Dashboard**
Platform metrics and signal version history.
> ⚠️ All dashboard metrics are mock data for demonstration purposes.
