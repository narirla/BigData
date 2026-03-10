SELECT * FROM space;

#1. homeplanet별로 몇명인지 확인하기
SELECT HOMEPLANET, COUNT(*) FROM space WHERE HOMEPLANET = 'EARTH';
SELECT COUNT(*) FROM space WHERE HOMEPLANET = 'EUROPA';

SELECT HOMEPLANET, COUNT(*) FROM space GROUP BY HOMEPLANET;

#2. homeplanet이 null인 값을 Moon으로 교체
UPDATE space SET HOMEPLANET = 'Moon' WHERE HOMEPLANET IS NULL OR HOMEPLANET = '';
UPDATE space SET NAME = 'NONAME' WHERE HOMEPLANET IS NULL OR NAME = '';

SELECT COUNT(*) FROM space WHERE HOMEPLANET IS NULL;
SELECT COUNT(*) FROM space WHERE HOMEPLANET = '';

#3. 0~15(미성년자), 16~25(청년), 26~35(중년), 36~60(장년), 61~(노년)으로 분류
SELECT AGE,
    CASE 
        WHEN AGE >= 0 AND AGE <=15 THEN '미성년자'
        WHEN AGE >= 16 AND AGE <=25 THEN '청년'
        WHEN AGE >= 26 AND AGE <=35 THEN '중년'
        WHEN AGE >= 36 AND AGE <=60 THEN '장년'
        ELSE '노년'
    END AS '나이분류'
FROM space;

#4. 승객의 편의시설 지불 비용 top5 랭킹 매기기(동률 포함 DENSE_RANK()사용)
# RoomService + FoodCourt + ShoppingMall + Spa + VRDECK = 지불비용
SELECT NAME, SUM(ROOMSERVICE + FOODCOURT + SHOPPINGMALL + SPA + VRDECK) AS '지불비용' FROM space GROUP BY NAME;
SELECT DENSE_RANK() OVER(ORDER BY SUM(ROOMSERVICE + FOODCOURT + SHOPPINGMALL + SPA + VRDECK) DESC) AS '랭킹' FROM space GROUP BY NAME;

SELECT NAME, 지불비용, 랭킹, HOMEPLANET
FROM (
    SELECT NAME, 
           SUM(ROOMSERVICE + FOODCOURT + SHOPPINGMALL + SPA + VRDECK) AS '지불비용', 
           DENSE_RANK() OVER(ORDER BY SUM(ROOMSERVICE + FOODCOURT + SHOPPINGMALL + SPA + VRDECK) DESC) AS '랭킹',
           HOMEPLANET
    FROM space 
    GROUP BY NAME, HOMEPLANET
) AS ranked
WHERE 랭킹 <= 5;

#5. Destination별 승객수를 확인하고, 가장 많은 승객이 향하는 Destination을 찾으시오
SELECT * FROM space;
SELECT DESTINATION, COUNT(*) FROM space GROUP BY DESTINATION; # 가장 높은건 TRAPPIST-1e(2604명)

#6. 각 HomePlanet별로 가장 많은 총비용을 지불한 승객의 정보를 조회하시오
SELECT NAME, HOMEPLANET, SUM(ROOMSERVICE +FOODCOURT + SHOPPINGMALL + SPA + VRDECK) AS '지불비용';

SELECT s.NAME, s.지불비용, s.HOMEPLANET
FROM (
    SELECT NAME, 
           SUM(ROOMSERVICE + FOODCOURT + SHOPPINGMALL + SPA + VRDECK) AS '지불비용',
           HOMEPLANET
    FROM space
    WHERE HOMEPLANET = 'EARTH'
    GROUP BY NAME, HOMEPLANET
) AS s
INNER JOIN (
    SELECT MAX(지불비용) AS '최대지불비용'
    FROM (
        SELECT SUM(ROOMSERVICE + FOODCOURT + SHOPPINGMALL + SPA + VRDECK) AS '지불비용'
        FROM space
        WHERE HOMEPLANET = 'EARTH'
        GROUP BY NAME, HOMEPLANET
    ) AS temp
) AS m ON s.지불비용 = m.최대지불비용;


SELECT s.NAME, s.HOMEPLANET, s.지불비용
FROM (
    SELECT NAME, 
           HOMEPLANET,
           SUM(ROOMSERVICE + FOODCOURT + SHOPPINGMALL + SPA + VRDECK) AS '지불비용'
    FROM space
    GROUP BY NAME, HOMEPLANET
) AS s
INNER JOIN (
    SELECT HOMEPLANET,
           MAX(지불비용) AS '최대지불비용'
    FROM (
        SELECT HOMEPLANET,
               SUM(ROOMSERVICE + FOODCOURT + SHOPPINGMALL + SPA + VRDECK) AS '지불비용'
        FROM space
        GROUP BY NAME, HOMEPLANET
    ) AS temp
    GROUP BY HOMEPLANET
) AS m ON s.HOMEPLANET = m.HOMEPLANET AND s.지불비용 = m.최대지불비용;

#7. 고액 지출 승객(상위 10%)을 찾으시오
# 총인원수 - 3740
SELECT COUNT(*) FROM space;

SELECT NAME, 지불비용, 랭킹, HOMEPLANET
FROM (
    SELECT NAME, 
           SUM(ROOMSERVICE + FOODCOURT + SHOPPINGMALL + SPA + VRDECK) AS '지불비용', 
           DENSE_RANK() OVER(ORDER BY SUM(ROOMSERVICE + FOODCOURT + SHOPPINGMALL + SPA + VRDECK) DESC) AS '랭킹',
           HOMEPLANET
    FROM space 
    GROUP BY NAME, HOMEPLANET
) AS ranked
WHERE 랭킹 <= (SELECT COUNT(*) FROM SPACE) * 0.1;

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

#9. 동명이인(NONAME) 중에서 같은 출발지, 같은 목적지인 사람은 몇명인지 구하시오 (NONAME 총 81명)
SELECT NAME, HOMEPLANET, DESTINATION, COUNT(*) FROM space WHERE NAME = 'NONAME' GROUP BY HOMEPLANET, DESTINATION;

#10. Cryosleep(냉동수면)을 한 사람(TRUE인 사람) 중에서 중&장년층을 구하시오
SELECT NAME, CRYOSLEEP, AGE,
    CASE 
        WHEN AGE >= 0 AND AGE <=15 THEN '미성년자'
        WHEN AGE >= 16 AND AGE <=25 THEN '청년'
        WHEN AGE >= 26 AND AGE <=35 THEN '중년'
        WHEN AGE >= 36 AND AGE <=60 THEN '장년'
        ELSE '노년'
    END AS '나이분류'
FROM space 
WHERE 
	CRYOSLEEP = 'TRUE'
	AND (AGE >=26 AND AGE <=60);