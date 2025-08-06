# 🌟 NXTCloud 교육팀 통합 컨트롤 시스템

> **NXTCloud 교육팀을 위한 AWS 리소스 관리 및 데이터 분석 도구 모음**

이 프로젝트는 NXTCloud 교육팀의 업무 효율성을 높이기 위한 다양한 도구들을 제공합니다. IAM 사용자 대량 생성, MCP 데이터베이스 관리, AWS 리소스 정리 등의 기능을 통합하여 교육 환경 구축과 관리를 자동화합니다.

## 📁 프로젝트 구조

```
Nxt-edu-control/
├── 📂 iamuser/                      # IAM 사용자 대량 생성 도구
│   ├── app.py                      # Streamlit 웹 애플리케이션
│   ├── generate-template.py        # CloudFormation 템플릿 생성기
│   ├── nxtcloud-iamuser-template.yaml  # 동적 생성 템플릿
│   ├── requirements.txt            # Python 의존성
│   ├── .env                        # 환경변수 (민감정보)
│   └── README.md                   # 상세 사용법
│
├── 📂 mcp/                          # MCP 데이터베이스 관리 도구
│   ├── mcp_data_initializer.py     # 더미 데이터 생성기
│   ├── cleanup-mcp-data.py         # 데이터 정리 도구
│   ├── mcp.json                    # MCP 서버 설정 (동적 생성)
│   ├── requirements.txt            # Python 의존성
│   ├── .env                        # 환경변수 (민감정보)
│   └── README.md                   # 상세 사용법
│
├── 📂 database-settings/            # 클래식 DB 환경 구축 도구
│   ├── classic-architecture-db.py  # MySQL/MariaDB 다중 DB 생성기
│   └── README.md                   # 상세 사용법
│
├── 📂 resourse-delete/              # AWS 리소스 정리 도구
│   ├── s3-delete.py                # S3 버킷 대량 삭제
│   └── lambda-delete.py            # Lambda 함수 대량 삭제
│
├── .gitignore                      # Git 제외 파일 목록
└── README.md                       # 프로젝트 전체 가이드 (이 파일)
```

## 🛠️ 주요 기능

### 🔐 **IAM 사용자 관리** (`iamuser/`)

- **대량 IAM 사용자 생성**: 교육용 AWS 계정을 한 번에 생성
- **Streamlit 웹 인터페이스**: 직관적인 한국어 UI
- **CloudFormation 자동화**: 스택 기반 사용자 관리
- **계정 정보 자동 생성**: 복사 가능한 마크다운 문서

### 📊 **MCP 데이터베이스 관리** (`mcp/`)

- **5개 시나리오 더미 데이터**: 이커머스, 금융, IT서비스, 공공행정, 학사관리
- **PostgreSQL 자동 연결**: RDS 데이터베이스 설정
- **MCP 서버 통합**: Claude Desktop과 연동
- **데이터 초기화/정리**: 교육 환경 빠른 리셋

### 🗄️ **클래식 DB 환경 구축** (`database-settings/`)

- **MySQL/MariaDB 다중 DB**: 교육용 개별 데이터베이스 대량 생성
- **사용자 계정 관리**: DB별 전용 사용자 및 권한 자동 설정
- **초기 데이터 삽입**: 명언 텍스트 포함 샘플 데이터 자동 생성
- **대량 처리**: 최대 56개 독립 데이터베이스 환경 구축

### 🧹 **리소스 정리** (`resourse-delete/`)

- **S3 버킷 대량 삭제**: 키워드 기반 일괄 정리
- **Lambda 함수 정리**: 교육 후 불필요한 함수 제거
- **안전한 삭제 확인**: 실수 방지를 위한 확인 절차

## 🚀 빠른 시작

### 1. 프로젝트 클론 및 설정

```bash
git clone <repository-url>
cd Nxt-edu-control
```

### 2. 각 모듈별 환경 설정

#### IAM 사용자 도구 설정

```bash
cd iamuser/
pip install -r requirements.txt

# .env 파일 생성 (예시)
cat > .env << EOF
ADMIN_PASSWORD=your_admin_password
DEFAULT_USER_PASSWORD=your_default_password
AWS_CONSOLE_URL=https://your-org.signin.aws.amazon.com/console
AWS_ACCOUNT_ID=your_account_id
POLICY_ARN_ALLOW_NON_OVERKILL=arn:aws:iam::your_account:policy/AllowNonOverkill
# ... 기타 정책 ARN들
EOF

# CloudFormation 템플릿 생성
python3 generate-template.py

# Streamlit 앱 실행
streamlit run app.py
```

#### MCP 데이터베이스 도구 설정

```bash
cd ../mcp/
pip install -r requirements.txt

# .env 파일 생성 (예시)
cat > .env << EOF
DB_HOST=your-rds-endpoint.amazonaws.com
DB_USER=postgres
DB_PASSWORD=your_db_password
DB_PORT=5432
# ... 기타 설정들
EOF

# 더미 데이터 생성
python3 mcp_data_initializer.py
```

#### 클래식 DB 환경 구축 도구 설정
```bash
cd ../database-settings/
pip install boto3 pymysql

# 스크립트 내 DB 연결 정보 수정 후 실행
python3 classic-architecture-db.py
```

#### 리소스 정리 도구 사용

```bash
cd ../resourse-delete/

# S3 버킷 정리 (키워드: "group-")
python3 s3-delete.py

# Lambda 함수 정리 (키워드: "group-")
python3 lambda-delete.py
```

## 🔒 보안 및 환경 관리

### 환경변수 관리

모든 민감한 정보는 `.env` 파일로 분리되어 있습니다:

- **AWS 계정 정보**: 계정 ID, 정책 ARN 등
- **데이터베이스 접속 정보**: 호스트, 비밀번호 등
- **애플리케이션 비밀번호**: 관리자 비밀번호 등

### Git 보안

- `.gitignore`를 통해 민감한 정보 보호
- `.env` 파일은 절대 커밋되지 않음
- 동적 생성 파일들도 Git에서 제외

### 권장 보안 실천사항

✅ 각 폴더의 `.env.example` 파일을 참고하여 환경변수 설정  
✅ 프로덕션 환경에서는 강력한 비밀번호 사용  
✅ AWS IAM 정책을 최소 권한 원칙에 따라 설정  
✅ 정기적으로 사용하지 않는 리소스 정리

## 📋 사용 시나리오

### 🎓 **교육 과정 시작 시**

1. **IAM 사용자 생성**: `iamuser/` 도구로 수강생 계정 일괄 생성
2. **데이터베이스 환경 구축**: 
   - **PostgreSQL 환경**: `mcp/` 도구로 Claude Desktop 연동 실습용 DB
   - **MySQL 환경**: `database-settings/` 도구로 개별 학습자 전용 DB
3. **계정 정보 배포**: 자동 생성된 마크다운 문서를 수강생에게 전달

### 📊 **데이터 분석 실습**

1. **MCP 서버 연결**: Claude Desktop과 PostgreSQL 데이터베이스 연동
2. **시나리오별 분석**: 5가지 업종별 데이터로 실전 분석 실습
3. **개별 DB 실습**: MySQL 환경에서 개인별 독립적인 SQL 학습
4. **데이터 리셋**: 필요시 `cleanup-mcp-data.py`로 초기화

### 🧹 **교육 과정 종료 후**

1. **IAM 정리**: CloudFormation 스택 삭제로 사용자 정리
2. **리소스 정리**: `resourse-delete/` 도구로 남은 리소스 제거
3. **비용 최적화**: 불필요한 AWS 리소스 완전 정리

## 🔧 기술 스택

### 프론트엔드

- **Streamlit**: 사용자 친화적 웹 인터페이스
- **HTML/CSS**: 커스텀 스타일링

### 백엔드

- **Python 3.9+**: 메인 개발 언어
- **boto3**: AWS SDK
- **psycopg2**: PostgreSQL 데이터베이스 연결
- **faker**: 더미 데이터 생성

### 인프라스트럭처

- **AWS CloudFormation**: 인프라 자동화
- **AWS RDS**: PostgreSQL 데이터베이스
- **AWS IAM**: 사용자 및 권한 관리
- **AWS Lambda**: 서버리스 함수

### 데이터 도구

- **MCP (Model Context Protocol)**: Claude Desktop 연동
- **PostgreSQL**: 관계형 데이터베이스 (MCP 연동)
- **MySQL/MariaDB**: 클래식 아키텍처 데이터베이스
- **PyMySQL**: MySQL 데이터베이스 연결

## 🤝 기여 가이드

### 개발 환경 설정

```bash
# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 의존성 설치
pip install -r requirements.txt
```

### 코드 스타일

- **Python**: PEP 8 준수
- **주석**: 한국어로 작성
- **함수명**: 영어, snake_case 사용
- **변수명**: 의미있는 이름 사용

### 보안 가이드라인

- 하드코딩된 민감 정보 금지
- 환경변수 사용 필수
- `.env` 파일 Git 커밋 금지
- AWS 권한은 최소 권한 원칙 적용

## 📞 지원 및 문의

### 개발팀

- **이정훈**: IAM 사용자 관리 도구
- **김유림**: MCP 데이터베이스 관리
- **김도겸**: 리소스 정리 도구
- **이성용**: 시스템 통합 및 보안

### 문제 해결

1. **각 모듈의 README.md** 참조
2. **환경변수 설정** 재확인
3. **AWS 권한** 확인
4. **로그 파일** 확인

## 📈 향후 계획

### v2.0 로드맵

- [ ] **추기기능 넣기**: 추가 기능 예정

---

> 💡 **팁**: 각 폴더의 상세한 사용법은 해당 폴더의 `README.md` 파일을 참조하세요!
