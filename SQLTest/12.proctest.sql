call show_all_users();

call get_student_by_age(20);
call get_student_by_age(30);

call get_student_name(20, @name);
select @name;

-- 함수 생성 허용
SET GLOBAL log_bin_trust_function_creators = 1;

select add_two_numbers(10,20);

select ename, sal, add_two_numbers(sal,2)
from emp;

select hiredate, get_half(hiredate)
from emp;