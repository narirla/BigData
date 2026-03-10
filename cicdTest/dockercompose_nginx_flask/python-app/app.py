from flask import Flask
import pymysql
import os

app = Flask(__name__)

# DB 연결 설정 함수
def get_db_connection():
    return pymysql.connect(
        host=os.environ.get('DB_HOST'),
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASS'),
        database=os.environ.get('DB_NAME'),
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor  # 데이터를 딕셔너리 형태로 반환
    )

@app.route('/')
def index():
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # [주의] 'users' 부분을 실제 init.sql에서 만든 테이블 이름으로 수정하세요.
            sql = "SELECT * FROM users"
            cursor.execute(sql)
            rows = cursor.fetchall()

        # 결과를 간단한 HTML 테이블로 출력
        html = "<h1>MySQL Data (via PyMySQL)</h1><table border='1'>"
        if rows:
            # 테이블 헤더 생성
            html += "<tr>" + "".join([f"<th>{key}</th>" for key in rows[0].keys()]) + "</tr>"
            # 테이블 내용 생성
            for row in rows:
                html += "<tr>" + "".join([f"<td>{val}</td>" for val in row.values()]) + "</tr>"
        else:
            html += "<tr><td>데이터가 없습니다.</td></tr>"
        html += "</table>"
        
        return html

    except Exception as e:
        return f"<h3>연결 에러 발생:</h3><p>{str(e)}</p>"
    
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)