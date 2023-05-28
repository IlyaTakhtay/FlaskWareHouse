SELECT sup_id, prod_amount,prod_cost
FROM warehouse.supplier_report
where report_month = '$rep_month' and report_year = '$rep_year'