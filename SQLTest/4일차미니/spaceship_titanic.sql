select * from space;
-- 1. homeplant별로 몇명인지 확인하시오.
select HomePlanet, count(*) as 인원수
from space
group by HomePlanet;

-- 2.homeplant이 NULL인 값을 Moon으로 채우고 컬럼이 없는 뷰테이블을 만드시요
update space
set HomePlanet = 'Moon'
where HomePlanet is null or '';

select count(*), HomePlanet
from space
where HomePlanet = 'Moon';

-- 2-1 이름이 null인 사람을 NONAME으로 변경
update space
set name = 'NONAME'
where name = '';

select count(*), name
from space
where name = 'NONAME';

-- 3.나이분류를 출력하시요.
-- 0~15(미성년자), 16~25(청년), 26~35(중년),36~60(장년), 61~(노년)으로 분류
select name, age,
case 
	when age between 0 and 15 then '미성년자'
	when age between 16 and 25 then '청년'
	when age between 26 and 35 then '중년'
	when age between 36 and 60 then '장년'
	else '노년'
end as '나이분류'
from space;

-- 4.룸서비스, 스파, 푸드 코드 금액을 다 합친 금액 top5를 구하시오. 
select name, sum(ROOMSERVICE + FOODCOURT + SHOPPINGMALL + SPA + VRDECK) as '지불비용'
from space
group by name;

select dense_rank() over(order by sum(ROOMSERVICE + FOODCOURT + SHOPPINGMALL + SPA + VRDECK)) as '랭킹'
from space
group by name; 

SELECT NAME, 지불비용, 랭킹
FROM (
    SELECT NAME, HomePlanet,
           SUM(ROOMSERVICE + FOODCOURT + SHOPPINGMALL + SPA + VRDECK) AS '지불비용', 
           DENSE_RANK() OVER(ORDER BY SUM(ROOMSERVICE + FOODCOURT + SHOPPINGMALL + SPA + VRDECK) DESC) AS '랭킹' 
    FROM space 
    GROUP BY NAME, HomePlanet
) AS ranked
WHERE 랭킹 <= 5;

#5. Destination별 승객수를 확인하고, 가장 많은 승객이 향하는 Destination을 찾으시오
select Destination, count(*) as 승객수
from space
group by Destination
order by 승객수 desc
limit 1;

select Destination, count(*) as 승객수
from space
group by Destination
order by 승객수 desc
limit 1;

SELECT DESTINATION, COUNT(*) FROM space GROUP BY DESTINATION;
#6. 각 HomePlanet별로 가장 많은 총비용을 지불한 승객의 정보를 조회하시오
SELECT s.PassengerId, s.Name, s.HomePlanet, s.RoomService, s.FoodCourt, s.ShoppingMall,
	   s.Spa, s.VRDeck, (s.RoomService + s.FoodCourt + s.ShoppingMall + s.Spa + s.VRDeck) AS total_spend
FROM space s 
JOIN ( SELECT HomePlanet, MAX(RoomService + FoodCourt + ShoppingMall + Spa + VRDeck) AS max_spend
		FROM space
		GROUP BY HomePlanet) m ON s.HomePlanet = m.HomePlanet
							  AND (s.RoomService + s.FoodCourt + s.ShoppingMall + s.Spa + s.VRDeck) = m.max_spend;

#7. 고액 지출 승객(상위 10%)을 찾고, 이들의 평균 나이를 구하시오
select name, 지불비용, 랭킹, HomePlanet
from (select name, SUM(ROOMSERVICE + FOODCOURT + SHOPPINGMALL + SPA + VRDECK) AS '지불비용', 
           DENSE_RANK() OVER(ORDER BY SUM(ROOMSERVICE + FOODCOURT + SHOPPINGMALL + SPA + VRDECK) DESC) AS '랭킹',
           HOMEPLANET
	from space
    group by name, HomePlanet
) as ranked
where 랭킹 <= (select count(*) from space)*0.1;

#8. Cabin의 Deck 정보를 이용하여, 가장 많은 승객이 속한 Deck을 구하시오(참고! - Deck = SUBSTRING_INDEX(Cabin, '/', 1))
SELECT DESTINATION, SUBSTRING_INDEX(Cabin, '/', 1) AS 'Deck' FROM space;

SELECT deck, cnt
FROM (
    SELECT
        SUBSTRING_INDEX(Cabin, '/', 1) AS deck,
        COUNT(*) AS cnt
    FROM space
    WHERE Cabin IS NOT NULL AND Cabin <> ''
    GROUP BY SUBSTRING_INDEX(Cabin, '/', 1)
) AS t
ORDER BY cnt DESC
LIMIT 1;

#9. 동명이인(NONAME) 중에서 같은 출발지, 같은 목적지인 사람은 몇명인지 구하시오
SELECT NAME, DESTINATION, COUNT(*) FROM space WHERE NAME = 'NONAME' GROUP BY DESTINATION;

#10. Cryosleep(냉동수면)을 한 사람(TRUE인 사람) 중에서 중&장년층은 총 몇명인지 구하시오
select Cryosleep, name, age
from space
where Cryosleep = 'TRUE'
group by CryoSleep;

SELECT name, CryoSleep, age,
	CASE 
	  WHEN age BETWEEN 0 AND 15 THEN '미성년자'
	  WHEN age BETWEEN 16 AND 25 THEN '청년'
	  WHEN age BETWEEN 26 AND 35 THEN '중년'
	  WHEN age BETWEEN 36 AND 60 THEN '장년'
	  ELSE '노년'
	END AS 나이분류
FROM space
WHERE CryoSleep = 'TRUE'
	and (age between 26 AND 60);


