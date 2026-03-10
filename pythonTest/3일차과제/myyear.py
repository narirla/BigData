def leap_year(year):
    return "윤년" if year % 4 == 0 and year % 100 != 0 or year % 400 == 0 else "아님"


def zodiac(year) :
    return ['원숭이', '닭', '개', '돼지', '쥐', '소', '호랑이',
               '토끼', '용', '뱀', '말', '양'][ year % 12 ]


def exchange(price,pay) :
    exchange = pay - price
    n500 = exchange // 500
    exchange = exchange % 500
    n100 = exchange // 100
    exchange = exchange % 100
    n50 = exchange // 50
    exchange = exchange % 50
    n10 = exchange // 10
    return n500, n100, n50, n10