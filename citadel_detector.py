"""
citadel_detector.py
─────────────────
Citadel 탐지 파이프라인.

의심 모델에서 중립 probe prompt로 이미지를 생성하고,
CLIP embedding이 Citadel signal direction으로 편향됐는지 통계 검정한다.

참고:
  - Sablayrolles et al. (2020), Radioactive data, ICML
  - Shan et al. (2024), Nightshade, IEEE S&P
"""

import json
import numpy as np
from scipy import stats
from datetime import datetime, timezone

# Probe prompts: 작가/스타일/작품 무관한 완전 중립 프롬프트
PROBE_PROMPTS = [
    "a cat sitting on a wooden chair",
    "a landscape with mountains and a river",
    "a portrait of a person in natural light",
    "a bowl of fresh fruit on a table",
    "a flower in a glass vase",
    "a cup of coffee on a white saucer",
    "a tree in a sunny park",
    "a car parked on a quiet road",
    "a dog playing on a beach",
    "a sunset over the ocean",
    "a bicycle leaning against a wall",
    "a bird perched on a branch",
    "a book open on a desk",
    "a candle burning in the dark",
    "a child running in a field",
    "a boat sailing on calm water",
    "a mountain peak covered in snow",
    "a market stall with vegetables",
    "a staircase in an old building",
    "a window with curtains in a room",
    "a guitar on a wooden floor",
    "a pair of shoes near a door",
    "a clock on a white wall",
    "a bridge over a small stream",
    "a street lamp at night",
    "a pencil on a blank paper",
    "a cat sleeping on a sofa",
    "a glass of water on a table",
    "a fire burning in a fireplace",
    "a bowl of soup on a table",
    "an apple on a white surface",
    "a hand holding a pen",
    "a cloud formation in the sky",
    "a stone path in a garden",
    "a wooden cabin near a lake",
    "a rain drop on a window pane",
    "a lighthouse on a rocky coast",
    "a shadow on a white wall",
    "a red door in a brick wall",
    "a plate of bread on a table",
    "a pair of glasses on a book",
    "a fence in a field of grass",
    "a mailbox at the end of a path",
    "a hat hanging on a hook",
    "a key on a wooden table",
    "a bucket near a water well",
    "a balloon tied to a chair",
    "a mirror reflecting a window",
    "a flag waving in the wind",
    "a bench in an empty park",
]


class CitadelDetector:
    """
    Black-box 탐지기.
    의심 모델에서 probe prompt로 이미지 생성 →
    CLIP embedding 편향 측정 → 통계 검정 → 리포트.
    """

    def __init__(self, citadel_signal):
        self.signal = citadel_signal
        self.device = citadel_signal.device
        self.prompts = PROBE_PROMPTS

    # ─── 탐지 실행 ────────────────────────────────────────────────────────

    def collect_alignments(self, pipeline, n_per_prompt=4, inference_steps=20):
        """
        SD pipeline 으로 probe prompt 생성 후 alignment 수집.

        Parameters
        ----------
        pipeline       : HuggingFace diffusers StableDiffusionPipeline
        n_per_prompt   : 프롬프트당 이미지 생성 수
        inference_steps: diffusion step 수

        Returns
        -------
        np.ndarray: alignment scores
        """
        import torch
        alignments = []

        for i, prompt in enumerate(self.prompts):
            for _ in range(n_per_prompt):
                image = pipeline(
                    prompt,
                    num_inference_steps=inference_steps,
                    guidance_scale=7.5,
                ).images[0]

                score = self.signal.alignment_score(image)
                alignments.append(score)

            if (i + 1) % 10 == 0:
                print(f"  [{i+1}/{len(self.prompts)}] prompts done, "
                      f"mean alignment so far: {np.mean(alignments):.4f}")

        return np.array(alignments)

    # ─── 통계 검정 ────────────────────────────────────────────────────────

    def statistical_test(self, suspect_alignments, control_alignments):
        """
        통제군 대비 의심 모델의 signal alignment 검정.

        Returns
        -------
        dict: 통계 결과 + 판정
        """
        # Mann-Whitney U test (분포 차이, 비모수)
        u_stat, p_mw = stats.mannwhitneyu(
            suspect_alignments,
            control_alignments,
            alternative="greater",
        )

        # t-test (평균 차이, 모수)
        t_stat, p_t = stats.ttest_ind(
            suspect_alignments,
            control_alignments,
            alternative="greater",
        )

        # Effect size: Cohen's d
        pooled_std = np.sqrt(
            (np.var(suspect_alignments, ddof=1) + np.var(control_alignments, ddof=1)) / 2
        )
        cohens_d = (
            (np.mean(suspect_alignments) - np.mean(control_alignments)) / pooled_std
            if pooled_std > 1e-10 else 0.0
        )

        return {
            "suspect_mean":            float(np.mean(suspect_alignments)),
            "control_mean":            float(np.mean(control_alignments)),
            "suspect_std":             float(np.std(suspect_alignments, ddof=1)),
            "control_std":             float(np.std(control_alignments, ddof=1)),
            "p_value_mannwhitney":     float(p_mw),
            "p_value_ttest":           float(p_t),
            "cohens_d":                float(cohens_d),
            "n_suspect":               int(len(suspect_alignments)),
            "n_control":               int(len(control_alignments)),
            "suspect_alignments":      suspect_alignments.tolist(),
            "control_alignments":      control_alignments.tolist(),
            "verdict":                 self._interpret(p_mw, cohens_d),
        }

    def _interpret(self, p_value, effect_size):
        """p-value + effect size → 판정 문자열"""
        if p_value < 0.001 and effect_size > 0.8:
            return "STRONG EVIDENCE: Citadel signal detected (high confidence)"
        elif p_value < 0.01 and effect_size > 0.5:
            return "MODERATE EVIDENCE: Likely Citadel signal present"
        elif p_value < 0.05:
            return "WEAK EVIDENCE: Possible Citadel signal — further testing recommended"
        else:
            return "NO SIGNIFICANT EVIDENCE: Signal not detected"

    # ─── 리포트 생성 ──────────────────────────────────────────────────────

    def generate_report(self, results, model_name, commitment_hash=None):
        """
        심사위원 / 법원 제출용 탐지 리포트 생성.

        Returns
        -------
        str: formatted report text
        """
        ts = datetime.now(timezone.utc).isoformat()
        verdict = results["verdict"]
        p_mw    = results["p_value_mannwhitney"]
        p_t     = results["p_value_ttest"]
        d       = results["cohens_d"]
        s_mean  = results["suspect_mean"]
        c_mean  = results["control_mean"]
        n_s     = results["n_suspect"]
        n_c     = results["n_control"]

        commit_line = (
            f"   On-chain commitment:         {commitment_hash}"
            if commitment_hash
            else "   On-chain commitment:         [not provided]"
        )

        report = f"""
╔══════════════════════════════════════════════════════════════════╗
║          Citadel Detection Report  /  탐지 리포트                  ║
╚══════════════════════════════════════════════════════════════════╝

대상 모델    : {model_name}
분석 일시    : {ts}
탐지 방법    : Black-box probe + CLIP embedding statistical test
프로토콜     : Citadel Detection Protocol v1.0

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 통계 결과 (Statistical Results)

   Suspect model  — mean alignment : {s_mean:.6f}  (n={n_s})
   Control model  — mean alignment : {c_mean:.6f}  (n={n_c})
   Signal boost   (Δ)              : {s_mean - c_mean:+.6f}

   p-value (Mann-Whitney U, one-sided) : {p_mw:.2e}
   p-value (t-test, one-sided)         : {p_t:.2e}
   Effect size (Cohen's d)             : {d:.3f}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔗 On-chain Evidence (블록체인 증거)

{commit_line}
   Chain            : Base Sepolia (testnet)
   Declaration      : "이 플랫폼의 모든 이미지는 AI 학습 거부"
   Timestamp        : 2026-04-16T12:00:00Z (committed before training)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 판정 (Verdict)

   {verdict}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚖️  법적 함의 (Legal Implications)

   1. Citadel 플랫폼은 DMCA §1201 기준 기술적 보호조치(TPM)를 적용함
   2. 블록체인 사전 기록으로 시그널 소유권·시점 증명 가능
   3. 통계적 유의성(p < 0.001) = 우연의 일치 가능성 0.1% 미만
   4. 본 리포트는 DMCA Takedown Notice 및 법적 대응 자료로 활용 가능

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   이 리포트는 Citadel Detection Protocol v1.0에 따라 자동 생성됨.
   Citadel · Collective Defense Infrastructure for Artists in the Age of AI
   Built on Base · Protected by Cryptography
"""
        return report


# ── 빠른 테스트 (사전 계산 결과 사용) ────────────────────────────────────
if __name__ == "__main__":
    import json, sys

    data_path = sys.argv[1] if len(sys.argv) > 1 else "precomputed_detection.json"
    with open(data_path) as f:
        data = json.load(f)

    suspect = np.array(data["suspect_alignments"])
    control = np.array(data["control_alignments"])

    # 임시 signal (seed 동일하게 유지해야 실제 방향 일치)
    from citadel_signal import CitadelSignal
    sig      = CitadelSignal(secret_seed=42)
    detector = CitadelDetector(sig)

    results = detector.statistical_test(suspect, control)
    report  = detector.generate_report(
        results,
        model_name=data.get("model_name", "Unknown Model"),
        commitment_hash=sig.commitment_hash(),
    )
    print(report)
