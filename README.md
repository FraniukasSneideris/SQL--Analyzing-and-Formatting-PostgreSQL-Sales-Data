# SQL--Analyzing-and-Formatting-PostgreSQL-Sales-Data

## Overview

This project involves analyzing and cleaning sales data from a hypothetical Super Store's PostgreSQL database. The focus is on uncovering key insights about the store's product sales, profitability, and order quantities, while handling missing or inconsistent data through SQL-based data cleaning techniques.

## Purpose

The primary objective of this project is to clean the database and conduct insightful analyses to help the Super Store optimize its sales strategies and inventory management. Key focus areas include:
1. Identifying the top 5 products from each category based on highest total sales.
2. Estimating missing quantities in orders based on available sales data.

----

## Data Analysis

### 1. **Top 5 Products by Category (Based on Sales)**
This analysis identifies the top 5 products in each category based on total sales. By ranking products within each category by their total sales, we gain insights into which products are driving the most revenue in different categories.

#### Query
This query identifies the top 5 products within each category based on total sales. It uses a RANK() window function to rank products within their respective categories, sorting them by sales in descending order. The query calculates the total sales and profit for each product, rounding the values to two decimal places. The final output includes the category, product name, total sales, total profit, and product rank, filtered to only show the top 5 products per category.
```sql
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
```
#### Query result
```sql
index | category        | product_name                                         | product_total_sales | product_total_profit | product_rank
------+-----------------+-----------------------------------------------------+---------------------+----------------------|--------------
0     | Furniture       | Hon Executive Leather Armchair, Adjustable          | 58193.48            | 5997.25              | 1
1     | Furniture       | Office Star Executive Leather Armchair, Adjustable  | 51449.8             | 4925.8               | 2
2     | Furniture       | Harbour Creations Executive Leather Armchair, Adjustable | 50121.52         | 10427.33             | 3
3     | Furniture       | SAFCO Executive Leather Armchair, Black             | 41923.53            | 7154.28              | 4
4     | Furniture       | Novimex Executive Leather Armchair, Adjustable      | 40585.13            | 5562.35              | 5
5     | Office Supplies | Eldon File Cart, Single Width                       | 39873.23            | 5571.26              | 1
6     | Office Supplies | Hoover Stove, White                                 | 32842.6             | -2180.63             | 2
7     | Office Supplies | Hoover Stove, Red                                   | 32644.13            | 11651.68             | 3
8     | Office Supplies | Rogers File Cart, Single Width                      | 29558.82            | 2368.82              | 4
9     | Office Supplies | Smead Lockers, Industrial                          | 28991.66            | 3630.44              | 5
10    | Technology      | Apple Smart Phone, Full Size                       | 86935.78            | 5921.58              | 1
11    | Technology      | Cisco Smart Phone, Full Size                       | 76441.53            | 17238.52             | 2
12    | Technology      | Motorola Smart Phone, Full Size                    | 73156.3             | 17027.11             | 3
13    | Technology      | Nokia Smart Phone, Full Size                       | 71904.56            | 9938.2               | 4
14    | Technology      | Canon imageCLASS 2200 Advanced Copier              | 61599.82            | 25199.93             | 5
```

### 2. Imputing Missing Quantities
The task is to estimate missing quantity values for products where the quantity is unavailable, using the unit price derived from existing sales and discount data.

#### Query
This query aims to estimate the missing quantity values for orders that have null quantities. It does this by calculating the average unit price for each product using available sales data. It then uses the unit price to calculate the missing quantity by dividing the total sales by the unit price. The query incorporates sales, discount, market, region, and the calculated quantity, rounding the final quantity to the nearest whole number. The result helps estimate missing order quantities, improving inventory accuracy.
```sql
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
```
#### Query result
```sql
index | product_id          | discount | market | region | sales   | quantity | calculated_quantity
------+---------------------+----------+--------+--------+---------+----------+---------------------
0     | TEC-STA-10003330     | 0        | Africa | Africa | 506.64  | NULL     | 2
1     | FUR-ADV-10000571     | 0        | EMEA   | EMEA   | 438.96  | NULL     | 4
2     | FUR-BO-10001337      | 0.15     | US     | West   | 308.499 | NULL     | 3
3     | TEC-STA-10004542     | 0        | Africa | Africa | 160.32  | NULL     | 4
4     | FUR-ADV-10004395     | 0        | EMEA   | EMEA   | 84.12   | NULL     | 2
```
----


