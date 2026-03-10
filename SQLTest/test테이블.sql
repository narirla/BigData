
create table testA( name varchar(20), id int );
create table testB( name varchar(20), myid int );
insert into testA values( 'A', 1);
insert into testA values( 'B', 2);
insert into testA values( 'C', 3);
insert into testA values( 'D', 4);

insert into testB values( 'E', 1);
insert into testB values( 'A', 2);
insert into testB values( 'C', 3);
insert into testB values( 'F', 4);


create table A(  id int ,name varchar(20));
create table B(  id int , name varchar(20));

insert into A values( 10, 'A');
insert into A values( 11, 'AA');
insert into A values( 12, 'AAA');
insert into A values( 13, 'AAAA');
insert into A values( 15, 'AAAAA');

insert into B values( 10, 'B');
insert into B values( 11, 'BB');
insert into B values( 12, 'BBB');
insert into B values( 13, 'BBBB');
insert into B values( 14, 'BBBBB');
INSERT INTO B VALUES(10,'A');