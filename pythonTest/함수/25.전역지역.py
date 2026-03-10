# 파이썬 컴파일러가 만들어 주는 전역변수
# __name__ = '__main__'
# __packgage__ = None
# ...
# __file__ = 
g = 10

def fn():
    g = 100

fn()
print("g=", g)
print(__file__)
# print("전역변수", globals()) 
#{'__name__': '__main__', '__doc__': None, '__package__': None, '__loader__': <_frozen_importlib_external.SourceFileLoader object at 0x000001DD3B354AC0>, 
# '__spec__': None, '__annotations__': {}, '__builtins__': <module 'builtins' (built-in)>, '__file__': 'c:\\pythonTest\\25.전역지역.py', '__cached__': None, 
# 'g': 10, 'fn': <function fn at 0x000001DD3B293E20>}:fn 함수 주소값 # <- 선언한 지역변수 두가지
