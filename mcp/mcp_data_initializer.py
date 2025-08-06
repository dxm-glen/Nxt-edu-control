import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from faker import Faker
import random
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# DB 접속 정보 (환경변수에서 로드)
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = os.getenv("DB_PORT", "5432")

# 공무원 더미 데이터 설정 (환경변수에서 로드)
NUM_CUSTOMERS = int(os.getenv("NUM_CUSTOMERS", 1000))
NUM_ORDERS = int(os.getenv("NUM_ORDERS", 5000))
NUM_CAMPAIGNS = int(os.getenv("NUM_CAMPAIGNS", 10))
NUM_FEEDBACKS = int(os.getenv("NUM_FEEDBACKS", 500))
NUM_TRANSACTIONS = int(os.getenv("NUM_TRANSACTIONS", 4000))
NUM_USERS = int(os.getenv("NUM_USERS", 800))
NUM_ACTIVITIES = int(os.getenv("NUM_ACTIVITIES", 3000))

# 학사 데이터 설정 (환경변수에서 로드)
NUM_STUDENTS = int(os.getenv("NUM_STUDENTS", 3000))  # 학생 수 (270명 장기결석자 = 9%)
NUM_PROFESSORS = int(os.getenv("NUM_PROFESSORS", 150))  # 교수 수
NUM_COURSES = int(os.getenv("NUM_COURSES", 200))  # 강좌 수
NUM_ENROLLMENTS = int(os.getenv("NUM_ENROLLMENTS", 15000))  # 수강신청 건수
NUM_ATTENDANCE_RECORDS = int(os.getenv("NUM_ATTENDANCE_RECORDS", 100000))  # 출석 기록

# Faker 설정 (환경변수에서 로케일 로드)
faker_locale = os.getenv("FAKER_LOCALE", "ko_KR")
faker = Faker(faker_locale)


def create_database_if_not_exists(dbname):
    conn = psycopg2.connect(
        host=DB_HOST, dbname="postgres", user=DB_USER, password=DB_PASSWORD
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (dbname,))
    exists = cur.fetchone()
    if not exists:
        cur.execute(f"CREATE DATABASE {dbname}")
        print(f"✅ 데이터베이스 생성됨: {dbname}")
    else:
        print(f"ℹ️ 데이터베이스 이미 존재: {dbname}")
    cur.close()
    conn.close()


# ---------------------------------------------------------------------------
# mcp1 – 이커머스 & 마케팅 성과 분석
# ---------------------------------------------------------------------------


def insert_mcp1():
    create_database_if_not_exists("mcp1")
    conn = psycopg2.connect(
        host=DB_HOST, dbname="mcp1", user=DB_USER, password=DB_PASSWORD
    )
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS Customers (
            customer_id SERIAL PRIMARY KEY,
            name TEXT,
            segment TEXT,
            signup_date DATE,
            acquisition_channel TEXT
        );
        CREATE TABLE IF NOT EXISTS Orders (
            order_id SERIAL PRIMARY KEY,
            customer_id INT REFERENCES Customers(customer_id),
            order_date DATE,
            amount NUMERIC,
            product_id INT
        );
        CREATE TABLE IF NOT EXISTS Campaigns (
            campaign_id SERIAL PRIMARY KEY,
            campaign_name TEXT,
            start_date DATE,
            end_date DATE,
            budget NUMERIC
        );
        CREATE TABLE IF NOT EXISTS Campaign_Performance (
            id SERIAL PRIMARY KEY,
            campaign_id INT REFERENCES Campaigns(campaign_id),
            date DATE,
            impressions INT,
            clicks INT,
            conversions INT
        );
    """
    )

    cur.execute("SELECT COUNT(*) FROM Customers")
    if cur.fetchone()[0] > 0:
        print("⏩ mcp1: 이미 데이터가 존재하므로 건너뜁니다.")
        cur.close()
        conn.close()
        return

    segments = ["일반", "VIP", "기업"]
    channels = ["SNS 광고", "검색엔진", "이메일"]

    for _ in range(NUM_CUSTOMERS):
        cur.execute(
            "INSERT INTO Customers (name, segment, signup_date, acquisition_channel) VALUES (%s, %s, %s, %s)",
            (
                faker.name(),
                random.choice(segments),
                faker.date_between(start_date="-2y", end_date="today"),
                random.choice(channels),
            ),
        )

    campaign_ids = []
    for i in range(NUM_CAMPAIGNS):
        name = f"Campaign_{i+1}"
        start = faker.date_between(start_date="-3M", end_date="-1M")
        end = start + timedelta(days=30)
        cur.execute(
            "INSERT INTO Campaigns (campaign_name, start_date, end_date, budget) VALUES (%s, %s, %s, %s) RETURNING campaign_id",
            (name, start, end, random.randint(1000, 5000)),
        )
        campaign_ids.append(cur.fetchone()[0])

    for cid in campaign_ids:
        start = datetime.now() - timedelta(days=30)
        for i in range(30):
            day = start + timedelta(days=i)
            impressions = random.randint(1000, 10000)
            clicks = random.randint(100, impressions)
            conversions = random.randint(0, clicks)
            cur.execute(
                "INSERT INTO Campaign_Performance (campaign_id, date, impressions, clicks, conversions) VALUES (%s, %s, %s, %s, %s)",
                (cid, day, impressions, clicks, conversions),
            )

    for _ in range(NUM_ORDERS):
        cur.execute(
            "INSERT INTO Orders (customer_id, order_date, amount, product_id) VALUES ((SELECT customer_id FROM Customers ORDER BY RANDOM() LIMIT 1), %s, %s, %s)",
            (
                faker.date_between(start_date="-1y", end_date="today"),
                random.randint(10000, 300000),
                random.randint(1, 100),
            ),
        )

    conn.commit()
    cur.close()
    conn.close()
    print("✅ mcp1 데이터 삽입 완료")


# ---------------------------------------------------------------------------
# mcp2 – 금융/결제 거래 분석 시나리오
# ---------------------------------------------------------------------------


def insert_mcp2():
    create_database_if_not_exists("mcp2")
    conn = psycopg2.connect(
        host=DB_HOST, dbname="mcp2", user=DB_USER, password=DB_PASSWORD
    )
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS Users (
            user_id SERIAL PRIMARY KEY,
            name TEXT,
            join_date DATE,
            segment TEXT
        );
        CREATE TABLE IF NOT EXISTS Transactions (
            transaction_id SERIAL PRIMARY KEY,
            user_id INT REFERENCES Users(user_id),
            date DATE,
            type TEXT,
            amount NUMERIC
        );
        CREATE TABLE IF NOT EXISTS PaymentMethods (
            payment_id SERIAL PRIMARY KEY,
            transaction_id INT REFERENCES Transactions(transaction_id),
            method TEXT,
            status TEXT
        );
    """
    )

    cur.execute("SELECT COUNT(*) FROM Users")
    if cur.fetchone()[0] > 0:
        print("⏩ mcp2: 이미 데이터가 존재하므로 건너뜁니다.")
        cur.close()
        conn.close()
        return

    segments = ["일반", "VIP", "기업"]
    methods = ["카드", "계좌이체", "포인트"]
    statuses = ["성공", "실패"]
    types = ["purchase", "refund", "reward"]

    for _ in range(NUM_USERS):
        cur.execute(
            "INSERT INTO Users (name, join_date, segment) VALUES (%s, %s, %s)",
            (faker.name(), faker.date_between("-2y", "today"), random.choice(segments)),
        )

    for _ in range(NUM_TRANSACTIONS):
        t_type = random.choice(types)
        amount = random.randint(1000, 100000) * (1 if t_type != "refund" else -1)
        cur.execute(
            "INSERT INTO Transactions (user_id, date, type, amount) VALUES ((SELECT user_id FROM Users ORDER BY RANDOM() LIMIT 1), %s, %s, %s) RETURNING transaction_id",
            (faker.date_between("-6M", "today"), t_type, amount),
        )
        tid = cur.fetchone()[0]
        cur.execute(
            "INSERT INTO PaymentMethods (transaction_id, method, status) VALUES (%s, %s, %s)",
            (tid, random.choice(methods), random.choice(statuses)),
        )

    conn.commit()
    cur.close()
    conn.close()
    print("✅ mcp2 데이터 삽입 완료")


# ---------------------------------------------------------------------------
# mcp3 – 금융 IT 서비스 로그 & 사용자 피드백 분석 시나리오
# ---------------------------------------------------------------------------


def insert_mcp3():
    create_database_if_not_exists("mcp3")
    conn = psycopg2.connect(
        host=DB_HOST, dbname="mcp3", user=DB_USER, password=DB_PASSWORD
    )
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS Users (
            user_id SERIAL PRIMARY KEY,
            name TEXT,
            signup_date DATE,
            acquisition_channel TEXT
        );
        CREATE TABLE IF NOT EXISTS UserActivity (
            activity_id SERIAL PRIMARY KEY,
            user_id INT REFERENCES Users(user_id),
            activity_date DATE,
            activity_type TEXT
        );
        CREATE TABLE IF NOT EXISTS Feedback (
            feedback_id SERIAL PRIMARY KEY,
            user_id INT REFERENCES Users(user_id),
            date DATE,
            rating INT,
            sentiment TEXT,
            category TEXT,
            comments TEXT
        );
    """
    )

    cur.execute("SELECT COUNT(*) FROM Users")
    if cur.fetchone()[0] > 0:
        print("⏩ mcp3: 이미 데이터가 존재하므로 건너뜁니다.")
        cur.close()
        conn.close()
        return

    channels = ["검색", "SNS", "광고", "지인추천"]
    activity_types = ["로그인", "검색", "상품조회", "결제"]
    categories = ["배송", "제품", "가격", "서비스"]
    sentiments = ["positive", "neutral", "negative"]

    for _ in range(NUM_USERS):
        cur.execute(
            "INSERT INTO Users (name, signup_date, acquisition_channel) VALUES (%s, %s, %s)",
            (faker.name(), faker.date_between("-1y", "today"), random.choice(channels)),
        )

    for _ in range(NUM_ACTIVITIES):
        cur.execute(
            "INSERT INTO UserActivity (user_id, activity_date, activity_type) VALUES ((SELECT user_id FROM Users ORDER BY RANDOM() LIMIT 1), %s, %s)",
            (faker.date_between("-6M", "today"), random.choice(activity_types)),
        )

    for _ in range(NUM_FEEDBACKS):
        cur.execute(
            "INSERT INTO Feedback (user_id, date, rating, sentiment, category, comments) VALUES ((SELECT user_id FROM Users ORDER BY RANDOM() LIMIT 1), %s, %s, %s, %s, %s)",
            (
                faker.date_between("-3M", "today"),
                random.randint(1, 5),
                random.choice(sentiments),
                random.choice(categories),
                faker.sentence(nb_words=8),
            ),
        )

    conn.commit()
    cur.close()
    conn.close()
    print("✅ mcp3 데이터 삽입 완료")


# ---------------------------------------------------------------------------
# mcp4 – 공공 행정 & 문화-관광 사업 분석 시나리오
# ---------------------------------------------------------------------------


def insert_mcp4():
    create_database_if_not_exists("mcp4")
    conn = psycopg2.connect(
        host=DB_HOST, dbname="mcp4", user=DB_USER, password=DB_PASSWORD
    )
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS Employees (
            emp_id SERIAL PRIMARY KEY,
            name TEXT,
            grade TEXT,
            dept TEXT,
            join_date DATE
        );
        CREATE TABLE IF NOT EXISTS Projects (
            proj_id SERIAL PRIMARY KEY,
            title TEXT,
            category TEXT,
            start_date DATE,
            end_date DATE,
            owner_emp INT REFERENCES Employees(emp_id)
        );
        CREATE TABLE IF NOT EXISTS BudgetRequests (
            req_id SERIAL PRIMARY KEY,
            proj_id INT REFERENCES Projects(proj_id),
            quarter TEXT,
            amount NUMERIC,
            status TEXT
        );
        CREATE TABLE IF NOT EXISTS Events (
            event_id SERIAL PRIMARY KEY,
            proj_id INT REFERENCES Projects(proj_id),
            event_name TEXT,
            event_date DATE,
            location TEXT,
            attendance INT
        );
        CREATE TABLE IF NOT EXISTS SuppliesRequests (
            supply_id SERIAL PRIMARY KEY,
            emp_id INT REFERENCES Employees(emp_id),
            request_date DATE,
            item TEXT,
            quantity INT,
            purpose TEXT,
            approval_status TEXT
        );
    """
    )

    cur.execute("SELECT COUNT(*) FROM Employees")
    if cur.fetchone()[0] > 0:
        print("⏩ mcp4: 이미 데이터가 존재하므로 건너뜁니다.")
        cur.close()
        conn.close()
        return

    grades = ["9급", "8급", "7급", "6급", "5급", "4급"]
    depts = ["문화정책과", "관광산업과", "스포츠진흥과", "국제협력담당관", "홍보담당관"]
    for _ in range(120):
        cur.execute(
            "INSERT INTO Employees (name, grade, dept, join_date) VALUES (%s, %s, %s, %s)",
            (
                faker.name(),
                random.choice(grades),
                random.choice(depts),
                faker.date_between("-10y", "today"),
            ),
        )

    categories = ["문화", "관광", "스포츠"]
    for i in range(30):
        s_date = faker.date_between("-18M", "-6M")
        e_date = s_date + timedelta(days=random.randint(90, 365))
        cur.execute(
            f"INSERT INTO Projects (title, category, start_date, end_date, owner_emp) VALUES (%s, %s, %s, %s, (SELECT emp_id FROM Employees ORDER BY RANDOM() LIMIT 1))",
            (f"프로젝트_{i+1:02d}", random.choice(categories), s_date, e_date),
        )

    cur.execute("SELECT proj_id FROM Projects")
    proj_ids = [row[0] for row in cur.fetchall()]
    statuses = ["제출", "검토중", "승인", "반려"]
    for pid in proj_ids:
        for q in ["2024Q4", "2025Q1", "2025Q2"]:
            cur.execute(
                "INSERT INTO BudgetRequests (proj_id, quarter, amount, status) VALUES (%s, %s, %s, %s)",
                (
                    pid,
                    q,
                    random.randint(5_000_000, 200_000_000),
                    random.choice(statuses),
                ),
            )

    venues = [
        "세종문화회관",
        "DDP",
        "광화문광장",
        "부산 벡스코",
        "인천 아시아드주경기장",
    ]
    for _ in range(80):
        cur.execute(
            "INSERT INTO Events (proj_id, event_name, event_date, location, attendance) VALUES ((SELECT proj_id FROM Projects ORDER BY RANDOM() LIMIT 1), %s, %s, %s, %s)",
            (
                faker.sentence(nb_words=3),
                faker.date_between("-6M", "today"),
                random.choice(venues),
                random.randint(100, 10000),
            ),
        )

    items = ["A4용지", "볼펜", "현수막", "배너", "기념품", "행사간식"]
    purposes = ["회의", "행사", "홍보물", "민원 대응"]
    approvals = ["대기", "승인", "반려"]
    for _ in range(300):
        cur.execute(
            "INSERT INTO SuppliesRequests (emp_id, request_date, item, quantity, purpose, approval_status) VALUES ((SELECT emp_id FROM Employees ORDER BY RANDOM() LIMIT 1), %s, %s, %s, %s, %s)",
            (
                faker.date_between("-3M", "today"),
                random.choice(items),
                random.randint(1, 200),
                random.choice(purposes),
                random.choice(approvals),
            ),
        )

    conn.commit()
    cur.close()
    conn.close()
    print("✅ mcp4 데이터 삽입 완료")


# ---------------------------------------------------------------------------
# mcp5 – 학사 행정 관리 시나리오
# ---------------------------------------------------------------------------


def insert_mcp5():
    create_database_if_not_exists("mcp5")
    conn = psycopg2.connect(
        host=DB_HOST, dbname="mcp5", user=DB_USER, password=DB_PASSWORD
    )
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS Students (
            student_id SERIAL PRIMARY KEY,
            student_number TEXT UNIQUE,
            name TEXT,
            grade INT,
            major TEXT,
            admission_date DATE,
            status TEXT,
            gpa NUMERIC(3,2)
        );
        CREATE TABLE IF NOT EXISTS Professors (
            prof_id SERIAL PRIMARY KEY,
            name TEXT,
            dept TEXT,
            position TEXT
        );
        CREATE TABLE IF NOT EXISTS Courses (
            course_id SERIAL PRIMARY KEY,
            course_code TEXT,
            course_name TEXT,
            credits INT,
            semester TEXT,
            prof_id INT REFERENCES Professors(prof_id),
            max_students INT
        );
        CREATE TABLE IF NOT EXISTS Enrollments (
            enrollment_id SERIAL PRIMARY KEY,
            student_id INT REFERENCES Students(student_id),
            course_id INT REFERENCES Courses(course_id),
            semester TEXT,
            enrollment_date DATE
        );
        CREATE TABLE IF NOT EXISTS Attendance (
            attendance_id SERIAL PRIMARY KEY,
            student_id INT REFERENCES Students(student_id),
            course_id INT REFERENCES Courses(course_id),
            attendance_date DATE,
            status TEXT,  -- 출석, 지각, 결석, 조퇴
            semester TEXT
        );
        CREATE TABLE IF NOT EXISTS Grades (
            grade_id SERIAL PRIMARY KEY,
            student_id INT REFERENCES Students(student_id),
            course_id INT REFERENCES Courses(course_id),
            semester TEXT,
            midterm_score NUMERIC(5,2),
            final_score NUMERIC(5,2),
            assignment_score NUMERIC(5,2),
            total_score NUMERIC(5,2),
            letter_grade TEXT,
            grade_point NUMERIC(2,1)
        );
        """
    )

    cur.execute("SELECT COUNT(*) FROM Students")
    if cur.fetchone()[0] > 0:
        print("⏩ mcp5: 이미 데이터가 존재하므로 건너뜁니다.")
        cur.close()
        conn.close()
        return

    # 1. 교수 데이터 삽입
    departments = [
        "컴퓨터공학과",
        "경영학과",
        "국어국문학과",
        "영어영문학과",
        "수학과",
        "물리학과",
        "화학과",
        "생물학과",
        "미술학과",
        "음악학과",
        "체육학과",
        "법학과",
    ]
    positions = ["교수", "부교수", "조교수", "겸임교수"]

    for _ in range(NUM_PROFESSORS):
        cur.execute(
            "INSERT INTO Professors (name, dept, position) VALUES (%s, %s, %s)",
            (faker.name(), random.choice(departments), random.choice(positions)),
        )

    # 2. 학생 데이터 삽입 (고학점자와 일반학생 구분하여 생성)
    statuses = ["재학", "휴학", "졸업", "제적"]
    majors = departments  # 전공은 학과와 동일

    # 🔧 학번 생성용 카운터 (중복 방지)
    student_counter = 1

    # 고학점자 생성 (전체의 20% = 600명, 이 중 15%가 장기결석 = 90명)
    high_gpa_students = int(NUM_STUDENTS * 0.2)
    for i in range(high_gpa_students):
        admission_year = random.randint(2020, 2024)
        # ✅ 수정: 순차적 학번 생성으로 중복 방지
        student_number = f"{admission_year}{student_counter:05d}"
        student_counter += 1
        gpa = round(random.uniform(3.8, 4.5), 2)  # 고학점자

        cur.execute(
            "INSERT INTO Students (student_number, name, grade, major, admission_date, status, gpa) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (
                student_number,
                faker.name(),
                random.randint(1, 4),
                random.choice(majors),
                faker.date_between(f"-{2025-admission_year}y", "today"),
                random.choice(statuses),
                gpa,
            ),
        )

    # 일반 학생 생성
    for i in range(NUM_STUDENTS - high_gpa_students):
        admission_year = random.randint(2020, 2024)
        # ✅ 수정: 순차적 학번 생성으로 중복 방지
        student_number = f"{admission_year}{student_counter:05d}"
        student_counter += 1
        gpa = round(random.uniform(1.0, 3.9), 2)  # 일반 학생

        cur.execute(
            "INSERT INTO Students (student_number, name, grade, major, admission_date, status, gpa) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (
                student_number,
                faker.name(),
                random.randint(1, 4),
                random.choice(majors),
                faker.date_between(f"-{2025-admission_year}y", "today"),
                random.choice(statuses),
                gpa,
            ),
        )

    # 3. 강좌 데이터 삽입
    course_prefixes = [
        "CS",
        "BU",
        "KL",
        "EN",
        "MA",
        "PH",
        "CH",
        "BI",
        "AR",
        "MU",
        "PE",
        "LA",
    ]
    semesters = ["2024-1", "2024-2", "2025-1"]

    for i in range(NUM_COURSES):
        course_code = f"{random.choice(course_prefixes)}{random.randint(100, 499)}"
        course_name = f"{faker.catch_phrase()} {random.choice(['이론', '실습', '세미나', '특강'])}"

        cur.execute(
            "INSERT INTO Courses (course_code, course_name, credits, semester, prof_id, max_students) VALUES (%s, %s, %s, %s, (SELECT prof_id FROM Professors ORDER BY RANDOM() LIMIT 1), %s)",
            (
                course_code,
                course_name,
                random.choice([1, 2, 3]),
                random.choice(semesters),
                random.randint(30, 120),
            ),
        )

    # 4. 수강신청 데이터 삽입
    for _ in range(NUM_ENROLLMENTS):
        cur.execute(
            "INSERT INTO Enrollments (student_id, course_id, semester, enrollment_date) VALUES ((SELECT student_id FROM Students ORDER BY RANDOM() LIMIT 1), (SELECT course_id FROM Courses ORDER BY RANDOM() LIMIT 1), %s, %s)",
            (random.choice(semesters), faker.date_between("-6M", "today")),
        )

    # 5. 출석 데이터 삽입 (장기결석자 270명 목표)
    attendance_statuses = ["출석", "지각", "결석", "조퇴"]

    # 학생별 출석률 설정
    cur.execute("SELECT student_id, gpa FROM Students WHERE status = '재학'")
    active_students = cur.fetchall()

    long_absent_count = 0
    target_long_absent = 270

    for student_id, gpa in active_students:
        # 고학점자 중 15%를 장기결석자로 설정
        if gpa >= 4.0 and long_absent_count < target_long_absent * 0.15:
            attendance_rate = 0.3  # 30% 출석률 (장기결석)
            long_absent_count += 1
        elif long_absent_count < target_long_absent:
            if random.random() < 0.1:  # 일반 학생 중 일부도 장기결석
                attendance_rate = 0.35  # 35% 출석률 (장기결석)
                long_absent_count += 1
            else:
                attendance_rate = random.uniform(0.7, 0.95)  # 정상 출석률
        else:
            attendance_rate = random.uniform(0.7, 0.95)  # 정상 출석률

        # 해당 학생의 수강과목에 대한 출석 생성
        cur.execute(
            "SELECT course_id FROM Enrollments WHERE student_id = %s", (student_id,)
        )
        courses = cur.fetchall()

        for (course_id,) in courses:
            # 학기당 15주 수업 가정
            for week in range(15):
                attendance_date = faker.date_between("-4M", "today")

                if random.random() < attendance_rate:
                    status = random.choices(
                        ["출석", "지각", "조퇴"], weights=[0.85, 0.1, 0.05]
                    )[0]
                else:
                    status = "결석"

                cur.execute(
                    "INSERT INTO Attendance (student_id, course_id, attendance_date, status, semester) VALUES (%s, %s, %s, %s, %s)",
                    (student_id, course_id, attendance_date, status, "2025-1"),
                )

    # 6. 성적 데이터 삽입
    letter_grades = ["A+", "A", "B+", "B", "C+", "C", "D+", "D", "F"]
    grade_points = [4.5, 4.0, 3.5, 3.0, 2.5, 2.0, 1.5, 1.0, 0.0]

    cur.execute("SELECT DISTINCT student_id, course_id FROM Enrollments")
    enrollments = cur.fetchall()

    for student_id, course_id in enrollments:
        # 학생의 GPA에 따라 성적 분포 조정
        cur.execute("SELECT gpa FROM Students WHERE student_id = %s", (student_id,))
        student_gpa = cur.fetchone()[0]

        if student_gpa >= 4.0:
            # 고학점자는 좋은 성적 위주
            letter_grade = random.choices(
                letter_grades, weights=[0.4, 0.3, 0.15, 0.1, 0.03, 0.02, 0, 0, 0]
            )[0]
        else:
            # 일반 학생은 정규분포
            letter_grade = random.choices(
                letter_grades, weights=[0.1, 0.15, 0.2, 0.25, 0.15, 0.1, 0.03, 0.02, 0]
            )[0]

        grade_point = grade_points[letter_grades.index(letter_grade)]

        midterm = (
            random.uniform(60, 100) if letter_grade != "F" else random.uniform(0, 59)
        )
        final = (
            random.uniform(60, 100) if letter_grade != "F" else random.uniform(0, 59)
        )
        assignment = (
            random.uniform(70, 100) if letter_grade != "F" else random.uniform(0, 69)
        )
        total = midterm * 0.3 + final * 0.4 + assignment * 0.3

        cur.execute(
            "INSERT INTO Grades (student_id, course_id, semester, midterm_score, final_score, assignment_score, total_score, letter_grade, grade_point) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (
                student_id,
                course_id,
                "2025-1",
                midterm,
                final,
                assignment,
                total,
                letter_grade,
                grade_point,
            ),
        )

    conn.commit()
    cur.close()
    conn.close()
    print("✅ mcp5 학사 행정 관리 데이터 삽입 완료")
    print(
        f"📊 생성된 데이터: 학생 {NUM_STUDENTS}명, 교수 {NUM_PROFESSORS}명, 강좌 {NUM_COURSES}개"
    )
    print(f"🎯 시나리오 목표: 장기결석자 약 270명, 고학점자 중 장기결석 15% 구현")


if __name__ == "__main__":
    insert_mcp1()
    insert_mcp2()
    insert_mcp3()
    insert_mcp4()
    insert_mcp5()
