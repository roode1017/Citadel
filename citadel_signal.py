"""
citadel_signal.py
───────────────
Citadel Radioactive Signal 주입 모듈.

CLIP embedding direction perturbation을 이용해
시각적으로 거의 구분 불가능하지만,
학습에 사용된 모델에서 통계적으로 탐지 가능한 signal을 심는다.

참고: Sablayrolles et al. (2020), Radioactive data: tracing through training, ICML.
"""

import json
import hashlib
import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image
from datetime import datetime, timezone

try:
    import open_clip
    CLIP_AVAILABLE = True
except ImportError:
    CLIP_AVAILABLE = False

# ── CLIP 정규화 파라미터 (ViT-B-32 / OpenAI pretrained) ──────────────────
CLIP_MEAN = torch.tensor([0.48145466, 0.4578275,  0.40821073])
CLIP_STD  = torch.tensor([0.26862954, 0.26130258, 0.27577711])


class CitadelSignal:
    """
    Citadel 플랫폼의 Radioactive Signal 주입기.

    secret_seed로 platform-wide signal direction을 생성한다.
    실제 프로덕션: per-version key + on-chain commit-reveal rotation.
    """

    def __init__(self, secret_seed=42, device=None):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")

        if not CLIP_AVAILABLE:
            raise ImportError(
                "open_clip_torch 가 설치되지 않았습니다.\n"
                "  pip install open-clip-torch"
            )

        # CLIP 모델 로드 (ViT-B-32, OpenAI pretrained)
        self.model, _, self.preprocess = open_clip.create_model_and_transforms(
            "ViT-B-32", pretrained="openai"
        )
        self.model = self.model.to(self.device).eval()
        self.embedding_dim = 512

        # Citadel 고유 signal direction (비밀 시드 / v1)
        torch.manual_seed(secret_seed)
        self.signal_direction = F.normalize(
            torch.randn(self.embedding_dim, device=self.device), dim=0
        )
        self.signal_version = 1
        self.signal_seed    = secret_seed

    # ─── 내부 헬퍼 ────────────────────────────────────────────────────────

    def _to_clip_space(self, t):
        """[0,1] 텐서 → CLIP 정규화 공간"""
        mean = CLIP_MEAN.view(1, 3, 1, 1).to(self.device)
        std  = CLIP_STD.view(1, 3, 1, 1).to(self.device)
        return (t - mean) / std

    def _from_clip_space(self, t):
        """CLIP 정규화 공간 → [0,1] 텐서"""
        mean = CLIP_MEAN.view(1, 3, 1, 1).to(self.device)
        std  = CLIP_STD.view(1, 3, 1, 1).to(self.device)
        return t * std + mean

    def _encode(self, clip_tensor):
        """CLIP 정규화 텐서 → L2-normalized embedding"""
        emb = self.model.encode_image(clip_tensor)
        return F.normalize(emb, dim=-1)

    def _to_pil(self, clip_tensor):
        """CLIP 정규화 텐서 → PIL Image"""
        img01 = self._from_clip_space(clip_tensor).clamp(0.0, 1.0)
        arr   = img01.squeeze(0).permute(1, 2, 0).cpu().numpy()
        return Image.fromarray((arr * 255).astype(np.uint8))

    # ─── 핵심 API ─────────────────────────────────────────────────────────

    def inject_signal(
        self,
        image_path,
        output_path,
        strength=0.03,
        n_iter=100,
        lr=0.01,
    ):
        """
        이미지에 Citadel radioactive signal을 심는다.

        Parameters
        ----------
        image_path  : 원본 이미지 경로
        output_path : 보호 이미지 저장 경로
        strength    : pixel-space L-inf 제약 (클수록 signal 강 / 시각 변화 증가)
        n_iter      : 최적화 반복 수
        lr          : Adam lr

        Returns
        -------
        dict: alignment 변화량, 해시, 타임스탬프 등
        """
        # 1. 원본 이미지 로드 (고해상도 유지)
        image      = Image.open(image_path).convert("RGB")
        orig_w, orig_h = image.size                                          # 원본 해상도 저장

        # CLIP용 224×224 텐서 (gradient 계산에만 사용)
        img_clip   = self.preprocess(image).unsqueeze(0).to(self.device)   # [1,3,224,224]
        img_01_224 = self._from_clip_space(img_clip).clamp(0.0, 1.0)       # [0,1], 224×224

        # 원본 해상도 텐서 ([0,1], H×W)
        import torchvision.transforms.functional as TF
        img_orig   = TF.to_tensor(image).unsqueeze(0).to(self.device)      # [1,3,H,W]

        # 2. 원본 alignment 측정
        with torch.no_grad():
            orig_align = (self._encode(img_clip) @ self.signal_direction).item()

        # 3. Perturbation 최적화 — 224×224 CLIP 공간에서 delta 학습
        delta     = torch.zeros_like(img_01_224, requires_grad=True)
        optimizer = torch.optim.Adam([delta], lr=lr)

        for _ in range(n_iter):
            perturbed_01   = (img_01_224 + delta).clamp(0.0, 1.0)
            perturbed_clip = self._to_clip_space(perturbed_01)

            emb        = self._encode(perturbed_clip)
            alignment  = (emb @ self.signal_direction).mean()
            visual_reg = torch.norm(delta) * 0.1      # 시각 품질 보존

            loss = -alignment + visual_reg
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            with torch.no_grad():
                delta.clamp_(-strength, strength)      # L-inf 제약

        # 4. delta를 원본 해상도로 upsample → 원본 이미지에 적용
        with torch.no_grad():
            import torch.nn.functional as F_interp
            delta_orig = F_interp.interpolate(
                delta.detach(),
                size=(orig_h, orig_w),
                mode="bilinear",
                align_corners=False,
            )
            final_orig = (img_orig + delta_orig).clamp(0.0, 1.0)           # 원본 해상도 + signal

            # alignment 측정은 224×224 CLIP으로
            final_224  = (img_01_224 + delta).clamp(0.0, 1.0)
            final_clip = self._to_clip_space(final_224)
            prot_align = (self._encode(final_clip) @ self.signal_direction).item()
            visual_l2  = torch.norm(delta).item()

        # 5. 원본 해상도로 저장
        arr = final_orig.squeeze(0).permute(1, 2, 0).cpu().numpy()
        Image.fromarray((arr * 255).astype(np.uint8)).save(output_path)

        # 5. SHA-256 해시
        with open(output_path, "rb") as f:
            img_hash = hashlib.sha256(f.read()).hexdigest()

        return {
            "original_alignment":  round(orig_align, 6),
            "protected_alignment": round(prot_align, 6),
            "alignment_boost":     round(prot_align - orig_align, 6),
            "visual_diff_l2":      round(visual_l2, 6),
            "signal_version":      self.signal_version,
            "hash":                img_hash,
            "timestamp":           datetime.now(timezone.utc).isoformat(),
        }

    def alignment_score(self, image):
        """PIL Image 의 signal direction alignment 점수 반환"""
        t = self.preprocess(image).unsqueeze(0).to(self.device)
        with torch.no_grad():
            emb = self._encode(t)
        return (emb @ self.signal_direction).item()

    def commitment_hash(self, salt="citadel_demo_salt_v1"):
        """
        On-chain commitment 시뮬레이션.
        실제: signal params + salt 를 SHA-256 → Base Sepolia 기록.
        """
        raw = f"seed={self.signal_seed}|version={self.signal_version}|salt={salt}"
        return "0x" + hashlib.sha256(raw.encode()).hexdigest()


# ── CLI ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python citadel_signal.py <input_image> <output_image>")
        sys.exit(1)
    sig    = CitadelSignal()
    result = sig.inject_signal(sys.argv[1], sys.argv[2])
    print(json.dumps(result, indent=2))
