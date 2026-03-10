select * from emp;
-- 1. 부서별로 부서명, 평균 급여를 출력하세요.
select dname 부서명, avg(sal) '평균급여'
from emp join dept using(deptno)
group by dname;

select ename, deptno
from emp
where deptno not in (
				select deptno
                from dept
                where loc='NEW YORK');
--  deptno not in (10,20);

-- 2. JAMES가 소속된 부서의 사원 중
-- 급여가 1000에서 2000 사이인 사원의 이름과 부서명을 출력하시오.
select *
from emp join dept using(deptno);

select dname 부서명, ename 사원이름
from emp join dept using(deptno)
where sal between 1000 and 2000
and deptno = ( select deptno
				from emp
				where ename='JAMES');
