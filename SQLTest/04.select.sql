-- 조건별 case when then(표준)
-- 급여가 1000 이하면 'LOW', 2000이하면 'MIDLLE' 'HIGH'

select ename, sal,
case
	when sal<=1000 then 'LOW'
    when sal<=2000 then 'MIDDLE'
    else 'HIGH'
end as 정도
from emp;
-- 급여가 1000 이하면 'LOW', 2000이하면 'MIDLLE' 'HIGH' 인 경우
-- HIGH 사원명과 급여를 출력하시요
select * from (
select ename, sal,
case
	when sal<=1000 then 'LOW'
    when sal<=2000 then 'MIDDLE'
    else 'HIGH'
end as 정도
from emp) as MY
where 정도='HIGH';

-- ~별( group by )
select deptno, avg(sal) from emp group by deptno;
select deptno, avg(sal), sum(sal) from emp group by deptno;

-- 표준
select deptno, avg(sal) 
from emp 
group by deptno
having avg(sal)>=2000;

-- mysql, oracle 가능 (표준아님)
select deptno, avg(sal) 평균
from emp 
group by deptno
having 평균>=2000;

-- job 별 급여의 평균을 구하시요.
SELECT 
    job, AVG(sal)
FROM
    emp
GROUP BY job;

--  부서및 job
select deptno, job, avg(sal) 
from emp group by deptno,job 
order by deptno;

--  총계:표준아님
select job, avg(sal) , sum(sal)
from emp 
group by job with rollup;

-- select job, avg(sal) , sum(sal)
-- from emp 
-- group by rollup(job);

-- 표준아님: rlike, having alias사용, with rollup

-- 표준아님 오라클제외 대부분 지원
select * from emp limit 2;
select * from emp order by ename desc limit 2;


