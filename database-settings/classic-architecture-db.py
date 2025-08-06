# 생성된 사용자 정보 예시
# 데이터베이스 이름 : user_01
# 유저 이름 : db_01
# 유저 암호 : pw_01


import pymysql
import boto3

# RDS 연결 정보
rds_host = "DB-HOST"
db_username = "DB-NAME"
db_password = "DB-PW"
db_name = "texts"

# RDS에 연결
try:
    conn = pymysql.connections.Connection(
        host=rds_host, user=db_username, password=db_password, database=db_name
    )
except Exception as e:
    print(f"Error connecting to RDS: {e}")
    exit()


# 데이터베이스와 사용자 생성, 테이블 생성 및 초기 데이터 삽입
def create_database_and_user(user_index):
    user_name = f"user_{user_index:02d}"
    db_name = f"db_{user_index:02d}"
    user_password = f"pw_{user_index:02d}"

    with conn.cursor() as cursor:
        # 데이터베이스 생성
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name};")

        # 사용자 생성 및 권한 부여
        cursor.execute(
            f"CREATE USER IF NOT EXISTS '{user_name}'@'%' IDENTIFIED BY '{user_password}';"
        )
        cursor.execute(f"GRANT ALL PRIVILEGES ON {db_name}.* TO '{user_name}'@'%';")

        # 생성된 데이터베이스 사용
        cursor.execute(f"USE {db_name};")

        # 테이블 생성 및 초기 데이터 삽입
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS texts (id INT AUTO_INCREMENT PRIMARY KEY, text TEXT NOT NULL, username VARCHAR(255) NOT NULL);"
        )
        cursor.execute(
            "INSERT INTO texts (text, username) VALUES ('언제나 현재에 집중할수 있다면 행복할것이다...아마도...', '파울로 코엘료');"
        )
        cursor.execute(
            "INSERT INTO texts (text, username) VALUES ('어리석은 자는 멀리서 행복을 찾고, 현명한 자는 자신의 발치에서 행복을 키워간다...아마도...', '제임스 오펜하임');"
        )
        cursor.execute(
            "INSERT INTO texts (text, username) VALUES ('성공의 비결은 단 한 가지, 잘할 수 있는 일에 광적으로 집중하는 것이다...아마도...', '톰 모나건');"
        )

        conn.commit()


# 사용자 및 데이터베이스를 원하는 횟수만큼 생성
number_of_users = 55  # 생성할 사용자 및 데이터베이스 수
for i in range(0, number_of_users + 1):
    create_database_and_user(i)

# RDS 연결 종료
conn.close()


# pip install boto3 pymysql
# python3 students_database_creator.py
