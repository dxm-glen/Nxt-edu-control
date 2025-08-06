import psycopg2
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# DB 접속 정보 (환경변수에서 로드)
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = os.getenv("DB_PORT", "5432")

# 데이터베이스 목록 (환경변수에서 로드)
database_list = os.getenv("DATABASE_LIST", "mcp1,mcp2,mcp3,mcp4")
databases = [db.strip() for db in database_list.split(",")]


def truncate_all_tables(dbname):
    print(f"🚮 초기화 중: {dbname}")
    conn = psycopg2.connect(
        host=DB_HOST, dbname=dbname, user=DB_USER, password=DB_PASSWORD
    )
    cur = conn.cursor()

    cur.execute(
        """
        DO $$
        DECLARE
            r RECORD;
        BEGIN
            FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
                EXECUTE 'TRUNCATE TABLE ' || quote_ident(r.tablename) || ' CASCADE';
            END LOOP;
        END
        $$;
    """
    )

    conn.commit()
    cur.close()
    conn.close()
    print(f"✅ {dbname} 데이터 초기화 완료")


if __name__ == "__main__":
    for db in databases:
        truncate_all_tables(db)
