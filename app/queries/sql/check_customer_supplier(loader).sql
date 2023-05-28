select inv_id,supplier_name,phone from invoice join supplier using(sup_id)
where (inv_id = '$inv_id')