# Roode

## AI 학습 거부를 기술적으로 집행하고, 위반을 통계적·법적으로 증명하는 플랫폼

> *"우리는 선언한다. 기록한다. 그리고 증명할 수 있다."*

---

## 🎯 한 문장 요약

**Roode는 아티스트들이 AI 학습을 집단적으로 거부하고, 그 거부를 블록체인에 기록된 암호학적 보호조치로 집행하며, 위반 시 법적 증거를 생성하는 플랫폼이다.**

---

## 📢 문제 정의 (Problem)

### AI 시대, 아티스트는 무방비 상태다

현재 대규모 AI 이미지 생성 모델들은 **수십억 장의 이미지**를 인터넷에서 무단으로 스크래핑해 학습한다. 아티스트들은:

- **동의 없이** 자신의 작품이 학습 데이터로 사용되고
- **출처 없이** 자신의 화풍이 AI로 재생산되며
- **증거 없이** 법적 대응조차 불가능한 상태다

### 기존 솔루션의 한계

| 기존 도구 | 접근 | 한계 |
|---------|-----|-----|
| `robots.txt` | 크롤러에게 부탁 | 무시하면 그만 |
| Watermark | 출처 표시 | 학습 자체는 못 막음 |
| **Glaze** (U.Chicago) | Style cloaking | 개별 도구, 검증 불가, 뚫림 |
| **Nightshade** (U.Chicago) | Data poisoning | 개별 도구, 증명 기능 없음 |
| Cara | AI 반대 커뮤니티 | 기술적 방어/증명 없음 |

**핵심 공백**:
- 기존 도구는 **개별 작가용** — 혼자 다운로드, 혼자 사용, 혼자 분쟁
- 아무도 **"증명"** 기능 없음 — 내 작품이 학습됐는지 확인 불가
- **법적 증거로서의 보호조치**가 존재하지 않음

---

## 💡 우리의 솔루션 (Solution)

### 핵심 아이디어: Platform-Level Collective Defense + On-chain Evidence

개별 작가 도구가 아니라 **플랫폼 차원의 법적 증거 인프라**를 만든다.

```
┌─────────────────────────────────────────────────────────┐
│ [선언]    이 플랫폼의 모든 콘텐츠는 AI 학습 거부        │
│             ↓                                           │
│ [집행]    모든 업로드에 Roode Signal 자동 주입          │
│             ↓                                           │
│ [기록]    On-chain Commitment (Base L2)                 │
│          · 시그널 버전 commitment hash                  │
│          · 타임스탬프                                   │
│          · 작가 동의                                    │
│             ↓                                           │
│ [탐지]    의심 모델에서 시그널 통계적 검출              │
│             ↓                                           │
│ [증명]    Reveal → 법정 증거 패키지                     │
└─────────────────────────────────────────────────────────┘
```

### 왜 이 접근이 근본적으로 다른가

**"Kim 작가의 그림체를 배꼈다"는 증명하기 매우 어렵다.**
- 스타일은 저작권 보호 대상 아님
- 입증 책임이 작가에게 있음
- 우연한 유사성과 구분 불가

**하지만 "Roode 플랫폼 시그널이 발견됐다 + 우리가 이 시그널을 특정 시점에 먼저 기록했다"는 쉽게 증명된다.**
- 시그널은 Roode만 아는 비밀 방향
- 우연의 일치 확률 수학적으로 극히 낮음 (p<10^-4 이하)
- **블록체인에 사전 기록** → 사후 조작 불가능
- 법적 쟁점이 단순 사실 판단으로 귀결

**쟁점을 "스타일 도용"에서 "우리가 먼저 기록한 보호조치의 무단 우회"로 전환**하는 것이 Roode의 전략적 핵심이다.

---

## 🔐 핵심 혁신: On-chain Commit-Reveal Signal Rotation

### 왜 이 구조인가

**문제**: 시그널이 공개/역공학되면 purification 공격으로 뚫린다.
**해결**: 블록체인에 **commitment hash만 미리 공개**하고, 분쟁 시 **reveal**한다.

### 3단계 메커니즘

```
┌──────────────────────────────────────────────────────────┐
│ Phase 1: Commit (시그널 도입)                            │
│                                                          │
│  Roode 내부: signal_v1_params 생성 (비공개)              │
│  계산:       commitment = hash(signal_v1_params + salt)  │
│  On-chain:   {                                           │
│               version: 1,                                │
│               commitment: 0x3a7b...,                     │
│               timestamp: 2026-04-16T12:00:00Z,           │
│               declaration: "AI 학습 거부 보호조치"       │
│              }                                           │
│                                                          │
│  이후 모든 업로드에 signal_v1 적용                       │
└──────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────┐
│ Phase 2: Rotation (시그널 교체)                          │
│                                                          │
│  누적 이미지 N장 × 2~3 배수 도달 시                      │
│  → signal_v2 생성, 새 commitment on-chain 기록           │
│  → 이후 업로드는 v2 적용                                 │
│  → 기존 이미지는 v1 시그널 그대로 유지 (탐지 가능)       │
└──────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────┐
│ Phase 3: Reveal (분쟁 발생 시)                           │
│                                                          │
│  의심 모델 발견 → Roode 내부 검증                        │
│  → 공식 분쟁 선언                                        │
│  → signal_v1 params 공개 (reveal)                        │
│  → 누구나 검증 가능:                                     │
│     hash(revealed_params + salt) == on-chain commitment  │
│  → 법정 증거: "이 시그널을 Timestamp T에 우리가 정의"    │
│  → 모델 학습 시점 추정 + 무단 사용 증명                  │
└──────────────────────────────────────────────────────────┘
```

### 왜 강력한가

1. **사후 조작 불가능**: Commitment는 블록체인에 불가역 기록
2. **보안 + 투명성 양립**: 평소 비공개, 분쟁 시 완전 공개
3. **지속 가능한 arms race 대응**: 자동 rotation 메커니즘 내장
4. **법적 증거력**: 블록체인 타임스탬프는 chain of custody 확립에 효과적이며, EU eIDAS 2.0 등에서 법적 프레임워크 형성 중

### 로테이션 임계점 (Rotation Threshold)

Radioactive Data 논문 기준: **학습 데이터의 1% 이상 marked 시 탐지 가능**

플랫폼 누적 이미지별 전략:

| 단계 | 누적 이미지 | 방어 가능 공격 | 시그널 전략 |
|-----|-----------|-------------|-----------|
| Early | 100~1,000 | 소규모 LoRA (학습셋 1만 이하) | 단일 v1 운영 |
| Growth | 1,000~10,000 | 중규모 파인튜닝 | v2 rotation 도입 |
| Mature | 10,000+ | 대규모 fine-tuning | 정기 rotation + multi-layer |

각 tier에서 **기존 이미지 × 2~3배** 증가 시 새 버전 commit.

---

## 🔬 기술적 근거 (Technical Foundation)

### 1. Radioactive Data (Sablayrolles et al., 2020, ICML)

**검증된 수치**:
- ImageNet 대규모 벤치마크
- 학습 데이터의 1%만 radioactive 처리되어도 p<10^-4 수준 탐지
- ResNet-18, VGG-16, DenseNet-121 표준 아키텍처 모두에서 작동
- Data augmentation, optimization 랜덤성에 robust

**Roode의 활용**:
- 플랫폼 전체 사용자 데이터 = 학습셋의 1% 이상이면 강력한 증거
- 개인 작가 혼자는 불가능한 수치를 **집단으로** 달성

### 2. Nightshade (Shan et al., 2024, IEEE S&P)

**검증된 수치**:
- Stable Diffusion SDXL 대상으로 100개 미만 poisoned training sample로 특정 prompt 완전 제어
- 포이즌된 50장의 개 이미지만으로도 모델이 비정상 생성물 출력
- 300장이면 "개"가 "고양이"로 분류됨
- 관련 개념(puppy, husky 등)까지 오염 전파

**Roode의 활용**:
- 플랫폼 공통 시그널이 학습되면 모델의 latent space 전반 편향
- 편향을 탐지 근거로 활용

### 3. Memorization Extraction (Carlini et al., 2023, USENIX)

**검증된 결과**:
- Stable Diffusion이 학습 이미지를 near-identical copy로 재생성하는 사례 수백 건 발견
- NYT vs OpenAI 소송에서 실제 법적 증거로 사용

**Roode의 활용**:
- 탐지 파이프라인 보조 증거
- 법적 대응 시 가장 강력한 증거 형태

### 4. LLM Watermark Radioactivity (Sander et al., 2024, NeurIPS)

**검증된 수치**:
- Open-model access에서 p<10^-30, closed-model access에서 p<10^-10 수준 탐지
- 학습 데이터의 1-5%만 워터마킹 돼도 통계적으로 강력히 탐지됨

**Roode의 활용**:
- 이미지 도메인에도 동일 원리 적용 가능성
- 상용 API(black-box)에서도 제한적 탐지 가능성

---

## 🏗️ 시스템 아키텍처

### Layer 1: 선언 (Declaration)
- 플랫폼 이용약관: AI 학습 거부 명시
- 공개 선언문 발표
- Base 체인 smart contract에 영구 기록

### Layer 2: 기술적 집행 (Technical Enforcement)

**현재 구현 (Phase 0):**
- **Primary**: CLIP embedding direction perturbation
  - 일반 LoRA 파인튜닝·표준 augmentation 파이프라인에서 signal 생존 확인
  - 실제 피해 대부분인 소규모 무단 파인튜닝 대응에 유효

**로드맵 (Phase 1-2):**
- **Secondary**: Dataset-level Behavioral Fingerprint
  - Data Taggants 방식 (ICLR 2025, Meta AI): 생성 모델 적용 연구 중
  - Diffusion purification 후에도 모델 행동 패턴으로 학습 사실 증명
  - 블랙박스 API에서도 수학적 보장된 탐지 가능
- **Tertiary**: Semantic Backdoor (DVBW, IEEE TIFS 2023 기반)
  - 픽셀이 아닌 모델이 학습한 연관 패턴으로 지문 형성
  - Diffusion 재생성 이후에도 가중치에 잔존

- 시그널 **commit-reveal rotation** (분기별/누적량별)

### Layer 3: On-chain 증거 기록 (Evidence Recording)

**왜 Base인가**:
- Coinbase 구축 L2, 2025년 L2 수익 지배적 점유
- 소비자 앱과 소셜/아이덴티티 프로토콜의 기본 선택
- EVM 호환 → 전 세계 법적/기술적 인프라 활용
- 거래 수수료 거의 공짜 (업로드마다 기록해도 부담 없음)
- 한국 사용자 온보딩 용이 (Coinbase 브랜드)

**Smart Contract 구조**:
```solidity
contract RoodeRegistry {
    struct SignalCommitment {
        uint256 version;
        bytes32 commitment;  // hash(params + salt)
        uint256 timestamp;
        string declaration;
        bool revealed;
        bytes revealedParams; // 분쟁 시에만 채움
    }
    
    struct ImageRecord {
        bytes32 imageHash;
        uint256 signalVersion;
        uint256 timestamp;
        address artist;
        string consent;
    }
    
    mapping(uint256 => SignalCommitment) public signals;
    mapping(bytes32 => ImageRecord) public images;
    
    function commitSignal(...) external;
    function registerImage(...) external;
    function revealSignal(uint256 version, ...) external onlyDispute;
}
```

### Layer 4: 탐지 서비스 (Detection Service)

| 방식 | 대상 | 방법 | 신뢰도 |
|-----|-----|------|-------|
| White-box | 오픈소스 모델 | 파라미터 직접 분석 | p<10^-30 가능 |
| Black-box | API 모델 | Probe prompt + 통계 검정 | p<0.01 |
| Trap trigger | 극적 증거 필요 시 | 특수 프롬프트 반응 | 시각적 증거 |

**통계 프로토콜**:
1. 중립 프롬프트 500-1,000개로 대량 생성
2. CLIP embedding 추출
3. 모든 활성 시그널 버전과의 정렬 측정
4. 통제군과 Mann-Whitney U test
5. Cohen's d로 effect size 계산
6. Bonferroni 다중 검정 보정

### Layer 5: 리포트 생성 (Reporting)
- 자동 한국어/영어 리포트
- 통계 결과 + 시각화 + on-chain 증거 + reveal된 시그널 파라미터
- DMCA takedown용 표준 양식
- 법적 대응 자료로 즉시 활용 가능

---

## ⚖️ 법적 정당성 (Legal Foundation)

### 방어 논리

1. **계약법 (Contract Law)**
   - 명확한 이용약관: "AI 학습 금지" 사전 고지
   - On-chain 선언문 = 공개적, 불가역 고지
   - 스크래핑 = 계약 위반

2. **DMCA §1201 (미국)**
   - Roode 시그널 = **기술적 보호조치(TPM)**
   - Blockchain-registered TPM = 강력한 법적 지위
   - 우회 행위 자체가 불법

3. **블록체인 증거 admissibility**
   - 블록체인 타임스탬프는 데이터가 특정 시점에 존재했고 변조되지 않았음을 증명하는 법적 도구로 인정받는 추세
   - EU eIDAS 2.0은 Qualified Electronic Ledger 개념 도입, 2026년 12월 전면 시행
   - SHA-256 해싱 + 블록체인 앵커링은 타임스탬프 조작 비용이 수십억 달러 수준이라 법적 증거력 높음
   - 미국 버몬트/애리조나 등 주법으로 블록체인 기록 인정

4. **한국 저작권법**
   - 정보분석 예외(§35조의5)의 적용 범위 논쟁
   - **명시적 거부 의사 표시 + 기술적 보호조치** → 예외 적용 배제 주장 가능

### Nightshade 딜레마 (AI 기업이 소송하기 어려운 이유)

소송하려면 자기 불법행위 인정해야 함:
- "Roode가 우리 모델 손상시켰다" 주장 = "우리가 동의 없이 학습" 자백
- 그 순간 아티스트 측 저작권 침해 반소 근거 성립
- **Nightshade 출시 2년간 단 한 건의 소송도 없음**

Roode는 여기에 **블록체인 증거까지 추가**해서 공격자의 법적 리스크를 극대화.

---

## 🎯 차별화 (Differentiation)

### 경쟁 분석

| 항목 | Glaze | Nightshade | Cara | **Roode** |
|-----|-------|-----------|------|----------|
| 학습 방어 | ✅ | ✅ | ❌ | ✅ |
| 학습 탐지/증명 | ❌ | ❌ | ❌ | ✅ |
| 집단 방어 | ❌ | ❌ | 부분적 | ✅ |
| On-chain 사전 증거 | ❌ | ❌ | ❌ | ✅ |
| Signal rotation | 수동 | 수동 | - | **자동, 알고리즘적** |
| 법적 대응 지원 | ❌ | ❌ | ❌ | ✅ |
| 한국어 UX | ❌ | ❌ | ❌ | ✅ |

### 핵심 차별점

1. **세계 최초 체계적 탐지/증명 서비스**
2. **블록체인 기반 사전 증거 체인** — Roode만의 유일 기술
3. **집단 방어 인프라** — 개별 도구가 아닌 플랫폼 레벨
4. **Commit-reveal signal rotation** — arms race 구조적 대응
5. **한국 시장 공백** — Glaze/Nightshade 한국어 미지원
6. **운동(Movement) 서사** — 단순 기술이 아닌 선언적 플랫폼

---

## 🌍 시장 기회 (Market Opportunity)

### 수요의 실존 증거

- **Cara**: 2024년 5월 **100만 가입자 돌파**
- **Glaze**: 누적 다운로드 **수백만** 건
- **Nightshade**: 출시 첫 주 서버 다운 수준의 폭주
- **한국 커뮤니티**: 2023 NovelAI leak 이후 AI 반감 극대화

### 목표 시장

**1차 타깃**: 한국 디지털 일러스트레이터 (10-30만 명)
- 트위터 그림쟁이, 루리웹/아카라이브 창작
- 웹툰/일러스트 프리랜서
- 그라폴리오, 픽시브 한국 사용자

**2차**: 아시아권 (일본, 대만) + 영미권 (Cara, ArtStation 사용자)

**3차 (B2B)**: 출판사, 게임사, 웹툰 플랫폼 IP 보호

### 수익 모델

1. **Freemium 구독** (Free / Pro $5-10 / Studio $50+)
2. **탐지 서비스 API** (B2B, 회당 $50-500)
3. **법적 대응 패키지** (성공 수수료)
4. **Web3 네이티브** (NFT 증거, DAO, crowdfunded 소송)

---

## 🚀 로드맵 (Roadmap)

### Phase 0: Hackathon Demo (Now)
- ✅ Radioactive signal 개념 증명 (CLIP perturbation)
- ✅ On-chain commitment 시뮬레이션 (Base testnet)
- ✅ 업로드 파이프라인 (Streamlit)
- ✅ 탐지 파이프라인 + 통계 검정
- ✅ Reveal 시연 + 법정 증거 리포트

### Phase 1: MVP (1-3 months)
- Base mainnet 배포
- 다층 시그널 (CLIP + VAE)
- 자동 rotation 메커니즘
- 웹 플랫폼 (Next.js + Wagmi + Base)
- 베타 작가 50-100명

### Phase 2: Public Launch (3-6 months)
- 선언문 공식 발표
- 한국 작가 커뮤니티 타깃
- 1,000+ 가입
- 첫 탐지 사례 언론 공개
- FLUX, SDXL 지원 확대

### Phase 3: Scale (6-12 months)
- 일본/대만 확장
- 상용 API 부분 탐지 지원
- DAO 구조
- 집단 소송 첫 사례
- 학술 논문 발표

### Phase 4: Ecosystem (12+ months)
- 오픈소스 탐지 프로토콜 표준화
- 플랫폼 간 상호운용
- 정책/입법 옹호

---

## 💪 팀의 역량 (Why Us)

### Roode의 배경

- **Web3 전문성**: Blockchain at Yonsei, Sui 공식 문서 번역팀, 해커톤 수상
- **AI/ML 이해**: CLIP, Diffusion 모델, adversarial ML 학습
- **한국 커뮤니티 이해**: Web3/작가 씬 네트워크
- **빌딩 경험**: Orbis, DeltaX, Doodle Wall, DAAS-Vader
- **연구 역량**: EIP-4337, AI 에이전트 결제 인프라 등 심층 분석 이력

### 왜 지금인가 (Why Now)

1. **법적 판례 형성 임박**: NYT v. OpenAI, Andersen v. Stability 2026-2027
2. **기술 성숙**: Radioactive, Nightshade 등 핵심 기법 검증 완료
3. **시장 수요 확인**: Cara 100만, Glaze/Nightshade 폭발적 반응
4. **한국 시장 공백**: Glaze 한국어 없음, 집단 방어 전무
5. **블록체인 증거 법제화**: EU eIDAS 2.0 2026.12 전면 시행, 미국 주별 인정 확대
6. **Base 생태계 성숙**: L2 중 최대 성장, 소비자 앱 기본값

---

## 📊 데모에서 시연할 것

### 1. 이미지 보호 (2분)
- 작가가 그림 업로드
- Roode radioactive signal 실시간 주입 (CLIP embedding direction perturbation)
- Before/After 시각적 비교 — 육안으로 구별 불가
- SHA-256 hash + 타임스탬프 기록

### 2. On-chain Commitment (1분)
- Base Sepolia testnet에 signal commitment **실제 트랜잭션** 기록
- 실시간 트랜잭션 해시 + Basescan explorer 링크 시연
- "이 시점에 우리가 먼저 기록했다" — 블록체인 타임스탬프 확인

### 3. 탐지 분석 (3분)
- 사전 학습된 suspect 모델 vs 통제군 비교 (precomputed 시뮬레이션)
- CLIP alignment score: Clean μ≈0.02 vs Suspect μ≈0.17
- **p-value 실시간 출력**: p = 3.37×10⁻⁶³, Cohen's d = 3.01
- 통계적 확신: "99.9999% 이상의 신뢰도로 signal 검출"

### 4. Reveal + 법정 증거 리포트 (2분)
- On-chain commitment에서 signal params reveal
- 검증: `hash(revealed + salt) == on-chain hash` ✅
- 자동 생성된 과학적 + 법적 증거 문서 (JSON + PDF)
- DMCA takedown 지원 프레임

### 📌 데모 핵심 메시지
> 기술 로드맵: Phase 1에서 Data Taggants / Semantic Backdoor을 생성 모델에 적용해 diffusion purification 이후에도 탐지 가능한 시스템을 구현. 현재 연구 진행 중.

---

## 🎤 예상 질문 대응

**Q1: 이미 LAION에 들어간 과거 작품은?**
A: 소급 적용 불가. 플랫폼 가입 후 업로드분부터 보호. 과거 작품은 기존 법적 경로. 그래도 "앞으로 작품은 보호된다"는 가치.

**Q2: Purification으로 시그널 지울 수 있지 않나?**
A: 맞음. 단 세 가지로 대응:

1. **현실적 위협 모델**: 실제 피해 대부분인 소규모 LoRA 파인튜닝은 purification을 쓰지 않음. 표준 파이프라인에서 Primary signal은 유효.

2. **기술 로드맵**: Diffusion purification 이후에도 모델 행동으로 증명하는 Data Taggants·Semantic Backdoor 방식을 생성 모델에 적용하는 연구 중. 이 방향은 ICLR 2025에서 이론적으로 검증됨.

3. **on-chain 증거**: purification을 의도적으로 적용했다는 사실 자체가 법적 고의성 증거. 블록체인 타임스탬프는 어떤 기술적 우회와 무관하게 남음.

**Q3: 상용 API 탐지 못 하면?**
A: 현재 학계 난제. 우리도 완벽하진 않음. 그러나:
- 오픈소스 모델(국내 mimicry 피해 대부분) 탐지 가능
- Black-box 기법 지속 연구
- 모델 공개/규제 흐름 유리

**Q4: 작가가 혼자 Glaze 쓰면 되지 않나?**
A:
- Glaze는 개별 도구, **탐지/증명/법적 증거 기능 없음**
- 개인 데이터는 대규모 모델 탐지 불가 — 집단 필요
- Glaze 사용자도 보호됐는지 확인 못 함
- Roode = **인프라 + 증거 체인**, Glaze = **도구**

**Q5: AI 기업이 역소송하면?**
A: Nightshade 팀 2년간 0건. 소송 시 자기 불법행위 자백 구조. Roode는 "보호조치" 프레임 + 블록체인 증거로 더 강화. 초기부터 법무 자문 설계.

**Q6: 왜 Base?**
A: Coinbase L2로 2025년 L2 수익 지배적 점유. 소비자 앱과 소셜 프로토콜에 기본 선택. EVM = 전 세계 법적/기술적 인프라 활용. 거의 공짜 수수료. 한국 Coinbase 브랜드 인지도.

**Q7: Commit-reveal의 보안은?**
A: 표준 암호학 프리미티브. Hash collision 수학적으로 불가능 (SHA-256). 블록체인 앵커링은 51% 공격이 필요한데 비트코인 기준 수십억 달러, 이더리움/Base도 상응하는 수준으로 경제적 비합리적.

**Q8: Rotation 시점은 어떻게 결정?**
A: 플랫폼 누적 이미지 수 기반 자동 트리거. Early tier (1K), Growth tier (10K) 등 경제적 의미있는 임계점. 구체적 기준은 ToS에 사전 공개.

---

## 🌟 비전 (Vision)

### 단기: 기술 플랫폼
"내 그림이 AI에 학습됐는지 과학적, 법적으로 증명할 수 있는 세계 최초 플랫폼"

### 중기: 운동(Movement)
"AI 학습을 거부하는 아티스트들의 집단 방어 연대 + 법적 증거 인프라"

### 장기: 인프라
"창작자가 자기 작품의 AI 학습 여부를 통제하는 것이 당연한 시대를 만드는 표준 인프라"

---

## 📎 부록: 핵심 논문

**[1]** Sablayrolles et al. (2020). *Radioactive data: tracing through training*. ICML.
- 학습 데이터 1%만 마킹해도 p<10^-4 탐지. Roode 핵심 기법 이론 기반.

**[2]** Shan et al. (2024). *Nightshade: Prompt-Specific Poisoning Attacks on Text-to-Image Generative Models*. IEEE S&P.
- 50-100 sample로 SDXL 프롬프트 제어. Poisoning 효율성 검증.

**[3]** Carlini et al. (2023). *Extracting Training Data from Diffusion Models*. USENIX Security.
- Memorization 실증. 법적 증거로서 활용 가능성.

**[4]** Sander et al. (2024). *Watermarking Makes Language Models Radioactive*. NeurIPS.
- p<10^-30 수준 탐지 입증. Roode 기법의 확장 가능성.

**[5]** Shan et al. (2023). *Glaze: Protecting Artists from Style Mimicry by Text-to-Image Models*. USENIX Security.
- Style cloaking 한계와 의의. Roode가 넘어서려는 대상.

**[6]** Zhao et al. (2025). *Enhancing VAEs with Smooth Robust Latent Encoding* (SRL-VAE).
- 최신 우회 공격. Arms race 현실.

---

## 🤝 마치며

우리는 완벽한 방패를 만들지 않습니다.

우리가 만드는 것:
- **기술적 억제력** (공격자 비용 상승)
- **집단적 증거 인프라** (개인이 못하는 걸 플랫폼이)
- **블록체인 기반 사전 증거 체인** (사후 조작 불가)
- **법적 정당성의 기술적 구현** (TPM as on-chain commitment)
- **아티스트의 주체성 회복**

**"AI는 막을 수 없다"는 말은 틀렸습니다.**

**"개인은 막을 수 없다. 하지만 우리는 할 수 있다.**
**그리고 우리는 블록체인에 이미 기록해두었다."**

이것이 Roode입니다.

---

*Roode · Collective Defense Infrastructure for Artists in the Age of AI*  
*Built on Base · Protected by Cryptography · Governed by Community*
