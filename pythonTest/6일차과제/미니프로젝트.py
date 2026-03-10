score_list = []

def main():
    print("<메인 메뉴>")
    print("1.입력 2.출력 3.검색 4.수정 5.저장 6.통계 7.종료")
    num = int(input("원하는 메뉴의 번호를 입력하세요. "))

    if num == 1:
        main_num()
    elif num == 2:
        sco_output()

def sco_input():
    print("이름과 국어, 영어, 수학 성적을 입력해주세요.")
    name = input('이름: ')
    kor = int(input('국어: '))
    eng = int(input('영어: '))
    mat = int(input('수학: '))

    return name, kor, eng, mat

def main_num():
    myScore = sco_input()
    score_list.append(myScore)

    answer = input('계속 입력하시겠습니까? (y/n) ')

    if answer == 'y':
        return main_num()
    elif answer == 'n':
        return main()
    # else:
    #     print("y와 n으로 입력해주세요.")
    #     return main()

def sco_output():
    print("-----------------------------")
    print(" 이름\t국어\t영어\t수학 ")
    print("-----------------------------")
    for name, kor, eng, mat in score_list:
        print(f"{name}\t{kor}\t{eng}\t{mat}")
    print("-----------------------------")

    return main()

main()
