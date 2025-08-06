# NXTCloud IAM 사용자 생성기

교육마다 다수 IAM USER를 생성해야하는  
Nxtcloud 교육팀을 위해  
AWS IAM 사용자를 대량으로 생성하고  
관리할 수 있는 **Streamlit 웹 애플리케이션**과 **CloudFormation 템플릿**을 제공합니다.

## 🌟 주요 기능

### 📱 Streamlit 웹 애플리케이션

- **보안 인증**: 비밀번호 기반 접근 제어
- **직관적인 UI**: 한국어 인터페이스와 이모지를 활용한 사용자 친화적 디자인
- **실시간 미리보기**: 생성될 사용자 목록을 미리 확인
- **계정 정보 생성**: 복사 가능한 마크다운 형식의 계정 안내서 자동 생성
- **스택 관리**: 생성된 CloudFormation 스택의 상태 확인 및 삭제
- **한국 시간 지원**: 모든 생성 일시는 KST(Asia/Seoul) 기준

### ⚙️ CloudFormation 템플릿

- **IAM 그룹 생성**: 사용자 지정 이름의 IAM 그룹
- **고정된 5개 IAM 정책** 자동 연결 : `필요시 arn 추가`
- **연속 번호 사용자 생성**: groupname-00부터 groupname-XX까지
- **초기 비밀번호 설정**: 최초 로그인 시 변경 강제
- **Lambda 함수**: 사용자 생성을 담당하는 커스텀 리소스

## 🏗️ 프로젝트 구조

```
iamuser/
├── app.py                           # Streamlit 웹 애플리케이션
├── nxtcloud-iamuser-template.yaml   # CloudFormation 템플릿 (자동 생성)
├── generate-template.py             # 템플릿 생성기 (환경변수 기반)
├── requirements.txt                 # Python 의존성
├── README.md                        # 프로젝트 문서
├── .env                             # 환경변수 설정 파일 (Git에서 제외)
├── .gitignore                       # Git 제외 파일 목록
└── stack_info.json                  # 스택 정보 저장 파일 (자동 생성)
```

## 🚀 설치 및 실행

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. 환경변수 설정

`.env` 파일을 생성하고 필요한 환경변수를 설정하세요:

```bash
# 예시 .env 파일
ADMIN_PASSWORD=your_admin_password
DEFAULT_USER_PASSWORD=your_default_password
AWS_CONSOLE_URL=https://your-org.signin.aws.amazon.com/console
AWS_ACCOUNT_ID=your_account_id
# ... 기타 정책 ARN 설정
```

**⚠️ 보안 주의사항**: `.env` 파일에는 민감한 정보가 포함되어 있으므로 Git에 커밋하지 마세요!

### 3. CloudFormation 템플릿 생성

환경변수 기반으로 템플릿을 생성하세요:

```bash
python3 generate-template.py
```

### 4. AWS CLI 설정(공용 cloud9 사용시 생략)

```bash
aws configure
```

### 5. Streamlit 앱 실행

```bash
streamlit run app.py
```

### 6. 웹 브라우저에서 접속

- 기본 주소: `http://localhost:8501`

## 📋 사용 방법

### 🎯 기본 워크플로우

1. **인증**: 비밀번호 입력하여 로그인
2. **생성 탭**:
   - 생성자 선택 (이정훈, 김유림, 김도겸, 이성용)
   - 그룹명 입력 (영문, 숫자, 하이픈, 언더스코어 사용 가능)
   - 최대 사용자 번호 설정 (1-100)
   - "계정 정보 생성" 버튼 클릭
   - 생성된 마크다운 내용 복사
   - "CloudFormation 스택 배포 실행" 버튼 클릭
3. **관리 탭**:
   - 생성된 스택 목록 확인 (최신순 정렬)
   - 스택 상태 확인
   - 필요시 스택 삭제

### 📄 생성되는 계정 정보 문서

웹 앱에서 자동 생성되는 마크다운 문서에는 다음이 포함됩니다:

- AWS Console 로그인 링크 (환경변수에서 설정)
- 초기 비밀번호 정보 (환경변수에서 설정)
- 생성된 계정 목록 테이블
- 상세한 사용 안내
- 그룹 정보 요약

## 🔧 IAM 정책 설정

템플릿에서 자동으로 연결되는 정책들은 환경변수를 통해 설정됩니다:

- `POLICY_ARN_ALLOW_NON_OVERKILL`
- `POLICY_ARN_IAM_BASIC_ACCESS`
- `POLICY_ARN_SAFE_POWER_USER`
- `POLICY_ARN_CONTROL_OWN_RESOURCES`
- `POLICY_ARN_RESTRICT_REGION_VIRGINIA`

각 정책 ARN은 `.env` 파일에서 조직의 AWS 계정에 맞게 설정해야 합니다.

## 📊 생성자 및 관리

### 지정된 생성자 목록

- 이정훈
- 김유림
- 김도겸
- 이성용

### 스택 정보 관리

- **저장 방식**: JSON 파일 (`stack_info.json`)
- **저장 정보**: 스택명, 그룹명, 사용자 수, 생성자, 생성일시(KST), 스택 ID
- **정렬**: 최신 생성 순서로 표시

## 🔐 보안 및 권한

### 필요한 AWS 권한

- IAM 그룹/사용자 생성 권한
- Lambda 함수 생성 권한
- CloudFormation 실행 권한

### 앱 보안 기능

- 비밀번호 기반 인증 (환경변수로 설정)
- 세션 상태 관리
- 로그아웃 기능

## 📋 파라미터 및 제한사항

| 설정 항목 | 범위              | 기본값 | 설명                         |
| --------- | ----------------- | ------ | ---------------------------- |
| 그룹명    | 영문, 숫자, -, \_ | -      | CloudFormation 스택명에 사용 |
| 사용자 수 | 1-100             | 30     | 00번부터 지정 번호까지 생성  |
| 생성자    | 고정 4명          | 이정훈 | 스택 생성 책임자             |

## 🔧 고급 사용법

### 직접 CloudFormation 사용

Streamlit 앱 없이 AWS CLI로 직접 배포:

```bash
aws cloudformation create-stack \
  --stack-name nxtcloud-iamuser-students \
  --template-body file://nxtcloud-iamuser-template.yaml \
  --parameters \
    ParameterKey=GroupName,ParameterValue=students \
    ParameterKey=UserCount,ParameterValue=30 \
  --capabilities CAPABILITY_NAMED_IAM
```

### 스택 삭제

```bash
aws cloudformation delete-stack --stack-name nxtcloud-iamuser-students
```

## 📦 의존성

- `streamlit>=1.28.0`: 웹 애플리케이션 프레임워크
- `boto3>=1.26.0`: AWS SDK
- `pytz>=2023.3`: 한국 시간대 지원
- `python-dotenv`: 환경변수 관리

## 🔒 보안 개선사항

✅ **환경변수 분리**: 모든 민감한 정보를 .env 파일로 분리  
✅ **Git 보호**: .env 파일이 실수로 커밋되지 않도록 .gitignore 설정  
✅ **동적 템플릿**: CloudFormation 템플릿을 환경변수 기반으로 동적 생성  
✅ **계정 정보 보호**: AWS 계정 ID 및 정책 ARN을 환경변수로 관리  
✅ **비밀번호 보호**: 관리자 비밀번호와 초기 사용자 비밀번호 분리

## 🔄 생성 예시

30명의 학생 계정 생성 시:

- **그룹명**: students
- **생성되는 사용자**: students-00, students-01, ..., students-30 (총 31개)
- **초기 비밀번호**: 초기비밀번호
- **스택명**: nxtcloud-iamuser-students

## 💡 문제 해결

### 배포 실패 시 확인사항

1. AWS CLI가 설치되고 구성되어 있는지 확인
2. 적절한 IAM 권한이 있는지 확인
3. 템플릿 파일이 같은 디렉토리에 있는지 확인
4. 그룹명이 AWS 규칙에 맞는지 확인

### Streamlit 앱 문제

1. Python 의존성이 모두 설치되어 있는지 확인
2. 포트 8501이 사용 가능한지 확인
3. AWS 자격 증명이 올바르게 설정되어 있는지 확인

---

_이 프로젝트는 NXTCloud에서 IAM 사용자를 효율적으로 관리하기 위해 개발되었습니다._
