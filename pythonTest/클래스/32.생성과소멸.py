class Test:
    def __init__(self): # 객체생성이 완료되면 멤버데이터 초기값을 위해 자동호출
        print('init call')
        self.a = 0  
        self.b = 0

    def  __del__(self): # 객체소멸전에 자동호출되는 함수
        print('del call')

    def setData(self, x,y): 
        self.a = x
        self.b = y

    def show(self): 
        print(self.a, self.b)



# def fn():
#     obj = Test()
#     obj.show()

# fn()
# print('hello')

def fn():
    obj = Test()
    obj.show()
    return obj

rst = fn()
print('hello')
rst.show() # rst.show(rst) 객체는 소멸되지않음 -> rst를 reference 하기 때문

# obj = Test()
# obj1 = obj
# obj = 'abc'
# print('hello')

# 파이썬의 참조계수기법 ( reference count 0 가 되면 객체 소멸)