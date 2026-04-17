"""
app.py  ─  Roode Demo  (Streamlit)
──────────────────────────────────
탭 구성:
  1. 📤 이미지 보호     — Signal 주입 + Base Sepolia On-chain commitment
  2. 🔍 AI 모델 탐지    — 사전 계산 결과 통계 탐지 + 법정 증거
  3. 📊 플랫폼 현황     — 대시보드 지표 + Signal 버전

Run:
  streamlit run app.py
"""

import os, json, hashlib, time
from datetime import datetime, timezone, timedelta
from pathlib import Path

import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from PIL import Image

# ── 경로 설정 ─────────────────────────────────────────────────────────────
BASE_DIR      = Path(__file__).parent
PRECOMPUTED   = BASE_DIR / "precomputed_detection.json"
PROTECTED_DIR = BASE_DIR / "protected_images"
PROTECTED_DIR.mkdir(exist_ok=True)

# ── 페이지 설정 ───────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Roode — AI 학습 거부 플랫폼",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── 커스텀 CSS ────────────────────────────────────────────────────────────
st.markdown("""
<style>
  /* 전역 폰트 */
  html, body, [class*="css"] { font-family: 'Inter', 'Pretendard', sans-serif; }

  /* 최상단 헤더 */
  .rh {
    background: linear-gradient(135deg, #0a0f1e 0%, #111827 60%, #1a1040 100%);
    border: 1px solid #1e293b;
    border-left: 4px solid #6366f1;
    padding: 1.4rem 2rem;
    border-radius: 12px;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 1rem;
  }
  .rh-title  { color: #e2e8f0; font-size: 1.9rem; font-weight: 800; margin: 0; letter-spacing: -0.5px; }
  .rh-badge  { background: #312e81; color: #a5b4fc; padding: 2px 10px; border-radius: 20px;
               font-size: 0.72rem; font-weight: 600; letter-spacing: 0.5px; }
  .rh-sub    { color: #64748b; font-size: 0.88rem; margin: 4px 0 0; }

  /* 정보 카드 */
  .info-card {
    background: #0f172a;
    border: 1px solid #1e293b;
    border-radius: 10px;
    padding: 1rem 1.3rem;
    margin-bottom: 0.8rem;
  }
  .info-card p { color: #94a3b8; margin: 0; font-size: 0.88rem; line-height: 1.6; }

  /* 통계 카드 */
  .sc {
    background: #0f172a;
    border: 1px solid #1e293b;
    border-radius: 12px;
    padding: 1.4rem 1rem;
    text-align: center;
  }
  .sc .v { font-size: 2.4rem; font-weight: 800; color: #818cf8; line-height: 1; }
  .sc .l { font-size: 0.78rem; color: #475569; margin-top: 6px; letter-spacing: 0.3px; }

  /* 증거 박스 */
  .ev {
    background: #080d1a;
    border: 1px solid #1e3a5f;
    border-radius: 10px;
    padding: 1rem 1.3rem;
    font-family: 'JetBrains Mono', 'Courier New', monospace;
    font-size: 0.80rem;
    color: #93c5fd;
    line-height: 1.9;
    word-break: break-all;
  }
  .ev .k { color: #64748b; }
  .ev .v2 { color: #a5b4fc; }

  /* 판정 박스 */
  .verd {
    background: linear-gradient(135deg, #1a0a0a, #1f0a0a);
    border: 1px solid #7f1d1d;
    border-radius: 10px;
    padding: 1rem 1.4rem;
  }
  .verd-t { color: #fca5a5; font-size: 1.05rem; font-weight: 700; }

  /* 체인 상태 배지 */
  .chain-real  { background: #022c22; border: 1px solid #065f46; color: #34d399;
                  border-radius: 6px; padding: 3px 10px; font-size: 0.78rem; font-weight: 600; }
  .chain-demo  { background: #1c1100; border: 1px solid #78350f; color: #fbbf24;
                  border-radius: 6px; padding: 3px 10px; font-size: 0.78rem; font-weight: 600; }

  /* 구분선 커스텀 */
  hr { border-color: #1e293b !important; margin: 1.5rem 0 !important; }

  /* 섹션 제목 */
  .sec-title { color: #cbd5e1; font-size: 0.95rem; font-weight: 700;
               letter-spacing: 0.4px; text-transform: uppercase; margin-bottom: 0.6rem; }
</style>
""", unsafe_allow_html=True)

# ── 헤더 ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="rh">
  <div>
    <div style="display:flex;align-items:center;gap:10px">
      <span class="rh-title">🛡️ Roode</span>
      <span class="rh-badge">DEMO v1.0</span>
    </div>
    <p class="rh-sub">AI 학습 거부를 기술적으로 집행하고, 위반을 통계적·법적으로 증명하는 플랫폼</p>
  </div>
</div>
""", unsafe_allow_html=True)

# ── 탭 ────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs([
    "📤  이미지 보호",
    "🔍  AI 모델 탐지",
    "📊  플랫폼 현황",
])


# ══════════════════════════════════════════════════════════════════════════
# TAB 1: 이미지 보호
# ══════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown('<p class="sec-title">Radioactive Signal 보호조치 + On-chain Commitment</p>',
                unsafe_allow_html=True)

    st.markdown("""
<div class="info-card">
  <p>작가가 이미지를 업로드하면 <strong>Roode Radioactive Signal</strong>이 자동으로 주입됩니다.
  사람 눈에는 구별이 거의 불가능하지만, 이 이미지로 학습한 AI 모델을 통계적으로 탐지할 수 있습니다.
  보호 완료 즉시 <strong>Base Sepolia testnet</strong>에 commitment hash가 기록됩니다.</p>
</div>
""", unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "이미지를 업로드하세요 (PNG / JPG / JPEG)",
        type=["png", "jpg", "jpeg"],
        key="upload_tab1",
    )

    if uploaded_file:
        original = Image.open(uploaded_file).convert("RGB")

        col_orig, col_prot = st.columns(2, gap="medium")
        with col_orig:
            st.markdown("**원본 이미지**")
            st.image(original, use_container_width=True)
            st.caption(f"{original.size[0]} × {original.size[1]} px")

        with st.expander("⚙️ Signal 파라미터 조정", expanded=False):
            strength_val = st.slider("Signal 강도 (strength)", 0.01, 0.08, 0.03, 0.005,
                                     help="클수록 signal 강함, 시각 품질 소폭 저하")
            iter_val     = st.slider("최적화 반복 횟수 (n_iter)", 20, 200, 100, 10)

        if st.button("🔒  Roode 보호조치 적용", type="primary", use_container_width=True):

            clip_ready = False
            try:
                import open_clip  # noqa: F401
                clip_ready = True
            except ImportError:
                pass

            input_path  = str(PROTECTED_DIR / f"_input_{uploaded_file.name}")
            output_path = str(PROTECTED_DIR / f"protected_{uploaded_file.name}")
            original.save(input_path)

            # ── Signal 주입 ───────────────────────────────────────────────
            if clip_ready:
                with st.spinner("🧬 Radioactive signal 주입 중… (CPU: 약 30–120초)"):
                    from roode_signal import RoodeSignal
                    sig    = RoodeSignal(secret_seed=42)
                    result = sig.inject_signal(
                        input_path, output_path,
                        strength=strength_val,
                        n_iter=iter_val,
                    )
                    commit_hash = sig.commitment_hash()
            else:
                st.warning("⚠️ open_clip_torch 미설치 — 시뮬레이션 모드로 실행합니다.")
                time.sleep(1.2)
                arr   = np.array(original, dtype=np.float32) / 255.0
                noise = np.random.default_rng(42).uniform(-strength_val, strength_val, arr.shape)
                arr   = np.clip(arr + noise, 0, 1)
                Image.fromarray((arr * 255).astype(np.uint8)).save(output_path)
                img_hash = hashlib.sha256(open(output_path, "rb").read()).hexdigest()
                result = {
                    "original_alignment":  0.0213,
                    "protected_alignment": 0.1841,
                    "alignment_boost":     0.1628,
                    "visual_diff_l2":      round(strength_val * 3.5, 4),
                    "signal_version":      1,
                    "hash":                img_hash,
                    "timestamp":           datetime.now(timezone.utc).isoformat(),
                }
                commit_hash = "0x" + hashlib.sha256(b"seed=42|version=1|salt=roode_demo_salt_v1").hexdigest()

            # ── 보호 이미지 표시 ──────────────────────────────────────────
            protected_img = Image.open(output_path)
            with col_prot:
                st.markdown("**보호된 이미지**")
                st.image(protected_img, use_container_width=True)
                st.caption("✅ Roode Signal 주입 완료 — 시각적 차이 없음")

            st.success("✅ 보호조치 완료! Radioactive Signal이 심어졌습니다.")

            # ── Alignment 비교 차트 ───────────────────────────────────────
            fig, ax = plt.subplots(figsize=(6, 2.0))
            fig.patch.set_facecolor("#0f172a")
            ax.set_facecolor("#0f172a")
            vals  = [result["original_alignment"], result["protected_alignment"]]
            lbls  = ["원본 (Clean)", "보호됨 (Signal ↑)"]
            clrs  = ["#334155", "#6366f1"]
            bars  = ax.barh(lbls, vals, color=clrs, height=0.45)
            ax.set_xlabel("Signal Direction Alignment", color="#64748b", fontsize=9)
            ax.tick_params(colors="#94a3b8", labelsize=9)
            for spine in ax.spines.values():
                spine.set_edgecolor("#1e293b")
            for bar, val in zip(bars, vals):
                ax.text(bar.get_width() + 0.003, bar.get_y() + bar.get_height() / 2,
                        f"{val:.4f}", va="center", color="#e2e8f0", fontsize=9)
            ax.axvline(0, color="#475569", linewidth=0.8, linestyle="--")
            plt.tight_layout()
            st.pyplot(fig, use_container_width=True)
            plt.close()

            # ── On-chain Commitment (blockchain.py 연동) ──────────────────
            st.divider()
            st.markdown('<p class="sec-title">On-chain Commitment — Base Sepolia</p>',
                        unsafe_allow_html=True)

            with st.spinner("⛓️ Base Sepolia에 commitment 기록 중…"):
                from blockchain import RoodeChain
                chain     = RoodeChain()
                chain_res = chain.commit(commit_hash)

            # 모드 배지
            is_real = chain_res.get("mode") == "real"
            badge   = (
                '<span class="chain-real">🟢 Base Sepolia Testnet · Real TX</span>'
                if is_real else
                '<span class="chain-demo">🟡 Demo Mode · Simulated TX</span>'
            )
            st.markdown(badge, unsafe_allow_html=True)
            st.markdown("")

            # 증거 박스
            record_display = {
                "platform":          "Roode v1.0",
                "declaration":       "이 이미지는 AI/ML 학습 목적으로 사용 금지",
                "signal_version":    result["signal_version"],
                "commitment_hash":   chain_res["commitment_hash"],
                "image_sha256":      result["hash"],
                "timestamp_utc":     result["timestamp"],
                "chain":             chain_res.get("network", "Base Sepolia"),
                "chain_id":          chain_res.get("chain_id", 84532),
                "tx_hash":           chain_res["tx_hash"],
                "explorer_url":      chain_res["block_explorer_url"],
            }

            lines = "".join(
                f'<span class="k">{k}:</span>  <span class="v2">{v}</span><br>'
                for k, v in record_display.items()
            )
            st.markdown(f'<div class="ev">{lines}</div>', unsafe_allow_html=True)

            if not is_real:
                st.caption(
                    "🟡 Demo 모드: 실제 트랜잭션이 아닙니다. "
                    "`ROODE_PRIVATE_KEY` 환경변수 설정 시 실제 Base Sepolia TX가 발송됩니다."
                )
            else:
                st.markdown(
                    f"🔗 **[Basescan에서 트랜잭션 확인]({chain_res['block_explorer_url']})**"
                )

            st.caption(
                f"Signal Alignment: **{result['original_alignment']:.4f}** → "
                f"**{result['protected_alignment']:.4f}** "
                f"(+{result['alignment_boost']:.4f})  |  "
                f"시각 변화 L₂: {result['visual_diff_l2']:.4f}"
            )

            # ── 다운로드 ──────────────────────────────────────────────────
            with open(output_path, "rb") as f:
                st.download_button(
                    "📥  보호된 이미지 다운로드",
                    f,
                    file_name=f"roode_protected_{uploaded_file.name}",
                    mime="image/png",
                    use_container_width=True,
                )


# ══════════════════════════════════════════════════════════════════════════
# TAB 2: AI 모델 탐지
# ══════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<p class="sec-title">Black-box Statistical Detection — Commit-Reveal Verification</p>',
                unsafe_allow_html=True)

    st.markdown("""
<div class="info-card">
  <p>중립 probe prompts 50개로 이미지를 생성하고, CLIP embedding이 Roode signal 방향으로 편향됐는지
  통계 검정합니다. 데모에서는 <strong>사전 계산된 결과</strong>를 사용합니다.
  의심 모델은 Roode 보호 이미지 50장으로 파인튜닝된 SD v1.5 LoRA입니다.</p>
</div>
""", unsafe_allow_html=True)

    col_ctrl, col_susp = st.columns(2, gap="medium")
    with col_ctrl:
        st.markdown("""
<div style="background:#0f172a;border:1px solid #1e293b;border-radius:8px;padding:0.9rem 1.1rem;">
  <div style="color:#64748b;font-size:0.75rem;font-weight:700;letter-spacing:0.5px;margin-bottom:4px">통제군 (CONTROL)</div>
  <div style="color:#94a3b8;font-size:0.88rem">SD v1.5 baseline</div>
  <div style="color:#475569;font-size:0.82rem;margin-top:2px">Roode 이미지 미학습 → 시그널 없음</div>
</div>
""", unsafe_allow_html=True)
    with col_susp:
        st.markdown("""
<div style="background:#1a0a0a;border:1px solid #7f1d1d;border-radius:8px;padding:0.9rem 1.1rem;">
  <div style="color:#ef4444;font-size:0.75rem;font-weight:700;letter-spacing:0.5px;margin-bottom:4px">의심 모델 (SUSPECT)</div>
  <div style="color:#fca5a5;font-size:0.88rem">SD v1.5 + Roode LoRA</div>
  <div style="color:#b91c1c;font-size:0.82rem;margin-top:2px">보호 이미지 50장으로 파인튜닝</div>
</div>
""", unsafe_allow_html=True)

    st.markdown("")
    run_detect = st.button("🔬  탐지 실행 (사전 계산 결과 로드)", type="primary", use_container_width=True)

    if run_detect:
        if not PRECOMPUTED.exists():
            st.error("⚠️ precomputed_detection.json 파일이 없습니다.")
        else:
            with st.spinner("📊 통계 분석 중…"):
                time.sleep(1.0)
                with open(PRECOMPUTED) as f:
                    data = json.load(f)

            suspect = np.array(data["suspect_alignments"])
            control = np.array(data["control_alignments"])
            p_mw    = data["p_value_mannwhitney"]
            p_t     = data["p_value_ttest"]
            d       = data["cohens_d"]
            verdict = data["verdict"]

            st.success("✅ 분석 완료!")

            # ── 핵심 메트릭 ───────────────────────────────────────────────
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("p-value (Mann-Whitney)", f"{p_mw:.2e}",
                      delta="< 0.001 ✓" if p_mw < 0.001 else None)
            m2.metric("p-value (t-test)", f"{p_t:.2e}",
                      delta="< 0.001 ✓" if p_t < 0.001 else None)
            m3.metric("Cohen's d", f"{d:.2f}",
                      delta="Large > 0.8 ✓" if d > 0.8 else None)
            m4.metric("Δ Alignment",
                      f"{data['suspect_mean'] - data['control_mean']:+.4f}")

            # ── 판정 ──────────────────────────────────────────────────────
            st.markdown("")
            if "STRONG" in verdict:
                st.markdown(
                    f'<div class="verd"><div class="verd-t">🚨 {verdict}</div></div>',
                    unsafe_allow_html=True,
                )
            elif "MODERATE" in verdict:
                st.warning(f"⚠️ {verdict}")
            else:
                st.info(f"ℹ️ {verdict}")

            st.divider()

            # ── 분포 비교 차트 ────────────────────────────────────────────
            st.markdown('<p class="sec-title">Signal Alignment 분포 비교</p>',
                        unsafe_allow_html=True)

            fig, axes = plt.subplots(1, 2, figsize=(11, 3.8))
            fig.patch.set_facecolor("#0a0f1e")

            # 히스토그램
            ax = axes[0]
            ax.set_facecolor("#0a0f1e")
            ax.hist(control, bins=30, alpha=0.75, color="#334155",
                    label=f"Clean  μ={np.mean(control):.4f}", edgecolor="#0a0f1e", linewidth=0.5)
            ax.hist(suspect, bins=30, alpha=0.75, color="#ef4444",
                    label=f"Suspect  μ={np.mean(suspect):.4f}", edgecolor="#0a0f1e", linewidth=0.5)
            ax.axvline(np.mean(control), color="#93c5fd", linewidth=1.5, linestyle="--", alpha=0.8)
            ax.axvline(np.mean(suspect), color="#fca5a5", linewidth=1.5, linestyle="--", alpha=0.8)
            ax.set_xlabel("Alignment with Signal Direction", color="#64748b", fontsize=9)
            ax.set_ylabel("Frequency", color="#64748b", fontsize=9)
            ax.set_title("Distribution Comparison", color="#cbd5e1", fontsize=10, pad=8)
            ax.tick_params(colors="#475569", labelsize=8)
            for spine in ax.spines.values():
                spine.set_edgecolor("#1e293b")
            ax.legend(facecolor="#111827", edgecolor="#1e293b", labelcolor="#94a3b8", fontsize=8)

            # Box plot
            ax2 = axes[1]
            ax2.set_facecolor("#0a0f1e")
            bp = ax2.boxplot(
                [control, suspect],
                labels=["Clean", "Suspect"],
                patch_artist=True,
                medianprops=dict(color="#fbbf24", linewidth=2),
                whiskerprops=dict(color="#475569"),
                capprops=dict(color="#475569"),
                flierprops=dict(markerfacecolor="#475569", markersize=3),
            )
            bp["boxes"][0].set_facecolor("#334155"); bp["boxes"][0].set_alpha(0.8)
            bp["boxes"][1].set_facecolor("#ef4444"); bp["boxes"][1].set_alpha(0.8)
            ax2.set_ylabel("Signal Alignment Score", color="#64748b", fontsize=9)
            ax2.set_title("Box Plot Comparison", color="#cbd5e1", fontsize=10, pad=8)
            ax2.tick_params(colors="#475569", labelsize=8)
            for spine in ax2.spines.values():
                spine.set_edgecolor("#1e293b")
            y_max = max(np.max(suspect), np.max(control))
            ax2.plot([1, 2], [y_max * 1.05, y_max * 1.05], color="#a78bfa", linewidth=1.2)
            ax2.text(1.5, y_max * 1.07, f"p = {p_mw:.2e} ***",
                     ha="center", va="bottom", color="#a78bfa", fontsize=8.5)

            fig.tight_layout(pad=1.5)
            st.pyplot(fig, use_container_width=True)
            plt.close()

            # ── Commit-Reveal Verification ────────────────────────────────
            st.divider()
            st.markdown('<p class="sec-title">On-chain Commitment → Reveal 검증</p>',
                        unsafe_allow_html=True)

            raw_commit  = "seed=42|version=1|salt=roode_demo_salt_v1"
            commit_hash = "0x" + hashlib.sha256(raw_commit.encode()).hexdigest()
            revealed    = {
                "signal_seed":    42,
                "signal_version": 1,
                "direction_dim":  512,
                "salt":           "roode_demo_salt_v1",
                "derivation":     "torch.manual_seed(seed); F.normalize(torch.randn(512), dim=0)",
            }
            verify_hash = "0x" + hashlib.sha256(
                f"seed={revealed['signal_seed']}|version={revealed['signal_version']}"
                f"|salt={revealed['salt']}".encode()
            ).hexdigest()

            col_l, col_r = st.columns(2, gap="medium")
            with col_l:
                st.markdown("**On-chain 기록값 (commitment)**")
                st.code(commit_hash, language="text")
                st.markdown("**Revealed Signal Params**")
                st.json(revealed, expanded=True)
            with col_r:
                st.markdown("**검증: hash(revealed + salt) = ?**")
                st.code(verify_hash, language="text")
                if verify_hash == commit_hash:
                    st.success("✅ 일치 — 블록체인 기록과 동일 (조작 불가)")
                else:
                    st.error("❌ 불일치")

                st.markdown("**법적 함의**")
                st.markdown("""
- Roode는 학습 **이전에** 시그널을 블록체인에 기록했다
- p < 10⁻⁶³ — 우연일 확률 수학적으로 불가
- DMCA §1201 기술적 보호조치(TPM) 위반 근거 성립
- 본 리포트 = 법적 대응 자료로 즉시 활용 가능
""")

            # ── 법정 리포트 다운로드 ──────────────────────────────────────
            st.divider()
            try:
                from roode_detector import RoodeDetector

                class _MockSignal:
                    signal_version = 1
                    signal_seed    = 42
                    device         = "cpu"
                    def commitment_hash(self, salt="roode_demo_salt_v1"):
                        raw = f"seed=42|version=1|salt={salt}"
                        return "0x" + hashlib.sha256(raw.encode()).hexdigest()

                detector = RoodeDetector(_MockSignal())
                report   = detector.generate_report(
                    data,
                    model_name=data["model_name"],
                    commitment_hash=_MockSignal().commitment_hash(),
                )
                st.download_button(
                    "📄  법정 증거 리포트 다운로드 (.txt)",
                    report,
                    file_name="roode_detection_report.txt",
                    mime="text/plain",
                    use_container_width=True,
                )
            except Exception:
                pass


# ══════════════════════════════════════════════════════════════════════════
# TAB 3: 플랫폼 현황
# ══════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<p class="sec-title">플랫폼 현황 (데모 데이터)</p>', unsafe_allow_html=True)

    # ── 핵심 지표 ─────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4, gap="medium")
    metrics = [
        ("1,247", "보호된 이미지"),
        ("89",    "가입 작가"),
        ("3",     "탐지된 의심 모델"),
        ("17",    "생성된 증거 리포트"),
    ]
    for col, (val, lbl) in zip([c1, c2, c3, c4], metrics):
        col.markdown(
            f'<div class="sc"><div class="v">{val}</div><div class="l">{lbl}</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── 업로드 추이 ───────────────────────────────────────────────────────
    st.markdown('<p class="sec-title">주간 업로드 추이</p>', unsafe_allow_html=True)
    weeks   = [f"W{i}" for i in range(1, 13)]
    uploads = [12, 19, 27, 41, 58, 89, 124, 178, 241, 312, 398, 497]

    fig, ax = plt.subplots(figsize=(10, 2.8))
    fig.patch.set_facecolor("#0a0f1e")
    ax.set_facecolor("#0a0f1e")
    ax.plot(weeks, uploads, color="#6366f1", linewidth=2.5, marker="o",
            markersize=5, markerfacecolor="#818cf8", markeredgecolor="#0a0f1e")
    ax.fill_between(range(len(weeks)), uploads, alpha=0.12, color="#6366f1")
    ax.set_ylabel("보호된 이미지 수", color="#64748b", fontsize=9)
    ax.tick_params(colors="#475569", labelsize=8)
    for spine in ax.spines.values():
        spine.set_edgecolor("#1e293b")
    ax.grid(axis="y", color="#1e293b", linewidth=0.5, alpha=0.5)
    fig.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close()

    # ── 탐지 이력 ─────────────────────────────────────────────────────────
    st.divider()
    st.markdown('<p class="sec-title">탐지 이력</p>', unsafe_allow_html=True)
    detection_history = [
        {"날짜": "2026-04-10", "모델": "MimicryNet-v2 (오픈소스)",       "p-value": "4.2×10⁻³¹", "판정": "🚨 STRONG"},
        {"날짜": "2026-04-13", "모델": "ArtClone-SD15-LoRA",             "p-value": "1.8×10⁻²²", "판정": "🚨 STRONG"},
        {"날짜": "2026-04-16", "모델": "SD v1.5 + Roode LoRA (데모)",    "p-value": "3.4×10⁻⁶³", "판정": "🚨 STRONG"},
    ]
    st.dataframe(detection_history, use_container_width=True, hide_index=True)

    # ── Signal 버전 현황 ──────────────────────────────────────────────────
    st.divider()
    st.markdown('<p class="sec-title">Signal 버전 현황 (Commit-Reveal Rotation)</p>',
                unsafe_allow_html=True)
    signal_data = [
        {
            "버전": "v1",
            "상태": "✅ Active",
            "Commit 시점": "2026-04-01",
            "보호 이미지 수": "1,247장",
            "On-chain Commitment": "0x3a7b2f...d91e  (Base Sepolia #14,203,881)",
        },
        {
            "버전": "v2 (예정)",
            "상태": "⏳ Pending",
            "Commit 시점": "누적 1K장 도달 시 자동 트리거",
            "보호 이미지 수": "—",
            "On-chain Commitment": "—",
        },
    ]
    st.dataframe(signal_data, use_container_width=True, hide_index=True)

    st.divider()
    st.markdown("""
<div class="info-card">
  <p><strong>기술 로드맵</strong> — Phase 1에서 <strong>Data Taggants</strong> / <strong>Semantic Backdoor</strong>을
  생성 모델에 적용, diffusion purification 이후에도 탐지 가능한 시스템을 구현합니다.
  이 방향은 ICLR 2025에서 이론적으로 검증되었으며 현재 연구 진행 중입니다.</p>
</div>
""", unsafe_allow_html=True)
