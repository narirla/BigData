import numpy as np
import matplotlib.pyplot as plt
plt.rcParams['font.family'] = 'Malgun Gothic' 

# 국어, 영어, 수학 성적 데이터 (5명의 학생)
arr = np.array([
    [85, 92, 78],
    [90, 88, 95],
    [75, 80, 82],
    [95, 90, 88],
    [80, 75, 90]
])

xname = ['홍길동','이순신','임꺽정','김철수','이황']

kor = arr[:,0]
eng = arr[:,1]
math = arr[:,2]

plt.plot(xname, kor)
plt.show()