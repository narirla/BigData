select * 
from A;

select * 
from B;

-- 합집합 공통적인걸 하나만 나오게
select * 
from A
union
select * 
from B;

-- 공통적인걸 다 나오게
select * 
from A
union all
select * 
from B;

-- 교집합
-- select * 
-- from A
-- intersect
-- select * 
-- from B;
-- 교집합
select * 
from A inner join B using(id)
where A.name = B.name;

-- select * 
-- from A
-- minus
-- select * 
-- from B;

select * 
from A
where not exists(
	select 1 
    from B
    where A.id = B.id);


select * 
from A
where not exists(
	select 1 
    from B
    where B.id = A.id);
    
select * 
from A; -- id : 10 11 12 13 15

select * 
from B; -- id: 10 11 12 13 14

select *
from sleep2016;


select * 
from sleep2014
union all
select *
from sleep2015
union all
select *
from sleep2016;

-- 년도별 평균 사망자를 보여주시오.
select left(구분,4) as 년도, avg(`사망(명)`) as '사망 평균'
from (
select * from sleep2014
union all
select *from sleep2015
union all
select *from sleep2016) sleepall_view
group by left(구분,4);


select left(구분,4) as 년도, avg(`사망(명)`) as '사망 평균'
from sleepall_view /*sleep2014 + sleep2015 + sleep2016 를 join에서 만든 가상의 view*/
group by left(구분,4);

select * 
from (select ename, sal, dense_rank() over(order by sal desc) as sal_rank
		from emp) as my
where sal_rank<=5;

select * 
from erank_view
where sal_rank<=5;







