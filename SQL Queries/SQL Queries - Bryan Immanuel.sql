# query 1
select maritalstatus, avg(age) from customer  
group by maritalstatus  

# query 2
select gender , avg(age) from customer 
group by gender 

# query 3
select s.storename, sum(t.qty) 
from store s inner join "transaction" t on s.storeid = t.storeid 
group by s.storename order by sum(t.qty) desc limit 1

# query 4
select p.productname, sum(t.totalamount)
from product p inner join "transaction" t on p.productid = t.productid 
group by p.productname order by sum(t.totalamount) desc limit 1