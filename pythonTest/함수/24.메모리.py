g = 10 # data segment 의 global(static) 영역에 데이터 할당
def fn1():
    a = 10
    b = 20

def fn2():
    c = 30
    d = 40
    fn1()

def main():
    e = 50
    f = 60
    fn2()

main()