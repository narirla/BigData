SELECT * FROM EMP;

#1. ALLEN과 부서가 같은 사원들의 사원명, 입사일을 출력하되 높은순으로
SELECT ENAME, HIREDATE FROM EMP WHERE DEPTNO = '30';
SELECT DEPTNO FROM EMP WHERE ENAME = 'ALLEN';

SELECT 
    ENAME, HIREDATE
FROM
    EMP
WHERE
    DEPTNO = (SELECT 
            DEPTNO
        FROM
            EMP
        WHERE
            ENAME = 'ALLEN')
ORDER BY SAL DESC;

#2. 가장 높은 급여를 받는 사원보다 입사일이 늦은 사원의 이름&입사일
SELECT MAX(SAL) FROM EMP;
SELECT HIREDATE FROM EMP WHERE 최댓값;
SELECT ENAME, HIREDATE FROM EMP WHERE (?);

SELECT
    ENAME, HIREDATE
FROM
    EMP
WHERE
    HIREDATE > (SELECT 
            HIREDATE
        FROM
            EMP
        WHERE
            SAL = (SELECT 
                    MAX(SAL)
                FROM
                    EMP))
ORDER BY HIREDATE DESC;

#3. FORD보다 입사일이 늦은 사원중 여가 가장 높은 사원&급여
SELECT ENAME, SAL FROM EMP WHERE HIREDATE > 포듴거;
SELECT HIREDATE FROM EMP WHERE ENAME = 'FORD';

SELECT 
    ENAME, SAL
FROM
    EMP
WHERE
    HIREDATE > (SELECT 
            HIREDATE
        FROM
            EMP
        WHERE
            ENAME = 'FORD')
ORDER BY SAL DESC
LIMIT 1;
            
#4. 이름에 'T'가 들어가는 사원들의 급여의 합
SELECT
    SUM(SAL)
FROM
    EMP
WHERE
    ENAME LIKE '%T%';
    
    
#5. 이름에 'S'자가 들어가는 사원 중 급여가 가장 높은 사람
SELECT 
    ENAME, SAL
FROM
    EMP
WHERE
    ENAME LIKE '%S%'
ORDER BY SAL DESC
LIMIT 1;

#6. 모든 사원의 평균 급여?
SELECT ROUND(AVG(SAL), 3) FROM EMP;

#7. 20번 부서의 최고급여보다 많의 사원의 출력
SELECT EMPNO, ENAME, SAL FROM EMP WHERE SAL > 3000;
SELECT MAX(SAL) FROM EMP WHERE DEPTNO = '20';

SELECT 
    EMPNO, ENAME, SAL
FROM
    EMP
WHERE
    SAL > (SELECT 
            MAX(SAL)
        FROM
            EMP
        WHERE
            DEPTNO = '20');
            
#8. SALES 부서에 근무하는 모든 사원의 이름과 급여
SELECT ENAME, SAL FROM EMP WHERE DEPTNO = '30';
SELECT DEPTNO FROM DEPT WHERE DNAME = 'SALES';

SELECT 
    ENAME, SAL
FROM
    EMP
WHERE
    DEPTNO = (SELECT 
            DEPTNO
        FROM
            DEPT
        WHERE
            DNAME = 'SALES');
            
#9. 직속상관의 이름이 king인 사람의 이름 & 급여
SELECT 
    ENAME, SAL
FROM
    EMP
WHERE
    MGR = (SELECT 
            EMPNO
        FROM
            EMP
        WHERE ENAME = 'KING');


#10. 사안기(1~6월)에 입사한 사람의 이름 & 입사일
SELECT 
    ENAME, HIREDATE
FROM
    EMP
WHERE
    MONTH(HIREDATE) BETWEEN 1 AND 6;

#11. 홀수년도에 입사한 사람의 이름과 입사일
SELECT 
    ENAME, HIREDATE
FROM
    EMP
WHERE
    YEAR(HIREDATE) % 2 = 1;
    
    
#12. 2000년대 이후 출생한 남아수 여아수
SELECT 
    SUM(BOYS), SUM(GIRLS)
FROM
    BIRTHS
WHERE
    YEAR >= 2000;

   
SELECT 
    YEAR, BOYS, GIRLS
FROM
    BIRTHS
WHERE
    YEAR >= 2000;

#13. 2000년대 이후 출생한 남아수, 여아수, 남아율 
SELECT 
    SUM(BOYS), SUM(GIRLS), SUM(BOYS) / (SUM(BOYS) + SUM(GIRLS)) * 100 AS 남아율
FROM
    BIRTHS
WHERE
    YEAR >= 2000;

#14. 남아수가 가장 많은 연도와 그 남아수 구하기
SELECT 
    YEAR, BOYS
FROM
    BIRTHS
ORDER BY BOYS DESC
LIMIT 1;


#15. 2000년대 이후 남아수가 50000이상이면 '많음, '적음'으로 정도 칼을 표
SELECT 
    YEAR, BOYS,
    CASE
        WHEN BOYS >= 50000 THEN '많음'
        ELSE '적음'
    END AS 정도
FROM
    BIRTHS
WHERE YEAR >= 2000;


