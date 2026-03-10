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

def selectProduct():
    try:
        db = pymysql.connect(host="127.0.0.1", user='root' ,
                        password='1234',database='test')
        cur = db.cursor()
        sql = "select * from product"
        cur.execute( sql )
        fdata = cur.fetchall()
        db.close()
        return fdata
    except Exception as err:
        print('에러', err)
        return []


while True:
    pname = input('제품명:')
    pcount = input('수량:')
    pdate = input('생산일:')
    insertData(pname, pcount, pdate)
    yn = input( '계속입력(y/n):')
    if yn=='n':
        break

rst = selectProduct() #( ('컴퓨터',20,'2020-11-11'),('마우스',20,'2020-11-11') )

print('='*20)
print('제품명','수량','생산일', sep='\t')
print('='*20)
for n,c,d in rst:
    ds = d.strftime("%Y년%m월%d일")
    print( n,c,ds, sep='\t' )
