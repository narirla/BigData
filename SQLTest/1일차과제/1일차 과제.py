import os
import sys
import pymysql

product = []


def title():
    print("-----------------------------")
    print(" 제품명\t수량\t생산일")
    print("-----------------------------")


def output_data():
    title()
    for pname, quantity, pdate in product:
        print(pname, quantity, pdate, sep='\t')

def input_data():
    while True:
        pname = input('제품명: ')
        quantity = int(input('수량: '))
        pdate = input('생산일: ')
        product.append((pname, quantity, pdate))
        answer = input('계속 입력하시겠습니까? (y/n) ').lower()
        if answer == 'n' or answer =='N':
            break
    if product:
        print("\nDB에 저장 중.....")
        save_database(product)
    else:
        print("저장 실패")

def main():
    product = []
    menu = {1:input_data, 2:output_data}
    while True:
        print("1.입력", "2.출력", sep='\n')
        answer = int( input('메뉴를선택:') )
        menu[answer]() #input_data()
    

    

def save_database(product):
    try:
        db  = pymysql.connect(host="127.0.0.1", user='root', password='1234' , database='test')
        cur = db.cursor()
        sql = "insert into product values(product, quantity , pdate)"
        cur.execute(sql)
        db.commit()
        db.close()
        print('DB 저장 완료')
    except Exception as err:
        print('에러',err)

main()