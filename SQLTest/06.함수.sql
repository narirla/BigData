-- 형변환 함수

select cast( '1' as signed ); /*문자열을 순자로 변환*/
select cast( '220' as char(3) ); /*문자열을 순자로 변환*/
select cast( '2020-11-12' as date ); /*문자열을 날짜로 변환*/

select ename, sal
from emp;

select ename, sal
from emp
where cast(sal as char(4)) like '2%'; /*월급이 2000대인것을 가져옴*/

-- over 함수 :전체로 창을 확대
select ename, avg(sal) 
from emp;

select ename, avg(sal) over() from emp;

select distinct deptno
from emp;

select ename, avg(sal) over(partition by deptno) 
from emp;
-- 같은 sal 값이 있는 행들은 같은 윈도우 범위(dbms 별 적용 상이)
select sal,sum(sal) over(order by sal) 누적급여 /*over(order by )는 누적*/
from emp;

select sal, sum(sal) over(order by sal ROWS between unbounded preceding and current row)
from emp;

select sum(sal) over(order by sal ROWS between 1 preceding and current row) /*바로 전 행과 현재 행만 더해라*/
from emp;

-- 순위
select ename, sal, rank() over( order by sal desc ) 
from emp;

select ename, sal, dense_rank() over( order by sal desc ) 
from emp;

select ename, sal, row_number() over( order by sal desc ) 
from emp;

select ename, deptno, sal, rank() over( partition by deptno order by sal desc)
from emp;

-- 퀴즈 : 급여 top5를 구하시오. (같은 급여 처리)
-- select ename 사원명, sal 급여, dense_rank() over( order by sal desc ) as sal_rank
-- from emp
-- where sal_rank<=5; 사용불가

select * 
from (select ename, sal, dense_rank() over(order by sal desc) as sal_rank
		from emp) as my
where sal_rank<=5;
