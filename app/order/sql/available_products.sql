select distinct product_name, product_in_invoice.amount, time_arrive, time_departure, cost
from product  join product_in_invoice using (pr_id) join invoice using(inv_id)
where (sup_id = '$sup_id');