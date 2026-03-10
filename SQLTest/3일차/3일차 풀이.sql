-- 1. 10번 부서 중에서 30번 부서에는 없는 업무를 하는 사원의 사원번호, 이름, 부서명, 입사일, 지역을 출력시요
SELECT DEPTNO, ENAME, DNAME, HIREDATE, LOC
FROM EMP JOIN DEPT USING(DEPTNO)
WHERE JOB NOT IN (SELECT JOB FROM EMP WHERE DEPTNO = 30)
AND DEPTNO = 10;

-- 2. 시카고에서 근무하는 사원의 이름과 근무지역을 출력하시오
SELECT ENAME, LOC
  FROM EMP JOIN DEPT USING(DEPTNO)
 WHERE LOC='CHICAGO';
 
 -- 3.  위치가 NEW YORK인 사원들 중 입사일이 가장 늦은사람의 부서명과 사원이름을 출력하시요.
 SELECT DNAME, ENAME FROM EMP E JOIN DEPT USING(DEPTNO)
 WHERE LOC='NEW YORK' AND HIREDATE=(SELECT MAX(HIREDATE) FROM EMP
 JOIN DEPT USING(DEPTNO) WHERE LOC='NEW YORK');
 
 -- 4. 입사요일별 급여의 평균을 구하시요.(view 테이블을 만들어서 해결)
SELECT AVG(SAL), `입사 요일` FROM HIRE_DAYOFWEEK
 GROUP BY `입사 요일`;

-- 아래를 talbe을 'hire_dayofweek' view로 변환
SELECT ENAME, SAL, HIREDATE
	 , CASE DAYOFWEEK(HIREDATE) WHEN 1 THEN '일'
								WHEN 2 THEN '월'
                                WHEN 3 THEN '화'
                                WHEN 4 THEN '수'
                                WHEN 5 THEN '목'
                                WHEN 6 THEN '금'
                                ELSE '토'
                                END AS '입사 요일'
  FROM EMP;
 
 -- 5.  사원이름, 입사일로부터 4개월이 지난 후의 날 , 입사일로부터 90일 후의 날, 급여 를 출력하시요.
 SELECT ENAME
	 , DATE_ADD(HIREDATE, INTERVAL 4 MONTH) '4개월 후'
     , DATE_ADD(HIREDATE, INTERVAL 90 DAY) '90일 후'
     , SAL
  FROM EMP;
  
-- 6. 년도 및 월별 급여의 평균을 구하시요.
SELECT YEAR(hiredate) AS year,
       MONTH(hiredate) AS month,
       AVG(sal) AS avg_sal
FROM emp
GROUP BY YEAR(hiredate), MONTH(hiredate)
ORDER BY year, month;

-- 7. 부산에서 발생한 총 사망자수를 구하시요
SELECT SUM(사망자수) AS total_dead
FROM accident
WHERE 발생지시도 = '부산';


-- 8. 부산지역 월요일에 발생한 사상자수, 사고유형, 법규위반
SELECT `사상자수`, `사고유형`, `법규위반` 
FROM KOREA_TRAFFIC_ACCIDENT 
WHERE `발생지시도` = '부산' AND `요일` = '월';

-- 9. 법규위반별 순위를 구하시요.
SELECT 법규위반,
       COUNT(법규위반) AS cnt,
       RANK() OVER (ORDER BY COUNT(법규위반) DESC) AS ranking
FROM accident
GROUP BY 법규위반;

-- 9. 부산에서 일어난 요일별 사망자수, 사상자수 를 출력하시요( 단, 월,화,...일 순으로 )

SELECT SUM(사망자수), SUM(사상자수), 요일
  FROM CAR_ACCIDENT
 WHERE 발생지시도='부산'
 GROUP BY 요일
 ORDER BY CASE 요일 
				WHEN '월' THEN 1
                WHEN '화' THEN 2
                WHEN '수' THEN 3
                WHEN '목' THEN 4
                WHEN '금' THEN 5
                WHEN '토' THEN 6
                WHEN '일' THEN 7
			END;
            
-- crime_in_Seoul.csv 테이블 생성후
-- 10. 살인발생이 가장높은 관서명, 살인발생,살인검거를 출력하시요
SELECT 관서명, `살인 발생`, `살인 검거`
FROM crime_in_seoul
WHERE `살인 발생` = (SELECT MAX(`살인 발생`) FROM crime_in_seoul);

-- view 생성
-- select `crime_in_seoul`.`살인 발생` AS `살인 발생`,`crime_in_seoul`.`살인 검거` AS `살인 검거`,`crime_in_seoul`.`강도 발생` AS `강도 발생`,`crime_in_seoul`.`강도 검거` AS `강도 검거`,`crime_in_seoul`.`강간 발생` AS `강간 발생`,`crime_in_seoul`.`강간 검거` AS `강간 검거`,cast(replace(`crime_in_seoul`.`절도 발생`,',','') as signed) AS `절도 발생`,`crime_in_seoul`.`절도 검거` AS `절도 검거`,cast(replace(`crime_in_seoul`.`폭력 발생`,',','') as signed) AS `폭력 발생`,cast(replace(`crime_in_seoul`.`폭력 검거`,',','') as signed) AS `폭력 검거` from `crime_in_seoul`
 
-- 11. 절도발생, 절도검거, 절도검거율 을 출력하시요
select (`절도 검거`/`절도 발생`)*100 절도검거율 from crime_seoul_view;


-- 12. 살인발생이 10건 이상이면 높음, 5건 이상이면 보통, 나머지는 적음으로 표시하는 발생정도 컬럼을 추가하여
-- (관서명, 살인발생,살인검거,발생정도) 를 출력하시요 
select 관서명, `살인 발생`, `살인 검거`,
case
	when `살인 발생` >=10 then '높음'
	when `살인 발생` >=5 then '보통'
	else '적음'
end as 발생정도
from crime_seoul_view;

-- 13. 강도발생이 높은 톱5를 구하시요
-- (관서명, 강도발생, 강도검거)

select *
from ( select 관서명, `강도 발생`, `강도 검거`, 
dense_rank() over( order by `강도 발생` desc)  as ranks
from crime_seoul_view ) as my
where ranks<=5;

-- 14. 관서명과 구별 컬럼을 출력하시요 ( 구별에는 중부, 종로, 남대문 ,,.... 로 출력할것)
-- ===============
-- 관서명   구별
-- 중부서   중부
-- 종로서   종로
-- 남대문서 남대문
 

-- length: 영문문자열, 한글은 글자 한개당 2개씩 길이가 계산됨.
-- : 영문문자열, 한글은 글자 한개당 2개씩 길이가 계산됨.
select 관서명, left(관서명, char_length(관서명)-1)
from crime_seoul_view;

-- select 관서명 from crime_seoul_view;
-- select regexp_substr(관서명, '([가-힣]+)서$',1) 
-- from crime_seoul_view;




 