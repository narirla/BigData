select * from testA;
select * from testB;

-- cross join(mysql, oracle)
select * 
from testa a , testb b
order by a.name;

-- cross join (의미 있는 X) : 표준
SELECT *
FROM testA CROSS JOIN testB
ORDER BY testA.name;

-- equi join(공통 컬럼 기준 = ): 가장 많이 적용
-- 표준 아님
select * 
from testa a, testb b where a.name = b.name;

-- 표준
SELECT 
    *
FROM
    testa
        INNER JOIN
    testb ON testa.name = testb.name;

SELECT *
FROM testa INNER JOIN testb USING (name);

select * 
from testa natural join testb; /*inner join과 동일*/

select * 
from testa join testb using(name); /*inner 생략가능: inner join이 default 값*/
 
select *
from testa left join testb using(name); /*testa가 다 나옴*/

select *
from testa right join testb using(name); /*testb가 다 나옴*/


-- join 이용 
-- 뉴욕에서 근무하는 사원의 이름과 급여를 출력하시오.
SELECT *
FROM testa INNER JOIN testb USING (name) /*inner join 사용 多*/
where myid<=2;

select ename, sal
from emp inner join dept using(deptno)
where loc = 'NEW YORK';

select *
from emp inner join dept using(deptno);

select *
from emp right join dept using(deptno);

select *
from emp left join dept using(deptno);
-- 퀴즈: ACCOUNTING 부서 소속 사원의 이름과 입사일을 출력하시오.
select ename, hiredate 
from emp join dept using(deptno)
where dname = 'ACCOUNTING';

-- subquery로 
SELECT ename, hiredate
FROM emp
WHERE deptno = (SELECT deptno
				FROM dept
				WHERE dname = 'ACCOUNTING');
                
-- non equi join : 공통 칼럼이 없는데 join 하는 것
SELECT *
FROM salgrade;

SELECT  *
FROM emp e 
JOIN salgrade s ON e.sal >= s.LOW_SALARY
				AND e.sal <= s.HIGH_SALARY;

SELECT  ename, sal, grade
FROM emp e 
JOIN salgrade s ON e.sal >= s.LOW_SALARY
				AND e.sal <= s.HIGH_SALARY;
                
SELECT  ename, sal, grade
FROM emp e JOIN salgrade s ON e.sal between s.LOW_SALARY AND s.HIGH_SALARY;

-- self join : 동일한 테이블에서 join 하는 것
select e1.ename 직원, e2.ename 상관
from emp e1 join emp e2 on e1.mgr = e2.empno;

-- quiz : 매니저가 KING인 사원들의 이름과 직급을 출력하시오.
select e1.ename 직원, e2.ename 상관
from emp e1 join emp e2 
			on e1.mgr = e2.empno and e2.ename = 'KING';