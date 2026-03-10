import os
import sys
import mysql.connector as MY
# from datetime import datetime


def print_separator():
    print("-" * 50)


def print_table_header():
    print(f"{'제품명':^10} {'수량':^10} {'생산일':^15}")
    print("-" * 50)


def print_table_row(product, quantity, production_date):
    print(f"{product:^15} {quantity:^10} {production_date:^15}")


def main():
    products = []
    
    while True:
        print()
        product_name = input("제품명: ")
        quantity = input("수량: ")
        production_date = input("생산일: ")
        
        products.append({
            'product': product_name,
            'quantity': quantity,
            'production_date': production_date
        })
        
        print()
        print_separator()
        print_table_header()
        for p in products:
            print_table_row(p['product'], p['quantity'], p['production_date'])
        print("...")
        print_separator()
        
        while True:
            continue_input = input("\n계속 입력하시겠습니까(y/n)? ").lower()
            if continue_input in ['y', 'n']:
                break
            print("y 또는 n을 입력해주세요.")
        
        if continue_input == 'n':
            break
    
    if products:
        print("\n데이터베이스에 저장 중...")
        save_database(products)
    else:
        print("\n저장할 데이터가 없습니다.")


def save_database(products):
    try:
        db = MY.connect(host='127.0.0.1', user = 'root', password = 'a06290629@', database = 'test')
        cur = db.cursor()
        
        sql = "INSERT INTO product (product, quantity, production_date) VALUES (%s, %s, %s)"
        for p in products:
            cur.execute(sql, (p['product'], p['quantity'], p['production_date']))

        db.commit()
        cur.close()
        db.close()
        print("데이터베이스에 저장되었습니다")

    except Exception as e:
        print(f"오류발생: {e}")

if __name__ == "__main__":
    main()