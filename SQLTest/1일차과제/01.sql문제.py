import pymysql

def insertData( pname, pcount,pdate):
    try:
        db = pymysql.connect(host="127.0.0.1", user='root' ,
                        password='1234',database='test')
        cur = db.cursor()
        sql = f"insert into product values('{pname}',{pcount},'{pdate}')"
        print( sql )
        cur.execute( sql )
        db.commit()
        db.close()
        print('추가성공')
    except Exception as err:
        print('에러', err)

pname = input('제품명:')
pcount = input('수량:')
pdate = input('생산일:')
insertData(pname, pcount, pdate)
