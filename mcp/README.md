# MCP PostgreSQL 데이터 초기화 프로젝트

## 🔧 환경 설정

### 1. 필수 패키지 설치

```bash
sudo yum install postgresql15 -y
pip3 install -r requirements.txt
```

### 2. 환경변수 설정

`.env` 파일을 생성하고 데이터베이스 연결 정보를 설정하세요:

```bash
cp .env .env.local  # .env 파일을 복사하여 로컬 설정으로 사용
```

**⚠️ 보안 주의사항**: `.env` 파일에는 민감한 정보가 포함되어 있으므로 Git에 커밋하지 마세요!

### 3. 데이터베이스 연결 테스트

````bash
psql -h $DB_HOST -u $DB_USER -d mcp4
# 또는 직접 연결
psql -h DATABASEHOST -u USER -d DBNAME

\dt
SELECT COUNT(_) FROM Customers;
SELECT COUNT(_) FROM Orders;
SELECT COUNT(_) FROM Campaigns;
SELECT COUNT(_) FROM Campaign_Performance;

SELECT \* FROM Customers LIMIT 5;

SELECT \* FROM Orders ORDER BY order_date DESC LIMIT 10;

- Orders 테이블에서 주문 내역을 최신 날짜 기준 내림차순 정렬
- 최근 5개의 주문을 가져옴 (LIMIT 10)

- 모두 같은 날짜(2025-06-13)에 주문됨 → 특정 프로모션일 가능성
- order_id 19: 29만 원 이상 주문 → 고가 제품 또는 대량 구매 추정
- 평균 주문금액도 상당히 높음 → 전체 고객의 소비력이나 제품 단가가 높은 편

SELECT \* FROM Orders WHERE customer_id = 349 LIMIT 10;

SELECT \* FROM Campaign_Performance WHERE campaign_id = 1 LIMIT 5;

- Campaign_Performance 테이블에서 campaign_id = 1인 캠페인의 성과 데이터를 조회
- LIMIT 5로 최대 5개의 행만 출력
- 날짜별로 impressions(노출), clicks(클릭), conversions(전환)을 기록

- 2025-05-16: 클릭 수는 9286로 매우 많지만, 전환은 172로 매우 낮음 → 효율이 낮은 클릭
- 2025-05-19: 클릭 수는 4615, 전환은 2653 → 전환율 약 **57%**로 매우 효율적
- 2025-05-18: 노출은 적지만 전환 수 대비 클릭이 적음 → 타겟이 정확했던 가능성

## 🚀 사용법

### 1. MCP 설정 파일 생성
```bash
python3 mcp-config-generator.py
````

### 2. 데이터 초기화 (모든 MCP 데이터베이스)

```bash
python3 mcp_data_initializer.py
```

### 3. 데이터 정리 (모든 테이블 비우기)

```bash
python3 cleanup-mcp-data.py
```

## 📁 파일 설명

- **`.env`**: 환경변수 설정 파일 (민감한 정보 포함, Git에서 제외됨)
- **`mcp_data_initializer.py`**: 모든 MCP 데이터베이스의 더미 데이터 생성
- **`cleanup-mcp-data.py`**: 모든 MCP 데이터베이스의 데이터 정리
- **`mcp-config-generator.py`**: 환경변수를 사용하여 mcp.json 설정 파일 동적 생성
- **`requirements.txt`**: 필요한 Python 패키지 목록
- **`.gitignore`**: Git에서 제외할 파일 목록

## 🔒 보안 개선사항

✅ **하드코딩 제거**: 모든 민감한 정보를 환경변수로 분리  
✅ **환경변수 보호**: .env 파일을 .gitignore에 추가  
✅ **동적 설정**: MCP 설정을 환경변수 기반으로 동적 생성  
✅ **기본값 제공**: 환경변수가 없을 때의 기본값 설정

## 🗃️ 데이터베이스 구조

### MCP1: 이커머스 & 마케팅 성과 분석

- Customers, Orders, Campaigns, Campaign_Performance

### MCP2: 금융/결제 거래 분석

- Users, Transactions, PaymentMethods

### MCP3: 금융 IT 서비스 로그 & 사용자 피드백 분석

- Users, UserActivity, Feedback

### MCP4: 공공 행정 & 문화-관광 사업 분석

- Employees, Projects, BudgetRequests, Events, SuppliesRequests

### MCP5: 학사 행정 관리

- Students, Professors, Courses, Enrollments, Attendance, Grades

```

```
