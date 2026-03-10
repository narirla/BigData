-- 1.ALLEN과 부서가 같은 사원들의 사원명, 입사일을 출력하되 높은 급여순으로 출력하세요.
SELECT ENAME, HIREDATE FROM EMP
 WHERE DEPTNO=(SELECT DEPTNO
				 FROM EMP
				WHERE ENAME='ALLEN')
 ORDER BY SAL DESC;
 
-- 2. 가장 높은 급여를 받는 사원보다 입사일이 늦은 사원의 이름&입사일
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


-- 3.FORD 보다 입사일이 늦은 사원 중 급여가 가장 높은 사원의 이름과 급여를 출력하세요.
select ename, sal from emp
where sal = (select max(sal) from emp 
where hiredate > (select hiredate from emp where ename = 'FORD')) and ename <> 'FORD';

-- 4.이름에 "T"자가 들어가는 사원들의 급여의 합을 구하세요.
SELECT SUM(SAL)  FROM EMP  WHERE ENAME LIKE '%T%';
SELECT SUM(SAL)  FROM EMP  WHERE ENAME RLIKE 'T';

-- 5.이름에 "S" 자가 들어가는 사원들 중 급여가 가장 높은 사원의 이름,급여를 출력하세요.
select ename, sal from emp
where ename like '%S%' and sal=(select max(sal) from emp where ename like '%S%');

-- 6.모든 사원의 평균급여를 구하세요.
select avg(sal) 평균급여 from emp;

-- 7. 20번 부서의 최고 급여보다 많은 사원의 사원번호,사원명,급여를 출력하세요.
SELECT EMPNO, ENAME, SAL
  FROM EMP
 WHERE SAL>(SELECT MAX(SAL)
			  FROM EMP
			 WHERE DEPTNO=20);
             
-- 8. SALES 부서에 근무하는 모든 사원의 이름과 급여
-- SELECT DEPTNO FROM DEPT WHERE DNAME = 'SALES';
-- SELECT ENAME, SAL FROM EMP WHERE DEPTNO = '30';

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

-- 9.직속상관이 KING인 사원의 이름과 급여를 출력하시오. 
select ename, sal from emp
where mgr=(select empno from emp where ename='KING');

-- 10.상반기(1월~ 6월) 입사한 사원의 이름 과 입사일을 구하시요.
select ename, hiredate from emp
where month(hiredate) between 1 and 6;

SELECT ENAME, HIREDATE
  FROM EMP
 WHERE SUBSTR(HIREDATE, 6, 2)<=06;
 
 -- 11. 홀수 년도에 입사한 사원의 이름 과 입사일을 구하시요.
SELECT ENAME, HIREDATE
  FROM EMP
 WHERE YEAR(HIREDATE)%2=1;
 
-- 12. 2000년대 이후 출생한 남아수, 여아수를 출력하시요

SELECT SUM(BOYS) '남아수'
	 , SUM(GIRLS) '여아수'
  FROM BIRTHS
 WHERE YEAR>2000;

SELECT boys, girs
  FROM BIRTHS
 WHERE YEAR>2000;
 
-- 13.  2000년대 이후 출생한 남아수, 여아수, 남아율(%) 을 출력하시요		

SELECT SUM(BOYS) '남아수'
	 , SUM(GIRLS) '여아수'
     , ROUND(SUM(BOYS)/(SUM(BOYS)+SUM(GIRLS))*100,2) '남아율'
  FROM BIRTHS
 WHERE YEAR>2000;
 
 
 -- 14. 남아수가 가장많은 년도, 남아수를 구하시요.

SELECT YEAR, BOYS
  FROM BIRTHS
 WHERE BOYS=(SELECT MAX(BOYS) FROM BIRTHS);

-- 15. 2000 년대이후 남아수가 50000 이상이면 '많음' '적음' 으로 정도 컬럼을 표시하시요

SELECT YEAR, BOYS
	 , CASE WHEN BOYS>=50000 THEN '많음'
			ELSE '적음'
            END AS '정도'
  FROM BIRTHS
 WHERE YEAR>=2000
;
