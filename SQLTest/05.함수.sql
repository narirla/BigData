-- https://dev.mysql.com/doc/refman/8.4/en/functions.html

select 10%3;

select mod(10,3);
select empno, mod(empno,2) from emp;
-- 사번이 홀수인 사원이름과 사번을 보여주시오.
select empno, ename 
from emp
where empno%2=1;

select empno, ename 
from emp
where empno%2!=1;
 
select empno, ename 
from emp
where mod(empno,2)=1;

select * from
(select empno, mod(empno, 2) 사번 from emp) as MY
where 사번=1;

select -10, abs(-10);

select 34.5678, floor(34.5678);/*내림*/
select 34.5678, ceil(34.5678); /*올림*/
select 34.5678, round(34.5678);
select 34.5678, round(34.5678,2);
select 34.5678, round(34.5678,-1);
select 34.5678, truncate(34.5678,2);
select pow(3,2); #3의 2승

-- https://dev.mysql.com/doc/refman/8.4/en/string-functions.html

select 'MySql', upper('MySql');
select 'MySql', lower('MySql');

select ename, lower(ename) 
from emp;

-- C:\ProgramData\MySQL\MYSQL Server 8.0
-- my.ini
-- lower_case_table_names=0
-- 대소문자 구분한다.
select ename
from emp
where ename='smith';
-- 표준
select ename
from emp
where ename= upper('smith');

select 'MySql', length('MySql');

-- 사원이름 글자수가 네글자 이하인 직원을 검색하시오.
select ename
from emp
where length(ename)<=4;
-- substr(문자열, 위치, 갯수)
-- substring(문자열, 위치)
select substr('welcome to mysql',4,3);
select substr('welcome to mysql',4,4);
select substr('welcome to mysql',-3,2);
select substr('welcome to mysql',2); 
select substring('welcome to mysql',2); 

-- 퀴즈: 사원이름에 앞 두글자를 출력하시오.
select substr(ename, 1,2) 
from emp; 
--  정규식 이용
select regexp_substr('welcome to mysql','^[a-zA-Z]{2}');
select regexp_substr('welcome to mysql','^[a-z]{2}');
select regexp_substr('welcome to mysql','^[a-z]{2}');
select regexp_substr('welcome to mysql','c[a-z]+');

-- 퀴즈: 사원들의 입사 년도와 월을 출력하시오.
select hiredate from emp;
select ename, substr(hiredate,1,4) 입사년도, substr(hiredate,6,2) 월
from emp;

# instr('문자열','문자열') 2번인자 문자열의 위치 값
# locate('찾을 문자열','문자열', 시작위치) 2번인자 문자열의 위치 값
select instr('welcome to mysql', 'm'); /*특정 글자의 위치값*/
select instr('welcome to mysql', 'my'); 
select locate( 'm' ,'welcome to mysql'); 
select locate( 'm' ,'welcome to mysql', 7); 
## lpad('문자열', 칸의 수, '채울 문자열')
select lpad('mysql',20,'#');
select rpad('mysql',20,'#');

select lpad(ename,10,' ') 
from emp;

select ltrim('      mysql'); #공백제거
select rtrim('mysql         '); #공백제거
select trim('       mysql         '); #공백제거
select trim('-' from '---------mysql---------');
select ename, trim(ename)
from emp;

select replace('i like mysql', 'like','love');

select regexp_replace('33aa22bb', '[0-9]' ,''); # 패턴매칭
select regexp_replace('##--sql__3', '[0-9#_-]' ,''); # 데이터 클리닝 작업에 유용
select regexp_replace('i like program like phone', 'phone|program' ,'hi'); 
select regexp_replace('i like program like phone', 'p[a-z]+' ,'hi'); 

select left('sql tutorial', 3);
select right('sql tutorial', 3);

select format(123456789, 0); /*천단위*/
select format(123456789, 2);

-- 퀴즈: 사원이름과 급여를 천단위 표시로 출력하시오.
select ename, format(sal, 0)
from emp;

select ename, concat('\\',format(sal,0))
from emp; /*원화*/

-- 날짜 관련 함수
-- https://dev.mysql.com/doc/refman/8.4/en/date-and-time-functions.html
select now();
select sysdate();
select year('1988-01-12');

select ename, year(hiredate) 년도, month(hiredate) 월, day(hiredate) 일
from emp;

select year(now());
select hour(now()), minute(now()), second(now());
-- 1=sunday, 2=monday, ... 7=saturday
select dayofweek(now());
-- 사원이름과 입사한 요일을 출력하시오.
select ename 사원이름,
case dayofweek(hiredate)
	when  1 then '일요일'
	when  2 then '월요일'
	when  3 then '화요일'
	when  4 then '수요일'
	when  5 then '목요일'
	when  6 then '금요일'
	when  7 then '토요일'
end as '입사한 요일'       
from emp;

-- 시계열 통계: 집계(분기, 반기, 주간, 월, 년)
select quarter(now()); /*분기*/
-- 사원명과 입사일, 입사분기를 구하시오.
select ename, hiredate 입사일, quarter(hiredate) 분기
from emp;

-- 사원명, 입사일, 상반기 또는 하반기를 표시하시오.
select ename, hiredate, 
case
	when quarter(hiredate) <=2 then '상반기'
    when quarter(hiredate) >=3 then '하반기'
end as 반기
from emp;

select ename, hiredate, 
case
	when month(hiredate) <=6 then '상반기'
    else '하반기'
end as 반기
from emp;

select now();
-- https://dev.mysql.com/doc/refman/8.4/en/date-and-time-functions.html
-- https://dev.mysql.com/doc/refman/5.7/en/date-and-time-functions.html
select date_format(now(), '%Y년%m월%d일 %W');
-- 사원명, 입사일(0000년00월00일)
select ename, date_format(hiredate, '%Y년%m월%d일') 입사일
from emp;

select date_add(now(), interval 1 year); /*1년을 더함*/
select date_add(now(), interval 1 month); /*1개월을 더함*/
select date_add(now(), interval 2 month); /*2개월을 더함*/
select date_add(now(), interval 20 day); /*20일을 더함*/
select date_add(now(), interval 20 hour); /*20시간을 더함*/
select date_add(now(), interval 20 minute); /*20분을 더함*/
select date_add(now(), interval 20 second); /*20초을 더함*/
select date_sub(now(), interval 1 year); /*1년을 뺌*/
select date_add(now(), interval -1 year); /*1년을 뺌*/
select date_sub(now(), interval 1 month); /*1개월을 뺌*/

-- 오늘(now)을 기준으로 최근 1년이내에 입사한 직원을 찾는 SQL을 작성하시오.
select ename, hiredate
from emp
where hiredate >= date_add(now(), interval -1 year);
