-- emp join 문제
select * from emp; 
select * from dept; 
-- 1. 10번 부서 중에서 30번 부서에는 없는 업무를 하는 사원의 사원번호, 이름, 부서명, 입사일, 지역을 출력시요
select ename 사원명, empno 사원번호 , hiredate 입사일, loc 지역, DNAME 부서명
from emp join dept using(deptno)
where deptno = 10 
and job not in(select job
				from emp
                where deptno = 30);
-- 2. 시카고에서 근무하는 사원의 이름과 근무지역을 출력하시오
select ename, loc
from emp join dept using(deptno)
where loc ='CHICAGO';

-- 3.  위치가 NEW YORK인 사원들 중 입사일이 가장 늦은사람의 부서명과 사원이름을 출력하시요.
select dname 부서명, ename 사원이름, HIREDATE 입사일
from emp join dept using(deptno)
where loc = 'NEW YORK'
order by HIREDATE desc limit 1;

select dname 부서명, ename 사원이름, HIREDATE 입사일
from emp join dept using(deptno)
where loc = 'NEW YORK' and hiredate = (
select 

-- emp 문제
-- 4. 요일별 급여의 평균을 구하시요.(view 테이블을 만들어서 해결)
select ename, sal, hiredate,
case dayofweek(hiredate)
	when 1 then '일'
	when 2 then '월'
	when 3 then '화'
	when 4 then '수'
	when 5 then '목'
	when 6 then '금'
	else '토'
end as 입사 요일
from emp;

select avg(sal), `입사 요일`
from hire_dayofweek
GROUP BY `입사 요일`;

-- 5.  le사원이름, 입사일로부터 4개월이 지난 후의 날 , 입사일로부터 90일 후의 날, 급여 를 출력하시요.
select ename, date_add(hiredate, interval 4 month) as '입사일 4개월 후', 
	date_add(hiredate, interval 90 day) '입사일 90일 후', sal '급여'
from emp;

-- 6. 년도 및 월별 급여의 평균을 구하시요.
select YEAR(hiredate) as year, MONTH(hiredate) as month, avg(sal) as avg_sal
from emp
group by YEAR(hiredate), MONTH(hiredate)
order by YEAR(hiredate), MONTH(hiredate);


-- 교통사고 데이터( 도로교통공단_전국_사망교통사고정보(2018).csv 테이블생성후)
-- 6. 부산에서 발생한 총 사망자수를 구하시요
select * from data2018;
select sum(사망자수)
from data2018
where 발생지시도 = '부산'; 

-- 7. 부산지역 월요일에 발생한 사상자수 사고유형 법규위반을 구하시요
select 사상자수, 사고유형, 법규위반
from data2018
where 발생지시도 = '부산' and 요일 = '월';

SELECT `사상자수`, `사고유형`, `법규위반` 
FROM KOREA_TRAFFIC_ACCIDENT 
WHERE `발생지시도` = '부산' AND `요일` = '월';
-- 8. 법규위반별 순위를 구하시요.
select 법규위반 , count(법규위반) , rank() over( order by count(법규위반)) 
from data2018
group by 법규위반;
-- 9. 부산에서 일어난 요일별 사망자수, 사상자수 를 출력하시요( 단, 월,화,...일 순으로 )

-- crime_in_Seoul.csv 테이블 생성후
-- 10. 살인발생이 가장높은 관서명, 살인발생,살인검거를 출력하시요
select * from crime_in_seoul;
select 관서명, `살인 발생`,`살인 검거`
from crime_in_seoul
where `살인 발생` = ( select max(`살인 발생`)
					 from crime_in_seoul);
-- 11. 절도발생, 절도검거, 절도검거율 을 출력하시요

-- 12. 살인발생이 10건 이상이면 높음, 5건 이상이면 보통, 나머지는 적음으로 표시하는 발생정도 컬럼을 추가하여 (관서명, 살인발생,살인검거,발생정도) 를 출력하시요 

-- 13. 강도발생이 높은 톱5를 구하시요
-- (관서명, 강도발생, 강도검거)

-- 14. 관서명과 구별 컬럼을 출력하시요 ( 구별에는 중부, 종로, 남대문 ,,.... 로 출력할것)
-- ===============
-- 관서명   구별
-- 중부서   중부
-- 종로서   종로
-- 남대문서 남대문
-- ...


