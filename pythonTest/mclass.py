class Student:
    def __init__(self, name, age, addr):
        self.name = name
        self.age = age
        self.addr = addr
    
    def show(self):
        print('이름', self.name)
        print('나이', self.age)
        print('주소', self.addr)

class Circle:
    @staticmethod
    def circle_area( r):
        return 3.14*r**2
    
    @staticmethod
    def cylinder( r,h):
        return 3.14*r**2*h
    
def hap(a,b):
    return a+b

myg = 100