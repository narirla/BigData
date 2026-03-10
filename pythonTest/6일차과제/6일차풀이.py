
mylist = []


def input_data():
    while True:
        name = input('이름: ')
        kor = int(input('국어: '))
        eng = int(input('영어: '))
        math = int(input('수학: '))
        mylist.append( (name,kor, eng, math ) )
        answer = input('계속 입력하시겠습니까? (y/n) ')
        if answer=='n' or answer=='N':
            break

def title():
    print("-----------------------------")
    print(" 이름\t국어\t영어\t수학 ")
    print("-----------------------------")

def output_data():
    title()
    for n,k,e,m in mylist:
        print(n,k,e,m, sep='\t')

def main():
    menu = {1:input_data, 2:output_data, 3:exit}
    while True:
        print("1.입력", "2.출력","3.종료", sep='\n')
        answer = int( input('메뉴를선택:') )
        menu[answer]() #input_data()
        # if answer==1:
        #     input_data()
        # elif answer==2:
        #     output_data()
        # elif answer==3:
        #     break
main()