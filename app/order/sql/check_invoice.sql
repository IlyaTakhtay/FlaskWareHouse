SELECT pr_id, product_name, amount, volume, cost, time_arrive
FROM product join product_in_invoice using(pr_id) join invoice using(inv_id) where (inv_id = '$inv_id');