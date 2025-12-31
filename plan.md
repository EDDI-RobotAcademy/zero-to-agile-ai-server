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

## 👥 팀 역할 및 책임

| 구분 | 역할명 | 담당자 | 핵심 책임 | 비고 |
|------|--------|-----|-----------|------|
| **Control Tower** | BE-1 (Team Lead) | 해인  | API Gateway, User Flow, ERD 총괄, **챗봇 API** ⭐ | 전체 흐름 조율 |
| **Data & Risk** | BE-2 (Risk Eng) | 용준  | 공공데이터 수집, 리스크 분석 로직 | 신뢰성 담당 |
| **Search** | BE-3 (RAG Core) | 장훈  | Vector DB, 검색 최적화, RAG 파이프라인 | 검색 품질 담당 |
| **Process** | BE-4 (Async & Queue) | 승연  | RabbitMQ, 비동기 처리, 데이터 파이프라인 | 속도/안정성 담당 |
| **AI Logic** | BE-5 (Prompt Eng) | 효진  | 페르소나 설계, 프롬프트 엔지니어링, **챗봇 프롬프트** ⭐ | UX 라이팅 담당 |
| **DevOps** | BE-6 (Infra & CI/CD) | 재현  | Docker, 배포, 모니터링, **챗봇 UI** ⭐ | 운영/배포 담당 |


---

### 🚨 팀원별 주의사항

#### BE-1 (다영) - API Gateway
- ✅ Router에서 Service 직접 생성
- ✅ 복잡한 DI 컨테이너 만들지 말 것
- ✅ 설정은 `get_settings()`로

#### BE-2 (용준) - Risk Eng
- ✅ `RiskService` 직접 구현
- ✅ 공공 API 클라이언트는 util로 분리
- ✅ Port/Adapter 불필요

#### BE-3 (장훈) - RAG Core
- ✅ `RAGService` 직접 구현
- ✅ pgvector 직접 사용
- ✅ Repository 패턴만 사용

#### BE-4 (승연) - Async & Queue
- ✅ RabbitMQ Producer/Consumer 직접 구현
- ✅ Worker는 Service를 직접 호출
- ✅ 복잡한 추상화 불필요

#### BE-5 (효진) - Prompt Eng
- ✅ `LLMService` 직접 구현
- ✅ 프롬프트는 템플릿 파일로 관리
- ✅ OpenAI SDK 직접 사용

#### BE-6 (재현) - DevOps
- ✅ Docker Compose로 간단하게
- ✅ CI/CD는 GitHub Actions 템플릿 사용
- ✅ 과도한 오케스트레이션 불필요

---

### 💡 핵심 메시지

> **"4주 안에 완성하려면, 간단하게 만들어야 합니다."**

- 추상화는 필요할 때만
- Service는 Router에서 직접 생성
- 설정은 config에서 읽기
- 불필요한 계층 제거

**목표:** 코드는 단순하게, 기능은 완벽하게 ✨

---

## 🗓️ 주차별 마일스톤

### 1주차: 설계 및 뼈대 구축 (D-0 ~ D-7)
**목표:** "프로젝트 구조 확정 및 기술 검증"

#### 전체 공통 목표
- [ ] **D-1**: 킥오프 미팅 (역할 확인, Git Repository 세팅)
- [ ] **D-2**: ERD 최종 확정 및 공유
- [ ] **D-7**: 1주차 회고 미팅 (각자 진척도 공유)

---

#### BE-1 (Team Lead - 해인)
**핵심 목표:** ERD 확정, API 스펙 정의, 기본 인증 구현

**세부 태스크:**
- [ ] ERD 설계 및 팀원 피드백 반영 (D-1 ~ D-2)
- [ ] PostgreSQL 초기 스키마 생성 (D-3)
- [ ] 회원 가입/로그인 API 구현 (Google OAuth, JWT) (D-3 ~ D-5)
- [ ] 임차인 프로필 생성 API (D-5 ~ D-7)
- [ ] Swagger API 문서 자동화 설정 (D-7)

**산출물:**
- `schema.sql` (초기 DB 스키마)
- `/api/auth/*` 엔드포인트
- `/api/tenants/*` 엔드포인트
- Swagger UI 접근 가능

**협업 포인트:**
- BE-6와 협업: Docker DB 환경 세팅
- 전체 팀과 ERD 리뷰 세션 진행

---

#### BE-2 (Risk Eng - 용준)
**핵심 목표:** 공공 API 연동 및 리스크 데이터 확보

**세부 태스크:**
- [ ] 국토부 건축물대장 API 연동 테스트 (D-1 ~ D-3)
- [ ] 실거래가 API 연동 테스트 (D-1 ~ D-3)
- [ ] 수집 데이터 파싱 로직 구현 (D-4 ~ D-6)
- [ ] 리스크 평가 Rule 설계 (위반 건축물, 내진설계, 사용승인일 등) (D-5 ~ D-7)
- [ ] 샘플 데이터 50개 수집 및 DB 저장 (D-7)

**산출물:**
- `risk_evaluator.py` (리스크 평가 모듈)
- 샘플 매물 데이터 50개 (CSV or JSON)
- 공공 API 연동 문서

**협업 포인트:**
- BE-3와 협업: 수집 데이터를 Vector DB에 전달
- BE-5와 협업: 리스크 Score를 LLM Prompt에 전달할 형식 논의

---

#### BE-3 (RAG Core - 장훈)
**핵심 목표:** pgvector 설정 및 검색 테스트

**세부 태스크:**
- [ ] pgvector 확장 설치 및 테스트 (D-1 ~ D-2)
- [ ] OpenAI 임베딩 API 연동 테스트 (D-2 ~ D-3)
- [ ] 매물 데이터 임베딩 파이프라인 구축 (D-4 ~ D-6)
- [ ] 하이브리드 검색 로직 설계 (키워드 필터 + 벡터 유사도) (D-5 ~ D-7)
- [ ] 테스트 데이터셋으로 검색 정확도 확인 (D-7)

**산출물:**
- `embedding_pipeline.py` (임베딩 생성 모듈)
- `search_engine.py` (하이브리드 검색 모듈)
- 검색 성능 테스트 결과 (Precision, Recall)

**협업 포인트:**
- BE-2와 협업: 매물 데이터 수신
- BE-5와 협업: 검색 결과를 LLM에 전달할 포맷 논의

---

#### BE-4 (Async & Queue - 승연)
**핵심 목표:** 개발 환경 구축 및 RabbitMQ 세팅

**세부 태스크:**
- [ ] Docker Compose 파일 작성 (PostgreSQL, RabbitMQ, Redis) (D-1 ~ D-2)
- [ ] RabbitMQ 기본 설정 및 테스트 (D-3 ~ D-4)
- [ ] Producer/Consumer 예제 코드 작성 (D-5 ~ D-6)
- [ ] 비동기 Task Queue 구조 설계 (D-6 ~ D-7)
- [ ] 팀원들에게 개발 환경 세팅 가이드 제공 (D-7)

**산출물:**
- `docker-compose.yml`
- `queue_producer.py`, `queue_consumer.py`
- 개발 환경 세팅 가이드 (README.md)

**협업 포인트:**
- BE-1과 협업: DB 스키마 공유
- BE-6과 협업: CI/CD 파이프라인 기초 논의

---

#### BE-5 (Prompt Eng - 효진)
**핵심 목표:** 페르소나 설계 및 프롬프트 프로토타입 작성

**세부 태스크:**
- [ ] "학교 선배" 페르소나 정의 (톤앤매너, 말투) (D-1 ~ D-2)
- [ ] 시나리오별 프롬프트 템플릿 작성 (D-3 ~ D-5)
  - 매물 추천 이유 설명
  - 리스크 경고 문구
  - 계약 전 주의사항
- [ ] OpenAI API 연동 및 프롬프트 테스트 (D-5 ~ D-7)
- [ ] 프롬프트 버전 관리 시스템 설계 (D-7)

**산출물:**
- `prompts/` 디렉토리 (템플릿 파일들)
- `llm_service.py` (LLM 호출 모듈)
- 페르소나 가이드 문서

**협업 포인트:**
- BE-2와 협업: 리스크 Score를 자연어로 변환하는 프롬프트
- BE-3와 협업: 검색 결과를 설명하는 프롬프트
- **BE-1과 협업: 챗봇용 프롬프트 설계 및 제공** ⭐ 신규

---

#### BE-6 (Infra & CI/CD - 재현)
**핵심 목표:** 배포 환경 구축 및 CI/CD 기초 세팅

**세부 태스크:**
- [ ] Git Repository 구조 설계 (D-1)
- [ ] Docker 기반 개발 환경 구축 지원 (D-2 ~ D-3)
- [ ] GitHub Actions 기초 CI 설정 (Lint, Test) (D-4 ~ D-6)
- [ ] 로깅 시스템 설정 (Python logging 설정) (D-6 ~ D-7)
- [ ] 개발 서버 배포 환경 준비 (D-7)

**산출물:**
- `.github/workflows/ci.yml`
- `docker/` 디렉토리 (Dockerfiles)
- 배포 가이드 문서

**협업 포인트:**
- BE-4와 협업: Docker Compose 리뷰
- 전체 팀: Git 브랜치 전략 공유

---

### 1주차 체크포인트 (D-7)
**전체 팀 회고 미팅 필수**

확인 사항:
- [ ] ERD가 확정되고 모두가 이해했는가?
- [ ] 각자의 개발 환경이 정상 동작하는가?
- [ ] 공공 데이터 API가 정상 연동되었는가?
- [ ] 테스트 데이터셋이 준비되었는가?

---

## 2주차: 핵심 기능 구현 & 중간 발표 준비 (D-8 ~ D-14)
**목표:** "가상 데이터라도 흐름(Flow)이 완벽하게 돌아가는 MVP"

### 전체 공통 목표
- [ ] **D-10**: 중간 발표 준비 (PPT, 데모 시나리오)
- [ ] **D-12**: 중간 발표 리허설
- [ ] **D-14**: 중간 발표 및 피드백 수렴, 2주차 회고

---

#### BE-1 (Team Lead - 다영)
**핵심 목표:** 전체 API 파이프라인 연결 + 매물별 챗봇 API 구현

**세부 태스크:**
- [ ] 임차인 요구사항 입력 API 구현 (D-8 ~ D-9)
- [ ] 추천 요청 API 구현 (비동기 Task 생성) (D-10 ~ D-11)
- [ ] Task 상태 조회 API 구현 (D-11 ~ D-12)
- [ ] 추천 결과 조회 API 구현 (D-12 ~ D-13)
- [ ] **챗봇 API 구현** (D-12 ~ D-14) ⭐ 신규
  - 매물별 챗봇 대화 API
  - 사용자 질문 → LLM 응답 파이프라인
  - 대화 히스토리 관리 (선택)
- [ ] 팀원 코드 리뷰 및 API 통합 테스트 (D-13 ~ D-14)

**산출물:**
- `/api/requests/*` 엔드포인트
- `/api/recommendations/*` 엔드포인트
- `/api/chatbot/*` 엔드포인트 ⭐ 신규
- 통합 테스트 케이스

**중간 발표 기여:**
- API Flow 시연 (Postman or Swagger)
- **챗봇 기능 시연** ⭐

---

#### BE-2 (Risk Eng - 용준)
**핵심 목표:** 리스크 분석 로직 실제 구현

**세부 태스크:**
- [ ] 건축물대장 위반 여부 체크 로직 (D-8 ~ D-9)
- [ ] 실거래가 대비 가격 이탈 분석 (D-10 ~ D-11)
- [ ] 내진설계, 사용승인일 체크 로직 (D-11 ~ D-12)
- [ ] 리스크 Score 계산 알고리즘 구현 (D-12 ~ D-13)
- [ ] 샘플 매물 100개로 테스트 (D-13 ~ D-14)

**산출물:**
- `risk_analysis/` 모듈
- 리스크 평가 결과 JSON 샘플
- 100개 매물 리스크 분석 결과

**중간 발표 기여:**
- 리스크 분석 로직 설명 (Before/After 예시)

---

#### BE-3 (RAG Core - 장훈)
**핵심 목표:** RAG 검색 파이프라인 완성

**세부 태스크:**
- [ ] 임차인 요구사항 → 쿼리 벡터 생성 (D-8 ~ D-9)
- [ ] 하드 필터링 (지역, 가격) + 벡터 검색 조합 (D-10 ~ D-11)
- [ ] Top-K 매물 추출 로직 구현 (D-11 ~ D-12)
- [ ] 검색 결과에 근거 데이터 추가 (왜 이 집이 맞는지) (D-12 ~ D-13)
- [ ] 검색 성능 최적화 (응답 시간 < 2초) (D-13 ~ D-14)

**산출물:**
- `rag_pipeline.py` (완성본)
- 검색 결과 샘플 (JSON)
- 성능 테스트 결과

**중간 발표 기여:**
- 검색 정확도 시연 (쿼리 → 추천 결과)

---

#### BE-4 (Async & Queue - 승연)
**핵심 목표:** 비동기 처리 파이프라인 구현

**세부 태스크:**
- [ ] 추천 요청을 RabbitMQ에 전송하는 Producer 구현 (D-8 ~ D-9)
- [ ] RAG + Risk + LLM을 실행하는 Consumer Worker 구현 (D-10 ~ D-12)
- [ ] Task 상태 관리 (pending/processing/completed/failed) (D-12 ~ D-13)
- [ ] 에러 핸들링 및 Retry 로직 (D-13 ~ D-14)
- [ ] 전체 파이프라인 통합 테스트 (D-14)

**산출물:**
- `async_worker.py` (Worker 완성본)
- Task Queue 모니터링 대시보드 (선택)

**중간 발표 기여:**
- 비동기 처리 흐름도 설명

---

#### BE-5 (Prompt Eng - 효진)
**핵심 목표:** 프롬프트 실전 적용 및 답변 생성

**세부 태스크:**
- [ ] BE-2(리스크) + BE-3(검색) 데이터를 받아 LLM 입력 생성 (D-8 ~ D-9)
- [ ] 추천 이유 설명 프롬프트 최적화 (D-10 ~ D-11)
- [ ] 리스크 경고 문구 자동 생성 (D-11 ~ D-12)
- [ ] **챗봇용 Q&A 프롬프트 설계** (D-12 ~ D-13) ⭐ 신규
  - 매물 정보 기반 질문 답변 프롬프트
  - "학교 선배" 페르소나 적용
  - 빠른 응답용 템플릿 (근처 편의점, 리스크 등)
- [ ] "학교 선배" 톤앤매너 적용 (D-12 ~ D-13)
- [ ] 다양한 시나리오 테스트 (최소 20개 케이스) (D-13 ~ D-14)

**산출물:**
- `prompt_templates/` (v1.0)
- `prompt_templates/chatbot/` ⭐ 신규
- LLM 응답 샘플 20개
- 챗봇 Q&A 샘플 10개 ⭐ 신규
- 프롬프트 성능 평가 보고서

**중간 발표 기여:**
- AI 답변 품질 시연 (실제 응답 예시)
- **챗봇 대화 시연** ⭐ 신규

---

#### BE-6 (Infra & CI/CD - 재현)
**핵심 목표:** 중간 발표용 데모 환경 안정화

**세부 태스크:**
- [ ] 개발 서버 배포 자동화 (D-8 ~ D-10)
- [ ] 로그 수집 및 모니터링 설정 (D-10 ~ D-11)
- [ ] 중간 발표용 데모 환경 세팅 (D-11 ~ D-12)
- [ ] 팀원들 코드 통합 지원 (D-12 ~ D-13)
- [ ] 발표 PPT 기술 파트 작성 지원 (D-13 ~ D-14)

**산출물:**
- 배포된 개발 서버 URL
- 모니터링 대시보드
- 중간 발표 PPT (기술 파트)

**중간 발표 기여:**
- 시스템 아키텍처 설명

---

### 2주차 체크포인트 (D-14 - 중간 발표)
**중간 발표 핵심 메시지:**
> "가상 데이터지만, 실제 작동하는 Flow를 보여주세요!"

**시연 시나리오:**
1. 임차인이 요구사항 입력 (예: "마포구, 전세 5000만원, 방 2개")
2. 시스템이 매물 검색 + 리스크 분석 (Loading...)
3. AI가 추천 이유 + 리스크 경고 설명
4. 결과 화면 출력 (Top 3 매물)
5. **매물 상세 → 챗봇 대화 시연** ⭐ 신규
   - "근처에 편의점 있어?"
   - "전세사기 위험은 없어?"

**발표 후 피드백 수렴:**
- 어떤 부분이 부족한가?
- 3~4주차에 집중할 부분은?
- **챗봇 응답 품질은 어떤가?** ⭐

---

## 💬 챗봇 기능 상세 스펙

### 챗봇 아키텍처 (BE-1 다영 담당)

**API 엔드포인트:**
```
POST /api/chatbot/{property_id}/message
- Request: { "message": "근처에 편의점 있어?" }
- Response: { 
    "reply": "네! 도보 2분 거리에 CU가 있어요.",
    "quick_replies": ["주차 가능해?", "학교 거리는?"]
  }

GET /api/chatbot/{property_id}/history (선택)
- Response: { "messages": [...] }
```

**처리 흐름:**
1. 프론트엔드에서 사용자 메시지 전송
2. BE-1이 메시지 수신 + 매물 정보 조회
3. BE-5의 챗봇 프롬프트로 LLM 호출
4. LLM 응답을 프론트엔드로 반환

**프롬프트 설계 (BE-5 효진 담당):**
```
시스템: 너는 대학생의 첫 자취를 돕는 친절한 선배야.
        매물 정보를 기반으로 질문에 답변해줘.

매물 정보:
- 주소: 마포구 신정동 123-45
- 가격: 전세 7000만원
- 근처 편의시설: CU (도보 2분), 이마트24 (도보 5분)
- 리스크: 건축물대장 위반 없음, 실거래가 대비 적정

사용자: 근처에 편의점 있어?
AI: 네! 도보 2분 거리에 CU가 있고, 5분 거리에 이마트24도 있어.
```

**빠른 질문 템플릿:**
- "근처 편의점 있어?"
- "전세사기 위험은 없어?"
- "학교까지 얼마나 걸려?"
- "주차 가능해?"
- "관리비는 얼마야?"

### 프론트엔드 챗봇 컴포넌트 (재현 담당)

**ChatbotModal.tsx:**
```typescript
interface ChatbotModalProps {
  isOpen: boolean
  propertyId: string
  onClose: () => void
}

const ChatbotModal: React.FC<ChatbotModalProps> = ({ 
  isOpen, 
  propertyId, 
  onClose 
}) => {
  const [messages, setMessages] = useState([])
  const [inputValue, setInputValue] = useState('')
  const [loading, setLoading] = useState(false)

  const sendMessage = async (text: string) => {
    setLoading(true)
    const response = await chatbotAPI.sendMessage(propertyId, text)
    setMessages([...messages, 
      { role: 'user', text },
      { role: 'ai', text: response.reply }
    ])
    setLoading(false)
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose}>
      <ChatHeader>💬 AI 선배에게 물어보기</ChatHeader>
      <ChatMessages>
        {messages.map((msg, idx) => (
          <ChatBubble key={idx} role={msg.role}>
            {msg.text}
          </ChatBubble>
        ))}
        {loading && <TypingIndicator />}
      </ChatMessages>
      <QuickReplies>
        <QuickButton onClick={() => sendMessage('근처 편의점?')}>
          근처 편의점?
        </QuickButton>
        <QuickButton onClick={() => sendMessage('리스크는?')}>
          리스크는?
        </QuickButton>
      </QuickReplies>
      <ChatInput
        value={inputValue}
        onChange={(e) => setInputValue(e.target.value)}
        onEnter={() => sendMessage(inputValue)}
      />
    </Modal>
  )
}
```

**UI 요구사항:**
- 모달 형태 (또는 우측 하단 팝업)
- 대화 말풍선 (사용자: 우측, AI: 좌측)
- Typing 애니메이션 (AI 응답 대기 중)
- 빠른 질문 버튼 (Quick Replies)
- 스크롤 자동 하단 이동
- 모바일 반응형

---

## 3주차: 고도화 및 최적화 (D-15 ~ D-21)
**목표:** "실제 데이터 연동 및 성능 개선"

### 전체 공통 목표
- [ ] **D-21**: 3주차 회고 미팅 (최종 발표 준비 상태 점검)

---

#### BE-1 (Team Lead - 다영)
**핵심 목표:** 임대인 기능 추가, 챗봇 고도화, 전체 API 안정화

**세부 태스크:**
- [ ] 임대인 매물 등록 API 구현 (D-15 ~ D-17)
- [ ] **챗봇 기능 고도화** (D-15 ~ D-17) ⭐
  - 대화 히스토리 저장 (선택)
  - 빠른 질문 답변 최적화
  - 응답 속도 개선 (<2초)
- [ ] 임차인-임대인 매칭 로직 (선택) (D-17 ~ D-19)
- [ ] API 에러 핸들링 강화 (D-19 ~ D-20)
- [ ] 전체 API 통합 테스트 (D-20 ~ D-21)
- [ ] API 문서 최종 업데이트 (D-21)

**산출물:**
- `/api/properties/*` 엔드포인트 (임대인)
- `/api/chatbot/*` 고도화 버전 ⭐
- 통합 테스트 케이스 (100% 커버리지 목표)

---

#### BE-2 (Risk Eng - 용준)
**핵심 목표:** 실제 데이터 기반 리스크 분석 고도화

**세부 태스크:**
- [ ] 융자금 정보 추가 (가능한 경우) (D-15 ~ D-16)
- [ ] 시세 비교 로직 정교화 (D-16 ~ D-18)
- [ ] 리스크 설명 문구 개선 (BE-5와 협업) (D-18 ~ D-19)
- [ ] 실제 매물 100개 리스크 재분석 (D-19 ~ D-20)
- [ ] 리스크 분석 정확도 검증 (D-20 ~ D-21)

**산출물:**
- 고도화된 리스크 분석 로직
- 100개 매물 최종 리스크 리포트

---

#### BE-3 (RAG Core - 장훈)
**핵심 목표:** 검색 품질 및 설명 근거 강화

**세부 태스크:**
- [ ] 검색 결과에 "왜 추천하는지" 근거 데이터 보강 (D-15 ~ D-17)
- [ ] 하이브리드 검색 가중치 튜닝 (D-17 ~ D-19)
- [ ] 검색 속도 최적화 (인덱싱 개선) (D-19 ~ D-20)
- [ ] Edge Case 테스트 (조건 없음, 결과 없음 등) (D-20 ~ D-21)
- [ ] 검색 품질 평가 (사용자 시나리오 10개) (D-21)

**산출물:**
- 검색 품질 향상 보고서
- 근거 데이터 포함한 검색 결과

---

#### BE-4 (Async & Queue - 승연)
**핵심 목표:** 응답 속도 개선 (목표 < 5초)

**세부 태스크:**
- [ ] Worker 병렬 처리 최적화 (D-15 ~ D-17)
- [ ] 캐싱 전략 도입 (Redis) (D-17 ~ D-19)
- [ ] Dead-letter Queue 설정 (D-19 ~ D-20)
- [ ] 성능 부하 테스트 (동시 요청 10개) (D-20 ~ D-21)
- [ ] 응답 시간 모니터링 (D-21)

**산출물:**
- 성능 테스트 결과 (목표: 평균 < 5초)
- 캐싱 전략 문서

---

#### BE-5 (Prompt Eng - 효진)
**핵심 목표:** 프롬프트 튜닝 및 친절도 강화

**세부 태스크:**
- [ ] "대학생 선배" 말투 개선 (더 친근하게) (D-15 ~ D-17)
- [ ] 리스크 설명의 구체성 향상 (D-17 ~ D-19)
- [ ] 다양한 상황별 프롬프트 추가 (D-19 ~ D-20)
  - 좋은 매물일 때
  - 위험한 매물일 때
  - 애매한 매물일 때
- [ ] A/B 테스트 (프롬프트 버전 비교) (D-20 ~ D-21)
- [ ] 최종 프롬프트 확정 (D-21)

**산출물:**
- 프롬프트 v2.0
- A/B 테스트 결과

---

#### BE-6 (Infra & CI/CD - 재현)
**핵심 목표:** 로딩 애니메이션 및 모니터링 강화

**세부 태스크:**
- [ ] 프론트엔드 로딩 UI 지원 (API 연동) (D-15 ~ D-17)
- [ ] 리스크 시각화 차트 API 설계 (D-17 ~ D-18)
- [ ] Sentry 에러 트래킹 설정 (D-18 ~ D-19)
- [ ] 성능 모니터링 대시보드 구축 (D-19 ~ D-20)
- [ ] 최종 발표용 배포 환경 안정화 (D-20 ~ D-21)

**산출물:**
- 모니터링 대시보드 (Grafana or 간단한 대시보드)
- 배포 환경 최종 점검 체크리스트

---

### 3주차 체크포인트 (D-21)
확인 사항:
- [ ] 실제 데이터 100개가 정상 작동하는가?
- [ ] 평균 응답 속도가 5초 이내인가?
- [ ] 리스크 분석이 정확한가?
- [ ] AI 답변이 친절하고 이해하기 쉬운가?

---

## 4주차: 안정화 및 최종 발표 (D-22 ~ D-28)
**목표:** "완성도 높은 최종 발표 및 서비스 안정화"

### 전체 공통 목표
- [ ] **D-25**: 최종 발표 리허설 1차
- [ ] **D-27**: 최종 발표 리허설 2차
- [ ] **D-28**: 최종 발표 및 프로젝트 완료

---

#### BE-1 (Team Lead - 해인)
**핵심 목표:** 최종 버그 수정 및 QA

**세부 태스크:**
- [ ] 전체 시스템 통합 테스트 (D-22 ~ D-24)
- [ ] 버그 수정 및 예외 처리 강화 (D-24 ~ D-26)
- [ ] API 성능 최종 점검 (D-26 ~ D-27)
- [ ] 최종 발표 시연 준비 (시나리오 작성) (D-27)
- [ ] 발표 당일 기술 지원 (D-28)

**산출물:**
- QA 체크리스트 (완료)
- 최종 발표 시연 시나리오

**최종 발표 기여:**
- 시스템 전체 Flow 시연

---

#### BE-2 (Risk Eng - 용준)
**핵심 목표:** 리스크 데이터 최종 검증

**세부 태스크:**
- [ ] 실제 매물 Sample 50~100개 최종 점검 (D-22 ~ D-24)
- [ ] 리스크 분석 결과 시각화 데이터 준비 (D-24 ~ D-26)
- [ ] Edge Case 처리 (데이터 없을 때 등) (D-26 ~ D-27)
- [ ] 발표 자료에 리스크 분석 예시 추가 (D-27)
- [ ] 최종 발표 지원 (D-28)

**산출물:**
- 리스크 분석 결과 시각화 자료
- Before/After 비교 슬라이드

**최종 발표 기여:**
- "왜 이 서비스가 대학생에게 필요한가?" 데이터 근거 제시

---

#### BE-3 (RAG Core - 장훈)
**핵심 목표:** 검색 품질 최종 점검

**세부 태스크:**
- [ ] 최종 검색 성능 테스트 (D-22 ~ D-24)
- [ ] 검색 결과 품질 검증 (정성 평가) (D-24 ~ D-26)
- [ ] 발표용 검색 결과 Best Case 선정 (D-26 ~ D-27)
- [ ] 발표 자료 작성 지원 (검색 품질 파트) (D-27)
- [ ] 최종 발표 지원 (D-28)

**산출물:**
- 검색 품질 평가 결과
- Best Case 검색 결과 샘플

**최종 발표 기여:**
- "AI가 어떻게 추천하는가?" 설명

---

#### BE-4 (Async & Queue - 승연)
**핵심 목표:** 성능 안정화 및 모니터링

**세부 태스크:**
- [ ] 부하 테스트 (동시 요청 20개) (D-22 ~ D-24)
- [ ] 병목 지점 파악 및 최적화 (D-24 ~ D-26)
- [ ] 발표 당일 시스템 모니터링 준비 (D-26 ~ D-27)
- [ ] 장애 대응 매뉴얼 작성 (D-27)
- [ ] 발표 당일 기술 지원 (D-28)

**산출물:**
- 성능 테스트 최종 결과
- 장애 대응 매뉴얼

**최종 발표 기여:**
- 시스템 안정성 설명

---

#### BE-5 (Prompt Eng - 효진)
**핵심 목표:** 최종 프롬프트 확정 및 발표 자료

**세부 태스크:**
- [ ] 최종 프롬프트 버전 확정 (D-22 ~ D-24)
- [ ] 발표용 AI 답변 Best Case 선정 (D-24 ~ D-26)
- [ ] 발표 자료 작성 (AI 답변 품질 파트) (D-26 ~ D-27)
- [ ] 발표 리허설 참여 (D-27)
- [ ] 최종 발표 지원 (D-28)

**산출물:**
- 최종 프롬프트 v3.0
- AI 답변 Best Case 10개

**최종 발표 기여:**
- "AI가 어떻게 설명하는가?" 시연

---

#### BE-6 (Infra & CI/CD - 재현)
**핵심 목표:** 최종 발표 환경 완벽 준비

**세부 태스크:**
- [ ] 발표용 배포 환경 최종 점검 (D-22 ~ D-24)
- [ ] 백업 및 복구 계획 수립 (D-24 ~ D-25)
- [ ] 발표 PPT 최종 정리 (D-25 ~ D-27)
- [ ] 발표 리허설 2회 진행 (D-27)
- [ ] 발표 당일 기술 총괄 (D-28)

**산출물:**
- 최종 발표 PPT (완성본)
- 백업 계획서

**최종 발표 기여:**
- 전체 시스템 아키텍처 설명

---

### 4주차 최종 발표 (D-28)

#### 발표 전략: Before/After 시나리오

**Before (기존 방식):**
- 대학생 A는 직방, 다방을 보지만 어떤 집이 좋은지 모름
- 중개인을 믿어야 하지만 불안함
- 계약 후 문제 발생 (전세사기, 건축물 위반 등)

**After (본 서비스):**
- 대학생 A가 조건 입력 (마포구, 전세 5000만원)
- AI가 Top 3 매물 추천 + 이유 설명
- **리스크 경고**: "이 집은 건축물대장 위반 이력이 있습니다"
- A는 안심하고 계약 진행

#### 발표 시연 시나리오 (5분)

1. **문제 제기** (1분)
   - 대학생의 Pain Point
   - 기존 서비스의 한계

2. **솔루션 소개** (1분)
   - 우리 서비스의 차별점
   - 핵심 기능 3가지

3. **실제 시연** (2분)
   - 요구사항 입력
   - AI 추천 결과 (이유 + 리스크)
   - Before/After 비교

4. **기술 설명** (1분)
   - RAG + 공공데이터 + LLM
   - 시스템 아키텍처

5. **결론 및 향후 계획** (30초)
   - KR 달성 여부
   - Phase 2 계획

---

## 📊 주차별 산출물 체크리스트

### 1주차 산출물
- [ ] ERD 확정본
- [ ] Docker Compose 환경
- [ ] 공공 API 연동 테스트 결과
- [ ] 샘플 데이터 50개
- [ ] 기본 인증 API
- [ ] pgvector 세팅 완료

### 2주차 산출물
- [ ] 전체 API Flow 완성
- [ ] RAG 검색 파이프라인
- [ ] 리스크 분석 로직
- [ ] 비동기 처리 시스템
- [ ] LLM 프롬프트 v1.0
- [ ] **챗봇 API 및 UI** ⭐ 신규
- [ ] 중간 발표 PPT 및 데모

### 3주차 산출물
- [ ] 실제 데이터 100개 적재
- [ ] 응답 속도 < 5초 달성
- [ ] 프롬프트 v2.0 (친절도 향상)
- [ ] 리스크 시각화
- [ ] 성능 테스트 결과

### 4주차 산출물
- [ ] 통합 테스트 완료
- [ ] 버그 수정 완료
- [ ] 최종 발표 PPT
- [ ] 시연 시나리오
- [ ] 프로젝트 회고 문서

---

## 🚨 리스크 관리 및 대응 전략

### 기술적 리스크

#### 리스크 1: 공공 API 응답 느림 또는 장애
- **대응**: 캐싱 전략 (Redis), 주기적 데이터 수집 후 DB 저장
- **담당**: BE-2 (용준), BE-4 (승연)

#### 리스크 2: RAG 검색 정확도 낮음
- **대응**: 하이브리드 검색 (키워드 + 벡터), 가중치 튜닝
- **담당**: BE-3 (장훈)

#### 리스크 3: LLM 응답 품질 낮음
- **대응**: 프롬프트 A/B 테스트, 페르소나 지속 개선
- **담당**: BE-5 (효진)

#### 리스크 4: 비동기 처리 병목
- **대응**: Worker 스케일링, 캐싱, 성능 프로파일링
- **담당**: BE-4 (승연)

### 일정 리스크

#### 리스크 5: 중간 발표 준비 부족
- **대응**: D-10부터 데모 시나리오 작성, 리허설 필수
- **담당**: 전체 팀

#### 리스크 6: 최종 발표 당일 장애
- **대응**: 백업 환경 준비, 사전 점검 2회, 매뉴얼 작성
- **담당**: BE-6 (재현), BE-1 (해인)

### 팀워크 리스크

#### 리스크 7: 팀원 간 소통 부족
- **대응**: 매주 회고 미팅, Slack/Discord 활용, 일일 스탠드업 (선택)
- **담당**: BE-1 (해인)

#### 리스크 8: 작업 의존성 블로킹
- **대응**: Mock 데이터 우선 사용, 병렬 작업 최대화
- **담당**: 전체 팀

---

## 📞 협업 및 소통 전략

### 일일 스탠드업 (선택)
- **시간**: 매일 오전 10시 (15분)
- **내용**: 어제 한 일, 오늘 할 일, 블로킹 이슈

### 주간 회고 미팅 (필수)
- **시간**: 매주 토요일 오후 2시 (1시간)
- **내용**: 주간 목표 달성 여부, 다음 주 계획, 개선 사항

### 코드 리뷰
- **방식**: Pull Request 기반
- **리뷰어**: BE-1 (해인) 필수, 관련 팀원 1명 추가
- **기준**: 24시간 내 리뷰 완료

### 문서화
- **Wiki**: 기술 스펙, API 문서, 의사결정 기록
- **README**: 설치 가이드, 실행 방법
- **CHANGELOG**: 주요 변경 사항 기록

---

## 🎯 최종 목표 달성 지표

### KR1: 대학생이 "이 집이 나에게 맞는다"는 연결 경험
- **측정**: 최종 발표 시연 성공 여부
- **목표**: 시연 시나리오 3개 모두 성공

### KR2: 평균 추천 응답 속도 < 5초
- **측정**: 성능 테스트 결과
- **목표**: 평균 4.5초 이내

### KR3: 중간 발표 Flow 시연 성공
- **측정**: 중간 발표 피드백
- **목표**: "Flow가 명확하다" 평가 받기

### KR4: 최종 발표 Before/After 시나리오 시연
- **측정**: 최종 발표 완성도
- **목표**: 청중이 "이해했다" 반응

---

## 📚 참고 자료 및 문서

### 기술 문서
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [pgvector GitHub](https://github.com/pgvector/pgvector)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [RabbitMQ Tutorial](https://www.rabbitmq.com/tutorials)

### 공공 데이터
- [국토교통부 실거래가 API](https://www.data.go.kr/)
- [건축물대장 정보 API](https://www.data.go.kr/)

### 프로젝트 문서
- `PRD.md`: 제품 요구사항 정의서
- `ERD.md`: 데이터베이스 스키마
- `API_SPEC.md`: API 명세서
- `ARCHITECTURE.md`: 시스템 아키텍처

---

## ✅ 주차별 체크리스트 요약

### 1주차 (D-0 ~ D-7)
- [ ] ERD 확정
- [ ] 개발 환경 세팅
- [ ] 공공 API 연동
- [ ] 테스트 데이터 50개
- [ ] 기본 기능 뼈대

### 2주차 (D-8 ~ D-14)
- [ ] 전체 Flow 완성
- [ ] 중간 발표 성공
- [ ] RAG + Risk + LLM 통합
- [ ] 비동기 처리 구현

### 3주차 (D-15 ~ D-21)
- [ ] 실제 데이터 100개
- [ ] 응답 속도 < 5초
- [ ] 프롬프트 최적화
- [ ] 성능 테스트 완료

### 4주차 (D-22 ~ D-28)
- [ ] 버그 수정 완료
- [ ] 최종 발표 준비
- [ ] 시연 시나리오 완성
- [ ] 프로젝트 완료 🎉

---
