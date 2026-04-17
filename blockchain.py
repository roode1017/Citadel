"""
blockchain.py
─────────────
Citadel On-chain Commitment 모듈.

Base Sepolia testnet에 signal commitment hash를 기록하고
트랜잭션 해시와 block explorer 링크를 반환한다.

Chain  : Base Sepolia (Chain ID 84532)
RPC    : https://sepolia.base.org
Explorer: https://sepolia.basescan.org
"""

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

# ── .env 파일 자동 로드 ───────────────────────────────────────────────────
def _load_env():
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, val = line.partition("=")
                os.environ.setdefault(key.strip(), val.strip())

_load_env()

# ── web3.py import (선택적) ────────────────────────────────────────────────
try:
    from web3 import Web3
    from eth_account import Account
    WEB3_AVAILABLE = True
except ImportError:
    WEB3_AVAILABLE = False

# ── Base Sepolia 설정 ─────────────────────────────────────────────────────
BASE_SEPOLIA_RPC     = "https://sepolia.base.org"
BASE_SEPOLIA_CHAIN   = 84532
BASE_SEPOLIA_EXPLORER = "https://sepolia.basescan.org"


class CitadelChain:
    """
    Citadel On-chain Commitment 클라이언트.

    두 가지 모드:
    1. REAL 모드  : CITADEL_PRIVATE_KEY 환경변수 있으면 실제 TX 발송
    2. DEMO 모드  : 없으면 deterministic fake TX (시연용, 명시적으로 표기)
    """

    def __init__(self, rpc_url=BASE_SEPOLIA_RPC, private_key=None):
        self.rpc_url    = rpc_url
        self.chain_id   = BASE_SEPOLIA_CHAIN
        self.explorer   = BASE_SEPOLIA_EXPLORER
        self.private_key = private_key or os.environ.get("CITADEL_PRIVATE_KEY")

        self.real_mode = False
        self.w3        = None
        self.account   = None

        if WEB3_AVAILABLE and self.private_key:
            try:
                self.w3      = Web3(Web3.HTTPProvider(rpc_url))
                self.account = Account.from_key(self.private_key)
                # 연결 확인
                if self.w3.is_connected():
                    self.real_mode = True
            except Exception:
                self.real_mode = False

    # ─── 공개 API ─────────────────────────────────────────────────────────

    def commit(self, commitment_hash: str, salt: str = "citadel_v1") -> dict:
        """
        On-chain commitment 기록.

        Parameters
        ----------
        commitment_hash : "0x..." 형식의 SHA-256 해시
        salt            : 선택적 salt (기록용)

        Returns
        -------
        dict: tx_hash, block_explorer_url, mode, timestamp 등
        """
        return self._send_real_tx(commitment_hash, salt)

    def verify_commitment(self, signal_seed: int, signal_version: int,
                          salt: str, on_chain_hash: str) -> bool:
        """Commit-reveal 검증: reveal된 params → hash → on-chain hash 비교"""
        raw = f"seed={signal_seed}|version={signal_version}|salt={salt}"
        computed = "0x" + hashlib.sha256(raw.encode()).hexdigest()
        return computed == on_chain_hash

    @property
    def mode_label(self):
        return "🟢 Base Sepolia Testnet (Real)" if self.real_mode else "🟡 Demo Mode (Simulated)"

    # ─── 내부 메서드 ──────────────────────────────────────────────────────

    def _send_real_tx(self, commitment_hash: str, salt: str) -> dict:
        """실제 Base Sepolia 트랜잭션 발송"""
        try:
            # data = commitment_hash를 UTF-8 hex로 인코딩
            data_hex = commitment_hash.encode("utf-8").hex()

            nonce    = self.w3.eth.get_transaction_count(self.account.address)
            gas_price = self.w3.eth.gas_price

            tx = {
                "chainId": self.chain_id,
                "nonce":   nonce,
                "to":      self.account.address,  # self-send (데이터 앵커링)
                "value":   0,
                "gas":     30000,
                "gasPrice": gas_price,
                "data":    "0x" + data_hex,
            }

            signed  = self.w3.eth.account.sign_transaction(tx, self.private_key)
            raw     = signed.raw_transaction if hasattr(signed, "raw_transaction") else signed.rawTransaction
            tx_hash = self.w3.eth.send_raw_transaction(raw)
            tx_hex  = tx_hash.hex()

            return {
                "mode":              "real",
                "tx_hash":           tx_hex,
                "block_explorer_url": f"{self.explorer}/tx/{tx_hex}",
                "network":           "Base Sepolia",
                "chain_id":          self.chain_id,
                "from_address":      self.account.address,
                "commitment_hash":   commitment_hash,
                "salt":              salt,
                "timestamp":         datetime.now(timezone.utc).isoformat(),
                "status":            "submitted",
            }

        except Exception as e:
            raise RuntimeError(f"Base Sepolia TX 실패: {e}") from e


# ── CLI ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    chain = CitadelChain()
    print(f"Mode: {chain.mode_label}")

    test_hash = "0x" + hashlib.sha256(b"test_signal_seed=42|version=1|salt=demo").hexdigest()
    result    = chain.commit(test_hash)
    print(json.dumps(result, indent=2, ensure_ascii=False))

    # Commit-reveal 검증 테스트
    verified = chain.verify_commitment(
        signal_seed=42, signal_version=1,
        salt="citadel_demo_salt_v1",
        on_chain_hash="0x" + hashlib.sha256(
            b"seed=42|version=1|salt=citadel_demo_salt_v1"
        ).hexdigest()
    )
    print(f"\nCommit-reveal verification: {'✅ PASS' if verified else '❌ FAIL'}")
