-- top_five_products_each_category
SELECT *
FROM (SELECT category, 
             product_name, 
	         ROUND(SUM(CAST(sales AS NUMERIC)), 2) AS product_total_sales,
             ROUND(SUM(CAST(profit AS NUMERIC)), 2) AS product_total_profit,
	         RANK() OVER (PARTITION BY category ORDER BY SUM(sales) DESC) AS product_rank
      FROM orders AS o
      LEFT JOIN products AS p
      USING (product_id)
      GROUP BY category, product_name) AS subquery
WHERE product_rank < 6;

-- impute_missing_values
SELECT product_id,
       discount,
	   market,
	   region,
	   sales,
	   quantity, 
       ROUND(CAST(sales / subquery.avg_unit_price AS NUMERIC), 0) AS calculated_quantity
FROM orders
LEFT JOIN (SELECT product_id, AVG(unit_price) AS avg_unit_price
		   FROM ((SELECT product_id, sales / (quantity * (1 - discount)) AS unit_price
                  FROM orders
                  WHERE discount != 0 AND quantity IS NOT NULL)
                  UNION ALL
                  (SELECT product_id, sales / quantity AS unit_price
                   FROM orders
                   WHERE discount = 0 AND quantity IS NOT NULL)) AS a
           GROUP BY product_id) AS subquery
USING (product_id)
WHERE quantity IS NULL;
