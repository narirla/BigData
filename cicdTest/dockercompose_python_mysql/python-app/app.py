import pymysql  # mysql.connector 대신 pymysql 사용
import time
import os

# MySQL 연결을 위한 재시도 로직
def connect_to_mysql():
    while True:
        try:
            # pymysql.connect를 사용.
            db_connection = pymysql.connect(
                host="db",           # docker-compose 서비스 이름
                user="testuser",
                password="testpassword",
                database="testdb",
                charset='utf8mb4',   # 한글 깨짐 방지를 위한 설정 추가
                cursorclass=pymysql.cursors.DictCursor # (선택) 결과를 딕셔너리 형태로 받기 위함
            )
            print("Successfully connected to MySQL!")
            return db_connection
        except pymysql.MySQLError as err:
            print(f"Error: {err}")
            time.sleep(5)  # 연결 실패 시 5초 기다린 후 재시도

# MySQL 연결
db_connection = connect_to_mysql()

try:
    with db_connection.cursor() as cursor:
        # product 테이블 조회
        sql = "SELECT * FROM product"
        cursor.execute(sql)

        # 결과 출력
        rows = cursor.fetchall()
        for row in rows:
            # DictCursor를 사용했으므로 row['column_name'] 형태로도 접근 가능.
            print("result:", row)

finally:
    # 연결 종료
    db_connection.close()

# import mysql.connector
# import time
# import os

# # MySQL 연결을 위한 재시도 로직
# def connect_to_mysql():
#     while True:
#         try:
#             db_connection = mysql.connector.connect(
#                 host="db",  # MySQL 컨테이너의 서비스 이름 (docker-compose에서 정의한 db 서비스)
#                 user="testuser",
#                 password="testpassword",
#                 database="testdb"
#             )
#             return db_connection
#         except mysql.connector.Error as err:
#             print(f"Error: {err}")
#             time.sleep(5)  # 연결 실패 시 5초 기다린 후 재시도

# # MySQL 연결
# db_connection = connect_to_mysql()
# cursor = db_connection.cursor()

# # product 테이블 조회
# cursor.execute("SELECT * FROM product")

# # 결과 출력
# for row in cursor.fetchall():
#     print("result", row)

# # 연결 종료
# cursor.close()
# db_connection.close()
