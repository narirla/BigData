-- is null 연산자
select ename, comm from emp;
-- select ename, comm from emp where comm = null; X
select ename, comm from emp where comm is null;
select ename, comm from emp where comm is not null;
-- 상관이 없는 사원( CEO )을 검색하기 위한 SQL 문을 작성해 보시오.
select ename, mgr from emp where mgr is null;

-- 정렬
select ename, sal from emp order by sal;
select ename, sal from emp order by sal asc;
select ename, sal from emp order by sal desc;

select ename, sal from emp order by ename;
-- 최근 입사한 직원 순으로 정렬하시요 ( 이름, 급여, 입사일)
select ename,hiredate, sal from emp order by hiredate desc;

select ename,hiredate, sal, deptno from emp
order by deptno desc, ename desc;

-- 부서 번호가 빠른 사원부터 출력하되 같은 부서내의 사원을 출력할 경우 
-- 최근에 입사한 사원부터 출력
select ename,hiredate, sal, deptno from emp
order by deptno , hiredate desc;
-- 급여가 3000 이상인 사원의 이름과 급여를 구하고 이름순으로 정렬하시요
select ename, sal from emp where sal>=3000 order by ename;

-- 집계함수
-- https://dev.mysql.com/doc/refman/8.4/en/aggregate-functions.html

select max(sal) from emp;
select min(sal) from emp;
select avg(sal) from emp;
select sum(sal) from emp;
select count( sal ) from emp;
-- null 은 count 에서 제외
select count( comm ) from emp;
-- emp 테이블 전체 행의 갯수
select count(*) from emp;
select std(sal) from emp;
select variance(sal) from emp;
select avg(sal) 평균, sum(sal) 총합 from emp;

-- sub query(서브쿼리)
-- 제임스의 부서명을 구하시요.
select deptno from emp where ename='JAMES';
select dname from dept where deptno=30;
-- 단일행 서브쿼리
select dname from dept 
where deptno=(select deptno from emp where ename='JAMES');
-- james와 같은 부서에서 근무하는 사원의 이름을 구하시요
select ename, deptno from emp
where deptno =(select deptno from emp where ename='JAMES');
-- james와 같은 직업의 사원의 이름, 직업을 구하시요
select job from emp where ename='JAMES';
select ename, job from emp where job='CLERK';
select ename, job from emp where job=(select job from emp where ename='JAMES');

-- JAMES 보다 높은 급여를 받는 사원의 이름과 급여를 구하시요.
select ename, sal from emp 
where sal>(select sal from emp where ename='JAMES');

-- james와 같은 부서에서 근무하는 사원의 이름을 구하시요(단 james는 제외)
-- 급여가 가장높은 사원의 이름과 급여를 구하시요.
-- 급여 평균보다 높은 사원의 이름과 급여를 구하시요.

select ename, deptno from emp
where deptno =(select deptno from emp where ename='JAMES') 
and ename<>'JAMES';

select max(sal) from emp;
select ename, sal from emp where sal = 5000;
select ename, sal from emp where sal =(select max(sal) from emp);

select avg(sal) from emp;
select ename, sal from emp where sal>2073.2142;

select ename, sal from emp where sal>(select avg(sal) from emp);

-- 퀴즈: WARD가 소속된 부서 사원들의 평균 급여보다  
-- 급여가 높은 사원의 이름 ,급여를 출력하세요.

select deptno from emp where ename='WARD';
select avg(sal) from emp where deptno=30;
select ename, sal from emp where sal>1566;

select ename, sal from emp 
where sal> (select avg(sal) from emp 
where deptno=(select deptno from emp where ename='WARD'));

-- 이름이 S로 시작하고 마지막글자가 H인 사원의 이름을 출력하세요.
select ename from emp where ename like 'S%H';
select ename from emp where ename rlike '^S[A-Z]+H$';
select * from 
(select ename from emp where ename like 'S%') as my
where ename like '%H';

-- 최저 급여를 받는 사원과 같이 근무하는 모든 사원의 수를 구하시요.
select min(sal) from emp;
select deptno from emp where sal=800;
select count(*) from emp where deptno=20;

select count(*) from emp 
where deptno=(select deptno from emp 
where sal=(select min(sal) from emp) );

-- DALLAS에 위치한 부서에 근무하는 사원들의 평균급여, 전체급여를 출력하세요.
select * from dept;

select deptno from dept where loc='DALLAS';
select avg(sal), sum(sal) from emp where deptno=20;

select avg(sal), sum(sal) from emp 
where deptno=(select deptno from dept where loc='DALLAS');

-- emp Table에서 이름, 급여, 커미션, 총액(sal + comm)을 구하여 
-- 총액이 많은 순서로 출력하라. 단, 커미션이 NULL인 사람은 제외한다.

select ename,sal, comm, sal+comm 총액 from emp
where comm is not null
order by 총액 desc;
