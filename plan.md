# 4주 완성 실행 계획 (PLAN.md)

## 아키텍처 개요

핵사고날 아키텍처 (Hexagonal Architecture) - 4 레이어

```
├── README.md                     # 프로젝트 개요, 아키텍처 규칙, 실행 방법
│
├── app                           # FastAPI 애플리케이션 엔트리 포인트
│   ├── __init__.py               # app 패키지 선언
│   └── main.py                   # 서버 실행, router 등록, middleware 설정
│
├── infrastructure                # ⭐ 공통 기술 인프라 (DB, ORM, 설정 등)
│   ├── __init__.py               # infrastructure 패키지 선언
│   │
│   ├── config                    # 인프라 관련 설정 모음
│   │   └── __init__.py           # DB / MQ / LLM 등 설정 관리
│   │
│   ├── db                        # DB 연결 및 세션 관리
│   │   └── __init__.py           # DB engine, session factory
│   │
│   └── orm                       # ORM 모델 정의
│       └── __init__.py           # SQLAlchemy Base, 테이블 매핑 클래스
│
├── modules                       # ⭐ 도메인별 모듈 (팀원 단위 협업의 핵심)
│   ├── __init__.py               # modules 패키지 선언
│   │
│   └── mq                        # MQ 도메인 (예: 메시지 큐 처리)
│       ├── __init__.py           # mq 모듈 선언
│       │
│       ├── adapter               # Hexagonal Adapter 계층
│       │   ├── __init__.py
│       │   │
│       │   ├── input             # Inbound Adapter (외부 → 내부)
│       │   │   ├── __init__.py
│       │   │   │
│       │   │   └── web            # Web API 진입점 (FastAPI)
│       │   │       ├── __init__.py
│       │   │       │
│       │   │       ├── request    # API 요청 DTO (Pydantic Model)
│       │   │       │   └── __init__.py
│       │   │       │
│       │   │       ├── response   # API 응답 DTO
│       │   │       │   └── __init__.py
│       │   │       │
│       │   │       └── router     # FastAPI router 정의
│       │   │           └── __init__.py
│       │   │
│       │   └── output            # Outbound Adapter (내부 → 외부)
│       │       ├── __init__.py
│       │       │
│       │       └── repository     # DB / MQ / 외부 시스템 접근 구현체
│       │           └── __init__.py
│       │
│       ├── application           # Application Layer (유스케이스 계층)
│       │   ├── __init__.py
│       │   │
│       │   ├── dto                # 유스케이스용 DTO
│       │   │   └── __init__.py
│       │   │
│       │   ├── port               # Application Port (의존성 인터페이스)
│       │   │   └── __init__.py
│       │   │
│       │   └── usecase            # 실제 비즈니스 흐름 구현
│       │       └── __init__.py
│       │
│       └── domain                # ⭐ 순수 도메인 계층
│           ├── __init__.py        # 도메인 패키지
│           └── model.py           # 도메인 모델 / 엔티티 / 규칙
│
└── test                          # 테스트 코드
    ├── __init__.py               # test 패키지 선언
    └── dev_lsy                   # 개인 / 실험용 테스트 영역
        └── __init__.py
```

**핵사고날 의존성 흐름**:
```
Adapter (Web) → Application (UseCase) → Domain ← Infrastructure (DB, API)
   [Inbound]        [Port]              [Core]      [Outbound]
```

---
## 🏗️ 핵심 설계 원칙 (Anti Over-Engineering)

### **철학: YAGNI + KISS 우선**

> "4주 프로젝트에서 과도한 추상화는 독이다"

---

### ❌ 하지 말 것

#### 1. 불필요한 추상화 계층
```python
# ❌ 나쁜 예: 구현체가 1개뿐인데 추상 포트 만들기
class OAuthProviderPort(ABC):
    @abstractmethod
    def authenticate(self): pass

class GoogleOAuthProvider(OAuthProviderPort):
    def authenticate(self): ...

# ✅ 좋은 예: 직접 구체 클래스 사용
class GoogleOAuthService:
    def authenticate(self): ...
```

**원칙:** 추상화는 구현체가 **2개 이상**일 때만 만든다.

---

#### 2. 복잡한 DI (Dependency Injection) 셋업
```python
# ❌ 나쁜 예: 불필요한 초기화 함수
def register_provider(container):
    container.register(OAuthProviderPort, GoogleOAuthProvider)
    
def set_use_case(use_case, provider):
    use_case.provider = provider

# ✅ 좋은 예: Router에서 직접 인스턴스화
from services.auth_service import GoogleOAuthService

@router.post("/login")
def login():
    service = GoogleOAuthService()  # 필요한 곳에서 바로 생성
    return service.authenticate()
```

**원칙:** Router에서 필요한 Service를 **직접 생성**한다.

---

#### 3. 파라미터 릴레이 (Parameter Relay)
```python
# ❌ 나쁜 예: 설정값을 계속 전달
def main(client_id, client_secret):
    service = create_service(client_id, client_secret)
    
def create_service(client_id, client_secret):
    return GoogleOAuthService(client_id, client_secret)

# ✅ 좋은 예: 필요한 곳에서 직접 읽기
from config.settings import get_settings

class GoogleOAuthService:
    def __init__(self):
        settings = get_settings()
        self.client_id = settings.GOOGLE_CLIENT_ID
        self.client_secret = settings.GOOGLE_CLIENT_SECRET
```

**원칙:** 설정값은 `config`에서 필요할 때 읽는다. `os.getenv()` 직접 호출 금지.

---

#### 4. 과도한 Layering
```python
# ❌ 나쁜 예: 불필요한 DTO 변환 계층
Request DTO → Domain Entity → Repository DTO → DB Model → 역변환 4단계

# ✅ 좋은 예: 필요한 만큼만
Request DTO → Service Logic → DB Model (ORM)
```

**원칙:** DTO는 API 경계(Request/Response)에만 사용. 내부는 직접 모델 사용.

---

### ✅ 해야 할 것

#### 1. Service 직접 사용
```python
# services/auth_service.py
class GoogleOAuthService:
    def __init__(self):
        settings = get_settings()
        self.client_id = settings.GOOGLE_CLIENT_ID
    
    def login(self, code: str) -> User:
        # 구글 OAuth 로직
        ...
```

#### 2. Router에서 직접 생성
```python
# api/v1/auth.py
from services.auth_service import GoogleOAuthService

@router.post("/auth/google/callback")
def google_callback(code: str):
    service = GoogleOAuthService()
    user = service.login(code)
    return {"user": user}
```

#### 3. 설정은 config에서
```python
# config/settings.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    DATABASE_URL: str
    
    class Config:
        env_file = ".env"

_settings = None

def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
```

**사용:**
```python
from config.settings import get_settings

settings = get_settings()
client_id = settings.GOOGLE_CLIENT_ID
```

**금지:**
```python
import os
client_id = os.getenv("GOOGLE_CLIENT_ID")  # ❌ 이렇게 하지 마세요
```

#### 4. 추상화는 실제 필요할 때만
```python
# 구현체가 2개 이상일 때만 추상화
class StoragePort(ABC):  # ✅ S3, MinIO 둘 다 지원 필요
    @abstractmethod
    def upload(self, file): pass

class S3Storage(StoragePort): ...
class MinIOStorage(StoragePort): ...
```

---

## Backlog

> **개발 전략**: Walking Skeleton + 수직 슬라이스 (Vertical Slice)
> - 기초 빌딩 블록 먼저 구현 (의존성 높고 간단한 값 객체)
> - 이후 기능별로 도메인→유스케이스→API 완전히 구현
> - 각 Phase마다 작동하는 기능 완성

## 🎯 프로젝트 개요

**프로젝트명:** 대학생 첫 자취 의사결정 지원 서비스  
**핵심 컨셉:** 대학생이 처음 집을 구할 때 혼자서도 판단할 수 있게 돕는 AI 기반 추천 서비스  
**기간:** 4주 (D-0 ~ D-28)  
**팀 구성:** 6명 (BE 5명, FE 1명)

---

## 🎪 핵심 가치 제안 (Simple & Clear)

> **"대학생 첫 계약, 놓치기 쉬운 리스크를 AI가 잡아주는 서비스"**

### Key Results (KR)
- **KR1**: 대학생이 "이 집이 나에게 맞는다"는 연결 경험 제공
- **KR2**: 평균 추천 응답 속도 < 5초
- **KR3**: 중간 발표에서 완전한 Flow 시연 성공
- **KR4**: 최종 발표에서 실제 데이터 기반 Before/After 시나리오 시연

---

---

# House Analysis Module - TDD 기반 실행 계획

## 🎯 프로젝트 목적

주소를 입력하면 건물 리스크와 가격 적정성을 분석하고, 결과를 DB에 자동 저장하는 내부 분석 모듈을 구축한다.

- 외부 공개용 ❌
- 내부 서비스/추천 로직에서 재사용 ✅
- Hexagonal Architecture + 팀 공통 구조 준수 ✅
- DB는 기존 인프라 그대로 사용 ✅

---

## 📋 참고사항

### 현재 프로젝트 상태 (2025-12-30 기준)

**기존 모듈 (7개)**:
- `auth`: Google OAuth2 인증
- `abang_user`: 사용자 관리
- `finder_request`: 매물 요청 관리 (가장 완성도 높음)
- `house_platform`: 집방 데이터 통합
- `student_house`: 학생 주거 추천 (임베딩 검색, 의미 분석)
- `chatbot`: AI 기반 추천 및 설명
- `mq`: 메시지 큐 처리 (RabbitMQ)

**인프라 구성**:
- DB: PostgreSQL + SQLAlchemy + psycopg2
- Session 관리: `infrastructure/db/postgres.py`의 `get_db_session()` (FastAPI Depends 호환)
- ORM Base: `infrastructure/orm/`에 중앙 집중식 ORM 모델
- 설정: `infrastructure/config/env.py`의 `Settings` 클래스
- 외부 서비스: OpenAI 임베딩 (`infrastructure/external/embedding_agent.py`)

**main.py 현재 라우터**:
- auth_router
- search_house_router
- finder_request_router
- chatbot_router
- student_house_router

**삭제된 모듈**:
- `risk_analysis`: 리스크 분석 (20+ 파일 삭제됨)
- `risk_analysis_mock`: Mock 구현 (8+ 파일 삭제됨)
→ 본 계획은 이들을 TDD 방식으로 재구축하는 것

---

## 🏗️ 구현 대상 기능 (확정)
✅ ① get_risk_score(address)

기능

주소 → 법정동/번지 코드 변환

건축물대장 API 조회

아래 요소로 Risk 점수 산출

위반 건축물 여부

내진 설계 여부

건축물 노후도

결과 DB 저장

점수 + 요약 코멘트 반환

출력 예

{
  "risk_score": 72,
  "summary": "내진 설계 미적용, 준공 30년 이상으로 위험도 높음"
}

✅ ② get_price_reasonable(address, type)

기능

주소 → 법정동 코드 변환

실거래가 API 조회

3㎡당 거래가 계산

동일 지역 평균과 비교

가격 적정성 점수 산출

결과 DB 저장

출력 예

{
  "price_score": 38,
  "comment": "동 평균 대비 약 22% 높은 가격"
}

3. 팀 프로젝트 기준 최종 디렉토리 구조

📁 팀 구조에 100% 맞춘 최종안

modules/
  house_analysis/
    ├── adapter/
    │   ├── input/
    │   │   └── web/
    │   │       ├── request/
    │   │       ├── response/
    │   │       └── router/
    │   │           └── house_analysis_router.py
    │   │
    │   └── output/
    │       └── repository/
    │           ├── address_codec_repository.py
    │           ├── public_api_repository.py
    │           ├── risk_history_repository.py
    │           └── price_history_repository.py
    │
    ├── application/
    │   ├── dto/
    │   │   ├── risk_dto.py
    │   │   └── price_dto.py
    │   │
    │   ├── port/
    │   │   ├── address_codec_port.py
    │   │   ├── public_api_port.py
    │   │   ├── risk_history_port.py
    │   │   └── price_history_port.py
    │   │
    │   └── usecase/
    │       ├── get_risk_score_usecase.py
    │       └── get_price_reasonable_usecase.py
    │
    └── domain/
        ├── model.py
        ├── services.py
        └── exceptions.py

4. 아키텍처 흐름 (실제 실행 흐름)
[API 요청]
   ↓
[Router]
   ↓
[UseCase]
   ├─ AddressCodecPort
   ├─ PublicApiPort
   ├─ Domain Service (점수 계산)
   └─ Repository.save()  ← DB 저장
   ↓
[Response 반환]


✔ DB 세션은 get_db_session()을 그대로 사용
✔ commit / rollback 은 UseCase에서 제어
✔ Repository는 insert만 담당
✔ Domain은 순수 계산 로직만 포함

5. DB 처리 방식 (중요)
✔ 사용 방식

DB 설정 ❌ (이미 있음)

Session 생성 ❌

ORM 모델 정의 → infrastructure/orm 사용

get_db_session()을 FastAPI Depends로 주입

✔ 저장 시점

UseCase 내부에서

repo.save(...)
db.commit()

✔ 저장 대상
테이블	내용
risk_score_history	주소, risk_score, 요약, factors
price_score_history	주소, 거래유형, 점수, metrics
6. main.py 연동 방식 (확정)
from modules.house_analysis.adapter.input.web.router.house_analysis_router import router as house_analysis_router

api_router.include_router(house_analysis_router)


API 호출 예:

GET /api/house_analysis/risk?address=서울시 강남구 역삼동 777
GET /api/house_analysis/price?address=...&deal_type=전세

7. 개발 순서 (실제 작업 기준)
🟩 Phase 1 – 구조 구성 (0.5일)

모듈 디렉토리 생성

router / usecase / port / repository 뼈대

🟩 Phase 2 – Port & UseCase 정의 (0.5일)

Risk / Price UseCase

Repository Port 정의

🟩 Phase 3 – 주소 & API 연동 (1~2일)

주소 → 법정동 변환

건축물대장 / 실거래가 API 연동

🟩 Phase 4 – 점수화 로직 (1~2일)

Risk 규칙

Price 평균 계산

🟩 Phase 5 – DB 저장 연결 (0.5일)

Repository 구현

commit / rollback 처리

🟩 Phase 6 – 테스트 & 정리 (1일)

UseCase 단위 테스트

API 호출 확인

8. 이 설계의 장점 (팀 관점)

✅ 기존 프로젝트 구조 100% 준수
✅ 추후 AI 추천 / 점수 고도화 가능
✅ 도메인 분리 완벽
✅ DB 의존성 최소화
✅ 테스트/확장 용이
✅ 팀원별 분업 쉬움

9. 최종 요약 (한 줄)

"주소 기반 위험도·가격 분석을 수행하고 결과를 자동 저장하는 House Analysis 모듈을, 팀 표준 아키텍처에 맞게 구현한다."

---

## 📐 아키텍처 설계

### 최종 디렉토리 구조

```
modules/house_analysis/
├── adapter/
│   ├── input/
│   │   └── web/
│   │       ├── request/
│   │       │   ├── __init__.py
│   │       │   ├── risk_request.py          # GET query params용 모델
│   │       │   └── price_request.py
│   │       ├── response/
│   │       │   ├── __init__.py
│   │       │   ├── risk_response.py         # API 응답 DTO
│   │       │   └── price_response.py
│   │       └── router/
│   │           ├── __init__.py
│   │           └── house_analysis_router.py # FastAPI 엔드포인트
│   │
│   └── output/
│       └── repository/
│           ├── __init__.py
│           ├── address_codec_repository.py   # 주소 → 법정동코드 변환
│           ├── building_ledger_repository.py # 건축물대장 API
│           ├── transaction_price_repository.py # 실거래가 API
│           ├── risk_history_repository.py    # 리스크 분석 결과 저장
│           └── price_history_repository.py   # 가격 분석 결과 저장
│
├── application/
│   ├── dto/
│   │   ├── __init__.py
│   │   ├── risk_dto.py                      # 유스케이스 내부용 DTO
│   │   └── price_dto.py
│   │
│   ├── port/
│   │   ├── __init__.py
│   │   ├── address_codec_port.py            # 추상 인터페이스
│   │   ├── building_ledger_port.py
│   │   ├── transaction_price_port.py
│   │   ├── risk_history_port.py
│   │   └── price_history_port.py
│   │
│   └── usecase/
│       ├── __init__.py
│       ├── analyze_risk_usecase.py          # 리스크 분석 유스케이스
│       └── analyze_price_usecase.py         # 가격 분석 유스케이스
│
└── domain/
    ├── __init__.py
    ├── model.py                             # RiskScore, PriceScore 도메인 모델
    ├── service.py                           # 순수 계산 로직
    └── exception.py                         # 도메인 예외

infrastructure/orm/
├── __init__.py
├── risk_score_history_orm.py                # 리스크 분석 결과 테이블
└── price_score_history_orm.py               # 가격 분석 결과 테이블

test/house_analysis/
├── __init__.py
├── domain/
│   ├── __init__.py
│   └── test_risk_service.py                 # 도메인 서비스 단위 테스트
├── application/
│   ├── __init__.py
│   └── test_analyze_risk_usecase.py         # 유스케이스 단위 테스트 (mock)
└── adapter/
    ├── __init__.py
    └── test_house_analysis_router.py        # API 통합 테스트
```

### 의존성 흐름

```
[FastAPI Router]
    ↓ (Request DTO)
[UseCase]
    ├─→ [AddressCodecPort] → [AddressCodecRepository] → [외부 API/DB]
    ├─→ [BuildingLedgerPort] → [BuildingLedgerRepository] → [공공 API]
    ├─→ [TransactionPricePort] → [TransactionPriceRepository] → [공공 API]
    ├─→ [Domain Service] (순수 계산 로직)
    └─→ [HistoryPort] → [HistoryRepository] → [PostgreSQL]
    ↓ (Response DTO)
[FastAPI Response]
```

**핵심 원칙**:
- Router는 UseCase를 직접 생성 (DI 컨테이너 없음)
- UseCase는 Port를 통해 Repository와 통신
- Domain은 외부 의존성 제로 (순수 계산 로직)
- DB 세션은 `get_db_session()` Depends로 주입

---

## 🧪 테스트 전략

### 테스트 레벨

1. **Domain 단위 테스트** (가장 먼저)
   - 순수 계산 로직 테스트
   - Mock 불필요 (외부 의존성 없음)
   - 예: `test_calculate_risk_score()`

2. **UseCase 단위 테스트**
   - Port를 Mock으로 대체
   - 비즈니스 흐름 검증
   - 예: `test_analyze_risk_with_mocked_repositories()`

3. **Repository 통합 테스트** (선택적)
   - 실제 외부 API 호출 (Rate Limit 주의)
   - 또는 VCR/httpretty로 녹화/재생

4. **API 통합 테스트**
   - TestClient로 엔드포인트 호출
   - 전체 흐름 검증
   - DB는 in-memory SQLite 또는 테스트 DB 사용

### 테스트 실행 명령어

```bash
# 전체 테스트
pytest test/house_analysis/

# 도메인만
pytest test/house_analysis/domain/

# 특정 테스트
pytest test/house_analysis/domain/test_risk_service.py::test_calculate_risk_score -v
```

---

## 📊 Epic별 실행 계획 (TDD 기반)

> **TDD 진행 방식**:
> - `/go` 명령어로 다음 미완료 테스트 자동 실행
> - Red (테스트 실패) → Green (최소 구현) → Refactor (개선) 사이클 준수
> - 각 테스트마다 `/commit-tdd` 또는 `/tidy` + `/commit` 실행

---

### Epic 1: Domain Layer - 리스크 점수 계산 로직

**목표**: 건축물 정보를 받아 리스크 점수를 계산하는 순수 도메인 로직 구현

**테스트 목록**:

- [x] **test_risk_score_domain_model_creation**
  - RiskScore 도메인 모델 생성 (score, factors, summary)
  - dataclass로 구현, 기본값 설정

- [x] **test_calculate_risk_score_with_violation**
  - 위반 건축물인 경우 리스크 점수 계산
  - 위반 여부: True → 점수 +30

- [x] **test_calculate_risk_score_without_seismic_design**
  - 내진 설계 없는 경우 리스크 점수 계산
  - 내진 설계: False → 점수 +25

- [x] **test_calculate_risk_score_by_building_age**
  - 건물 노후도에 따른 리스크 점수 계산
  - 30년 이상: +40, 20~30년: +30, 10~20년: +20, 10년 미만: +10

- [x] **test_calculate_risk_score_combined**
  - 여러 요소 결합된 리스크 점수 계산
  - 위반 건축물 + 내진 미적용 + 30년 이상 = 95점

- [x] **test_generate_risk_summary_message**
  - 리스크 점수에 따른 요약 메시지 생성
  - 점수 범위별 적절한 메시지 반환

**파일**:
- `modules/house_analysis/domain/model.py`
- `modules/house_analysis/domain/service.py`
- `test/house_analysis/domain/test_risk_service.py`

---

### Epic 2: Domain Layer - 가격 적정성 계산 로직

**목표**: 실거래가 데이터로 가격 적정성 점수를 계산하는 순수 도메인 로직 구현

**테스트 목록**:

- [x] **test_price_score_domain_model_creation**
  - PriceScore 도메인 모델 생성 (score, comment, metrics)
  - dataclass로 구현

- [x] **test_calculate_price_per_area**
  - 3.3㎡당 가격 계산
  - 전세가 / 면적 * 3.3 = 평당 가격

- [x] **test_calculate_price_score_above_average**
  - 지역 평균 대비 높은 가격 점수 계산
  - 평균 대비 +20% → 점수 40 (낮음)

- [x] **test_calculate_price_score_below_average**
  - 지역 평균 대비 낮은 가격 점수 계산
  - 평균 대비 -10% → 점수 55 (보통)

- [x] **test_calculate_price_score_at_average**
  - 지역 평균과 동일한 가격 점수 계산
  - 평균과 동일 → 점수 50

- [x] **test_generate_price_comment**
  - 가격 점수에 따른 코멘트 생성
  - "동 평균 대비 약 22% 높은 가격"

**파일**:
- `modules/house_analysis/domain/model.py`
- `modules/house_analysis/domain/service.py`
- `test/house_analysis/domain/test_price_service.py`

---

### Epic 3: Infrastructure - ORM 모델 정의

**목표**: 분석 결과를 저장할 DB 테이블 ORM 정의

**테스트 목록**:

- [x] **test_risk_score_history_orm_table_creation**
  - RiskScoreHistory ORM 모델 정의
  - 컬럼: id, address, risk_score, summary, factors(JSON), created_at

- [x] **test_price_score_history_orm_table_creation**
  - PriceScoreHistory ORM 모델 정의
  - 컬럼: id, address, deal_type, price_score, comment, metrics(JSON), created_at

- [x] **test_risk_score_history_save_and_load**
  - RiskScoreHistory 저장 및 조회 테스트
  - DB에 데이터 저장 후 조회하여 검증

- [x] **test_price_score_history_save_and_load**
  - PriceScoreHistory 저장 및 조회 테스트
  - DB에 데이터 저장 후 조회하여 검증

**파일**:
- `infrastructure/orm/risk_score_history_orm.py`
- `infrastructure/orm/price_score_history_orm.py`
- `test/house_analysis/infrastructure/test_orm.py`

---

### Epic 4: Application Layer - Port 인터페이스 정의

**목표**: 외부 의존성에 대한 추상 인터페이스(Port) 정의

**테스트 목록**:

- [x] **test_address_codec_port_interface**
  - AddressCodecPort 인터페이스 정의
  - 메서드: `convert_to_legal_code(address: str) -> dict`

- [x] **test_building_ledger_port_interface**
  - BuildingLedgerPort 인터페이스 정의
  - 메서드: `fetch_building_info(legal_code: str) -> dict`

- [x] **test_transaction_price_port_interface**
  - TransactionPricePort 인터페이스 정의
  - 메서드: `fetch_transaction_prices(legal_code: str, deal_type: str) -> list`

- [x] **test_risk_history_port_interface**
  - RiskHistoryPort 인터페이스 정의
  - 메서드: `save(risk_score: RiskScore) -> None`

- [x] **test_price_history_port_interface**
  - PriceHistoryPort 인터페이스 정의
  - 메서드: `save(price_score: PriceScore) -> None`

**파일**:
- `modules/house_analysis/application/port/address_codec_port.py`
- `modules/house_analysis/application/port/building_ledger_port.py`
- `modules/house_analysis/application/port/transaction_price_port.py`
- `modules/house_analysis/application/port/risk_history_port.py`
- `modules/house_analysis/application/port/price_history_port.py`
- `test/house_analysis/application/port/test_ports.py`

---

### Epic 5: Application Layer - UseCase 구현 (Risk)

**목표**: 리스크 분석 유스케이스 구현 (Mock Port 사용)

**테스트 목록**:

- [x] **test_analyze_risk_usecase_with_mocked_ports**
  - Mock Port를 사용한 리스크 분석 유스케이스 테스트
  - 주소 → 법정동 코드 → 건축물 정보 → 점수 계산 → DB 저장

- [x] **test_analyze_risk_usecase_with_invalid_address**
  - 잘못된 주소 입력 시 예외 처리
  - AddressCodecPort에서 예외 발생 → 적절한 에러 응답

- [x] **test_analyze_risk_usecase_with_api_failure**
  - 건축물대장 API 실패 시 예외 처리
  - BuildingLedgerPort에서 예외 발생 → 적절한 에러 응답

- [x] **test_analyze_risk_usecase_saves_to_history**
  - 리스크 분석 결과가 히스토리에 저장되는지 검증
  - RiskHistoryPort.save() 호출 확인
  - (이미 test_analyze_risk_usecase_with_mocked_ports에서 검증됨)

**파일**:
- `modules/house_analysis/application/usecase/analyze_risk_usecase.py`
- `modules/house_analysis/application/dto/risk_dto.py`
- `test/house_analysis/application/usecase/test_analyze_risk_usecase.py`

---

### Epic 6: Application Layer - UseCase 구현 (Price)

**목표**: 가격 분석 유스케이스 구현 (Mock Port 사용)

**테스트 목록**:

- [x] **test_analyze_price_usecase_with_mocked_ports**
  - Mock Port를 사용한 가격 분석 유스케이스 테스트
  - 주소 → 법정동 코드 → 실거래가 정보 → 점수 계산 → DB 저장

- [x] **test_analyze_price_usecase_with_no_transaction_data**
  - 실거래가 데이터가 없는 경우 처리
  - 기본 점수 반환 또는 적절한 메시지

- [x] **test_analyze_price_usecase_with_different_deal_types**
  - 거래 유형별(전세/월세) 가격 분석
  - 각 거래 유형에 맞는 계산 로직 적용

- [x] **test_analyze_price_usecase_saves_to_history**
  - 가격 분석 결과가 히스토리에 저장되는지 검증
  - PriceHistoryPort.save() 호출 확인
  - (이미 test_analyze_price_usecase_with_mocked_ports에서 검증됨)

**파일**:
- `modules/house_analysis/application/usecase/analyze_price_usecase.py`
- `modules/house_analysis/application/dto/price_dto.py`
- `test/house_analysis/application/usecase/test_analyze_price_usecase.py`

---

### Epic 7: Adapter Layer - Repository 구현 (Output)

**목표**: Port 인터페이스의 실제 구현체 작성

**테스트 목록**:

- [x] **test_address_codec_repository_integration**
  - 실제 주소 → 법정동 코드 변환 테스트
  - (통합 테스트, VCR 사용 권장)
  - 현재는 하드코딩된 샘플 데이터 반환, 추후 실제 API 연동 필요

- [x] **test_building_ledger_repository_integration**
  - 실제 건축물대장 API 호출 테스트
  - (통합 테스트, VCR 사용 권장)
  - 공공데이터포털 건축물대장 API 실제 연동 완료 (법정동코드 분리, 번/지 4자리 패딩)

- [x] **test_transaction_price_repository_integration**
  - 실제 실거래가 API 호출 테스트
  - (통합 테스트, VCR 사용 권장)
  - 국토교통부 실거래가 API 실제 연동 완료 (아파트 매매/전월세 API 지원)

- [ ] **test_risk_history_repository_save**
  - RiskHistoryRepository의 save() 메서드 테스트
  - 실제 DB 또는 in-memory DB 사용

- [ ] **test_price_history_repository_save**
  - PriceHistoryRepository의 save() 메서드 테스트
  - 실제 DB 또는 in-memory DB 사용

**파일**:
- `modules/house_analysis/adapter/output/repository/address_codec_repository.py`
- `modules/house_analysis/adapter/output/repository/building_ledger_repository.py`
- `modules/house_analysis/adapter/output/repository/transaction_price_repository.py`
- `modules/house_analysis/adapter/output/repository/risk_history_repository.py`
- `modules/house_analysis/adapter/output/repository/price_history_repository.py`
- `test/house_analysis/adapter/output/repository/test_repositories.py`

---

### Epic 8: Adapter Layer - FastAPI Router 구현 (Input)

**목표**: HTTP API 엔드포인트 구현

**테스트 목록**:

- [ ] **test_risk_analysis_endpoint_success**
  - GET /api/house_analysis/risk 성공 케이스
  - 올바른 주소 입력 → 200 OK, 리스크 점수 반환

- [ ] **test_risk_analysis_endpoint_validation_error**
  - GET /api/house_analysis/risk 유효성 검증 실패
  - 빈 주소 입력 → 422 Unprocessable Entity

- [ ] **test_price_analysis_endpoint_success**
  - GET /api/house_analysis/price 성공 케이스
  - 올바른 주소 + 거래유형 → 200 OK, 가격 점수 반환

- [ ] **test_price_analysis_endpoint_missing_deal_type**
  - GET /api/house_analysis/price deal_type 누락
  - 422 Unprocessable Entity

- [ ] **test_router_dependency_injection**
  - FastAPI의 Depends를 사용한 DB 세션 주입 확인
  - get_db_session()이 올바르게 주입되는지 검증

**파일**:
- `modules/house_analysis/adapter/input/web/router/house_analysis_router.py`
- `modules/house_analysis/adapter/input/web/request/risk_request.py`
- `modules/house_analysis/adapter/input/web/request/price_request.py`
- `modules/house_analysis/adapter/input/web/response/risk_response.py`
- `modules/house_analysis/adapter/input/web/response/price_response.py`
- `test/house_analysis/adapter/input/web/test_house_analysis_router.py`

---

### Epic 9: Integration - main.py 연동 및 E2E 테스트

**목표**: 전체 시스템 통합 및 엔드투엔드 테스트

**테스트 목록**:

- [ ] **test_main_app_includes_house_analysis_router**
  - main.py에 house_analysis_router가 등록되었는지 확인
  - app.router.routes에서 확인

- [ ] **test_e2e_risk_analysis_flow**
  - 실제 API 호출 → DB 저장까지 전체 흐름 테스트
  - TestClient 사용, Mock 없이 실제 흐름 검증

- [ ] **test_e2e_price_analysis_flow**
  - 실제 API 호출 → DB 저장까지 전체 흐름 테스트
  - TestClient 사용, Mock 없이 실제 흐름 검증

- [ ] **test_concurrent_requests_handling**
  - 동시 요청 처리 테스트
  - 여러 클라이언트가 동시에 요청해도 정상 동작 확인

**파일**:
- `app/main.py` (수정)
- `test/house_analysis/integration/test_e2e.py`

---

## 🎯 테스트 진행 순서 요약

1. **Epic 1-2**: Domain Layer (외부 의존성 없음, 가장 먼저)
2. **Epic 3**: Infrastructure ORM (DB 테이블 생성)
3. **Epic 4**: Application Port (인터페이스만 정의)
4. **Epic 5-6**: Application UseCase (Mock Port 사용)
5. **Epic 7**: Adapter Repository (실제 구현)
6. **Epic 8**: Adapter Router (API 엔드포인트)
7. **Epic 9**: Integration (전체 통합)

**총 테스트 수**: 약 35개

---

## 📝 개발 가이드

### TDD 사이클 실행 방법

```bash
# 1. 다음 테스트 자동 실행
/go

# 2. 테스트가 실패하는지 확인 (Red)
pytest <test_file>::<test_name> -v

# 3. 최소한의 코드로 테스트 통과 (Green)
# ... 코드 작성 ...
pytest <test_file>::<test_name> -v

# 4. 리팩터링 필요 시
/refactor

# 5. 구조 개선만 필요한 경우
/tidy

# 6. 커밋
/commit-tdd  # 자동으로 structural/behavioral 구분
```

### 백로그 생성

```bash
# 특정 테스트의 백로그 생성 (plan.md에서 텍스트 선택 후)
/backlog

# 또는 다음 미완료 테스트의 백로그 자동 생성
/backlog
```

### 테스트 실행

```bash
# 전체 테스트
pytest

# 특정 모듈
pytest test/house_analysis/

# 특정 파일
pytest test/house_analysis/domain/test_risk_service.py

# 특정 테스트
pytest test/house_analysis/domain/test_risk_service.py::test_calculate_risk_score_with_violation -v

# 커버리지 포함
pytest --cov=modules/house_analysis --cov-report=html
```

---

## ✅ 완료 기준

### Epic별 완료 조건

- [ ] 모든 테스트 통과 (Green)
- [ ] 코드 리뷰 완료
- [ ] 커밋 완료 (`/commit-tdd` 또는 `/tidy` + `/commit`)
- [ ] plan.md의 해당 Epic 체크박스 체크

### 전체 프로젝트 완료 조건

- [ ] 총 35개 테스트 모두 통과
- [ ] API 엔드포인트 정상 동작 확인
  - `GET /api/house_analysis/risk?address=서울시 강남구 역삼동 777`
  - `GET /api/house_analysis/price?address=서울시 강남구 역삼동 777&deal_type=전세`
- [ ] DB에 분석 결과 저장 확인
  - `risk_score_history` 테이블에 데이터 존재
  - `price_score_history` 테이블에 데이터 존재
- [ ] main.py에 router 등록 완료
- [ ] 전체 테스트 커버리지 > 80%

---

## 🚀 다음 단계

1. `/go` 명령어로 첫 번째 테스트부터 시작
2. Red → Green → Refactor 사이클 반복
3. 각 Epic 완료 시 체크박스 체크
4. 최종 통합 테스트 및 문서화

