select * from emp;
select * from dept;
select * from salgrade;
-- database 선택
use test;
-- 선택된 데이터베이스 테이블 목록 보여주기
show tables;
-- 테이블 정보 칼럼 보여주기
desc emp;

-- sql 대소문자 구분 x
-- select * from student; SELECT * FROM student; 
-- select
-- [distinct] [column [alias]]
-- from
-- table_name 

select empno, ename from emp;
-- emp 테이블로 부터 사원명, 급여, 고용일 컬럼을 가져오시오.
select ename, sal, hiredate from emp;

select ename 사원명 from emp;

select ename as 사원명 from emp;
select ename, job from emp;
select job from emp;
-- 현재 사원의 직업 종류는?
select distinct job from emp; /*disrinct: 중복된 코드 제외하고 보여줌*/
-- 산술연산자: +, - , *, /, %(표준 X), 연삱자 우선순위 괄호
select 3+2;
select 3+2, 3*2;
select 3+2, 3*2 from dual;
select (3+2)*2;
select sal, sal*12 연봉 from emp;

-- 퀴즈: emp 테이블 급여에서 세금 3.3%를 제한 실수령액을 구하시오.
-- 사원이름, 급여, 실수령액 결과를 보여주시오.
select ename 사원이름, sal 급여, sal*(1-0.033) 실수령액 from emp; 
select ename 사원이름, sal 급여, round(sal*(1-0.033),2) 실수령액 from emp; 

select sal, sal*12, sal/30, sal%3 from emp;

select ename, sal, comm from emp;
select ename, sal, comm, sal+comm 총급여 from emp;
select ename, sal, comm, sal+comm 총급여 from emp;
-- null 을 처리해야 연산 가능히다: nvl(일반적인 dbms), ifnull -> mysql
select ename, sal, comm, ifnull(comm,0) 총급여 from emp;

-- 퀴즈
-- emp에서 ename, sal, comm, 실급여를 구하시오.
select ename, sal, comm, sal+ifnull(comm, 0) 실급여 from emp;
select ename, sal, comm, sal+ifnull(comm, 0) "실수령 급여" from emp; /*alias 줄때 공백이 있으면 ""로 묶어주기 ""묶어주지 않으면 오류발생*/
-- 연결함수: concat
select concat(ename, ' is a ', job) as "이름과 직업" from emp;
-- select 컬럼 연산자 값 from 테이블명: 행 단위 연산(요소별)
-- select 컬럼 연산자 칼럼 from 테이블명: 행 단위 연산
-- 관계 연산자: >, >= , < , <= , = , <> , !=
select ename, sal>3000 from emp; /* 0:False, 1:True */

 select ename, sal from emp where sal>3000;
 select ename, sal from emp where sal=3000;
 select ename, sal from emp where sal>=3000;
 select ename, sal from emp where sal<3000;
 select ename, sal from emp where sal<=3000;
 select ename, sal from emp where sal<>3000; /*<>: standard*/
 select ename, sal from emp where sal!=3000;
 
 -- 문자열
 select ename from emp where ename  < 'SMITH';
 select ename, sal from emp where ename  = 'SMITH';
 
-- like (문자열, 날짜) 특수기호(%, _)
-- 이름이 s로 시작
select ename, sal from emp where ename like 's%';
-- 이름이 s로 끝
select ename, sal from emp where ename like '%s';
-- 이름에 M 존재하는 것
select ename, sal from emp where ename like '%M%';

-- 퀴즈 : 1982년도 입사한 사원을 구하시오.
select * from emp where HIREDATE like '1982%';

select ename, sal from emp where ename like '%T_'; /*끝에서 두번째 글자가 T*/
select ename, sal from emp where ename like '%T__'; /*끝에서 세번째 글자가 T*/
select ename, sal from emp where ename like '_M%'; /*앞에서 두번째 글자가 M*/ # '_'는 한개의 글자를 의미  

-- 정규식 rlike 특수기호( +, * , ^ , $ , [] , | ,  \w, \W,   ...등등 ) : 표준은 아니나 dbms에서 많이 사용함
-- 포함
select ename, sal from emp where ename rlike 'M';
-- 시작메타기호: ^
select ename, sal from emp where ename rlike '^S';
-- 끝메타기호: $
select ename, sal from emp where ename rlike 'S$';
-- 문자의 집합 중 하나
select ename, sal from emp where ename rlike '[SM]';
select ename, sal from emp where ename rlike '^[SM]';
select ename, sal from emp where ename rlike 'CO|LE|NG'; /*CO or LE oe NG*/

-- 퀴즈: 9월에 입사한 사원을 구하시오.
select  ename, HIREDATE from emp where HIREDATE rlike '-09-';
-- 1982년도 이전에 입사한 사원
select ename, HIREDATE from emp where HIREDATE  < '1982-01-01';

-- 퀴즈: 1982년 07월 이전에 입사한 사원을 구하시오.
select ename, hiredate from emp where HIREDATE < '1982-07-01';
select ename, hiredate from emp where HIREDATE < '1982/07/01';


-- 논리 연산자: not , and , or , in , between
select * from emp where deptno=10 and job='MANAGER';
select * from emp where deptno=10 or job='MANAGER';

select * from emp where not deptno=10;


-- 퀴즈 : 부서번호가 10이 아니면서 job이 manager인 데이터를 출력하시오.
select * from emp where not deptno=10 and job='MANAGER'; 
select * from emp where not (deptno=10 and job='MANAGER'); /*() 빼고 다 출력*/

-- 부서 번호가 10 또는 20번
select * from emp where deptno=10 or deptno=20;
select * from emp where deptno in(10,20);
select * from emp where not  (deptno=10 or deptno=20);

select * from emp where deptno not in(10,20);

-- between 연산자 
-- 200 <=sal<=3000 X
select * from emp where sal>=2000 and sal<=3000;
select * from emp where sal between 2000 and 3000;

-- 3분 퀴즈
-- 1) 커미션이 300 이거나 500 이거나 1400 인 사원을 선택
select * from emp where comm in (300, 500 ,1400);
-- 2) 급여가 2000 미만이거나 3000 초과인 사람을 검색 
select * from emp where sal<2000 or sal>3000;
select * from emp where sal not between 2000 and 3000;
-- 2분 퀴즈 : 1982년에 입사한 사원을 출려하시오.
select * from emp where HIREDATE between '1982-01-01' and '1982-12-31'; 








 