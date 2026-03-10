drop table emp01;
drop table dept01;
drop table myseq;

-- emp 와 동일한 복사본 테이블 생성
create table emp01 as
select * from emp;

select * from emp01;

-- 데이터 제외 dept 테이블 스키마 복사
create table dept01 like dept;
select * from dept01;

insert into dept01
select * from dept;

select * from dept01;

create table myseq(
	id int auto_increment primary key,
    name varchar(50),
    addr varchar(100)
);

insert into myseq(name, addr) values('홍길동','서을시');
insert into myseq(name, addr) values('이순신','부산시');

select * from myseq;

set SQL_SAFE_UPDATES = 0;

update emp01 
set deptno = 21, job = 'test1'
where deptno = 20; /*where 조건이 없으면 싹 다 바뀜*/

select * from emp01; 

-- 모든 직원의 급여를 10% 인상해라.
update emp01
set sal = sal*1.1;

-- 1981년도 입사한 사원의 입사일을 오늘로 수정하시오.
update emp01
set hiredate = date(now())
where year(hiredate) = 1981;

-- 사원 중 급여가 4000 이상인 사원들의 급여만 500씩 삭감
update emp01
set sal = sal-500
where sal>= 4000;

-- dept01 20번 부서의 지역명을 30번 부서의 지역명으로 변경하시오.
select * from dept01;

update dept01
set loc = (select loc
			from (select loc 
					from dept01
					where deptno = 30) as my)
where deptno = 20;

-- dept01의 10번 부서명과 지역명을 40번 부서의 부서명, 지역명으로 변경하시오.
UPDATE dept01 
SET dname = (SELECT dname
			  FROM (SELECT  dname
					 FROM dept01
					WHERE deptno = 40) AS my),
    loc = (SELECT loc
			FROM (SELECT loc
				   FROM dept01
				  WHERE deptno = 40) AS my)
WHERE deptno = 10;

-- NEW YORK(dept)에 위치한 부서 소속 사원들의 급여를 1000 인상하시오.(emp)
update emp01
set sal = sal+1000
where deptno = (select deptno
				 from dept
                 where loc ='NEW YORK');
select * from emp01;

-- delete: where 처리된다, transaction 처리
-- truncate: 모두 삭제, 빠르다, transaction X
-- 모두 삭제

-- drop table emp01; -- table  포함 삭제
-- truncate table emp01; -- 데이터만 삭제
-- delete from emp01; -- 복구가능

delete from emp01 
where deptno = 21;
-- 사원 테이블에서 부서명이 SALES(dept)인 사원을 모두 삭제 하시오.
delete from emp01 
where deptno = (select deptno from dept where dname = 'SALES');