# SQL--Analyzing-and-Formatting-PostgreSQL-Sales-Data

## Overview

This project involves analyzing and cleaning sales data from a hypothetical Super Store's PostgreSQL database. The focus is on uncovering key insights about the store's product sales, profitability, and order quantities, while handling missing or inconsistent data through SQL-based data cleaning techniques.

## Introduction

This project involves cleaning and analyzing a PostgreSQL database that contains data from a hypothetical Super Store. The database includes several tables that are crucial for our analysis:

### 1. **orders**
Contains details about each order placed in the store.

| Column       | Definition                                                | Data Type         | Comments                                                   |
|--------------|-----------------------------------------------------------|-------------------|-----------------------------------------------------------|
| row_id       | Unique Record ID                                          | INTEGER           |                                                           |
| order_id     | Identifier for each order in table                        | TEXT              | Connects to order_id in the returned_orders table         |
| order_date   | Date when order was placed                                | TEXT              |                                                           |
| market       | Market order_id belongs to                                | TEXT              |                                                           |
| region       | Region Customer belongs to                                | TEXT              | Connects to region in people table                        |
| product_id   | Identifier of Product bought                              | TEXT              | Connects to product_id in products table                  |
| sales        | Total Sales Amount for the Line Item                      | DOUBLE PRECISION  |                                                           |
| quantity     | Total Quantity for the Line Item                          | DOUBLE PRECISION  |                                                           |
| discount     | Discount applied for the Line Item                        | DOUBLE PRECISION  |                                                           |
| profit       | Total Profit earned on the Line Item                       | DOUBLE PRECISION  |                                                           |

### 2. **returned_orders**
Contains information about returned orders.

| Column       | Definition                                                | Data Type         | Comments                                                   |
|--------------|-----------------------------------------------------------|-------------------|-----------------------------------------------------------|
| returned     | Yes values for Order / Line Item Returned                 | TEXT              |                                                           |
| order_id     | Identifier for each order in table                        | TEXT              |                                                           |
| market       | Market order_id belongs to                                | TEXT              |                                                           |

### 3. **people**
Contains details about salespersons.

| Column       | Definition                                                | Data Type         | Comments                                                   |
|--------------|-----------------------------------------------------------|-------------------|-----------------------------------------------------------|
| person       | Name of Salesperson credited with Order                   | TEXT              |                                                           |
| region       | Region Salesperson is operating in                        | TEXT              | Connects to region in orders table                        |

### 4. **products**
Contains information about products available in the store.

| Column       | Definition                                                | Data Type         | Comments                                                   |
|--------------|-----------------------------------------------------------|-------------------|-----------------------------------------------------------|
| product_id   | Unique Identifier for the Product                         | TEXT              |                                                           |
| category     | Category Product belongs to                                | TEXT              |                                                           |
| sub_category | Sub Category Product belongs to                            | TEXT              |                                                           |
| product_name | Detailed Name of the Product                              | TEXT              |                                                           |

These tables are joined together using `product_id` from `products`, `order_id` from `orders`, and `region` from `people` to provide insights into sales and profitability across different categories and regions.

The two key queries in this analysis focus on:
1. **Finding the top 5 products from each category based on total sales.**
2. **Imputing missing quantity values for orders by estimating them based on available data and pricing factors.**


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
| index | category        | product_name                                         | product_total_sales | product_total_profit | product_rank |
|-------|-----------------|-----------------------------------------------------|---------------------|----------------------|--------------|
| 0     | Furniture       | Hon Executive Leather Armchair, Adjustable          | 58193.48            | 5997.25              | 1            |
| 1     | Furniture       | Office Star Executive Leather Armchair, Adjustable  | 51449.8             | 4925.8               | 2            |
| 2     | Furniture       | Harbour Creations Executive Leather Armchair, Adjustable | 50121.52         | 10427.33             | 3            |
| 3     | Furniture       | SAFCO Executive Leather Armchair, Black             | 41923.53            | 7154.28              | 4            |
| 4     | Furniture       | Novimex Executive Leather Armchair, Adjustable      | 40585.13            | 5562.35              | 5            |
| 5     | Office Supplies | Eldon File Cart, Single Width                       | 39873.23            | 5571.26              | 1            |
| 6     | Office Supplies | Hoover Stove, White                                 | 32842.6             | -2180.63             | 2            |
| 7     | Office Supplies | Hoover Stove, Red                                   | 32644.13            | 11651.68             | 3            |
| 8     | Office Supplies | Rogers File Cart, Single Width                      | 29558.82            | 2368.82              | 4            |
| 9     | Office Supplies | Smead Lockers, Industrial                          | 28991.66            | 3630.44              | 5            |
| 10    | Technology      | Apple Smart Phone, Full Size                       | 86935.78            | 5921.58              | 1            |
| 11    | Technology      | Cisco Smart Phone, Full Size                       | 76441.53            | 17238.52             | 2            |
| 12    | Technology      | Motorola Smart Phone, Full Size                    | 73156.3             | 17027.11             | 3            |
| 13    | Technology      | Nokia Smart Phone, Full Size                       | 71904.56            | 9938.2               | 4            |
| 14    | Technology      | Canon imageCLASS 2200 Advanced Copier              | 61599.82            | 25199.93             | 5            |


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
| index | product_id          | discount | market | region | sales   | quantity | calculated_quantity |
|-------|---------------------|----------|--------|--------|---------|----------|---------------------|
| 0     | TEC-STA-10003330     | 0        | Africa | Africa | 506.64  | NULL     | 2                   |
| 1     | FUR-ADV-10000571     | 0        | EMEA   | EMEA   | 438.96  | NULL     | 4                   |
| 2     | FUR-BO-10001337      | 0.15     | US     | West   | 308.499 | NULL     | 3                   |
| 3     | TEC-STA-10004542     | 0        | Africa | Africa | 160.32  | NULL     | 4                   |
| 4     | FUR-ADV-10004395     | 0        | EMEA   | EMEA   | 84.12   | NULL     | 2                   |

----

## Data Visualization and Further Analysis
*Please note: all visualizations were done with Python Pandas, Matplotlib and Seaborn. The code for graphics is in "data_visualizations.py".*
### Sales vs. Category by Market and by Region
![image](https://github.com/user-attachments/assets/979bc2ff-8ea0-4a3b-b92b-ff95770a4f02)
![image](https://github.com/user-attachments/assets/3a3294c4-2156-4ac6-af43-61c9e7ac4f41)
Working directly with a merge of the "orders" and "products" tables, we can see that the biggest sales took place on Asia-Pacific (APAC) for the categories Technology and Furniture, with similar numbers in sales, reaching over 1.3 million sales. On the flip-side, the lowest sales took place on Canada for Furniture.

Europe, LATAM and the US also exhibit huge sales numbers. On the flip-side, the lowest sales took place on Canada for Furniture.

Moving to the second graphic, we can take a closer look at sales: the winner by far is the Central APAC region for Technology category, with a whopping 1038449 total sales. Both Furniture and Office Supplies also exhibit their highest sales for the Central APAC region. 
### Top 5 Products by Category 
![image](https://github.com/user-attachments/assets/f7b102a1-e072-474e-85d9-e04c6e5dcfdd)
Here we focus on the results of the first assignment: finding out which are the Top 5 Products by Category based on Sales. This visualization takes the data directly for the resulting table of the first query "top_five_products_each_category.csv".
Though the biggest total sales correspond to the "Apple Smart Phone, Full Size", this product didn't generate the biggest total profit. The biggest total profit goes to the "Canon ImageCLASS 2200 Advanced Capler". As seen before, Technology category has the first place regarding both sales and profit, and it makes sense, since Technology usually is the biggest seller.
One interest observation is that though the "Hoover Stove, White" is within the Top 5 sold products for the Office Supplies, this product generated negative profit. This might be related to high discounts, high shipping cost, or data entry.
### Profit vs Sales with Quantity 
![image](https://github.com/user-attachments/assets/de2810b8-d654-49c8-8c44-28341261e2c4)
In this chart we can see that, even though usually the bigger the sales quantity, the bigger the profit, this is not always the case. Taking a closer look to the graphic we can see that there's actually a lot of sales which product negative profit. I would assume the company noticed this, otherwise they might get into troubles in the future!

----

## Conclusion
Through SQL-based analysis and data cleaning techniques, this project provided key insights into the Super Store's sales data. 

- **Top Products by Sales:** The analysis of top-selling products per category revealed that executive leather armchairs dominate the furniture segment, while high-end smartphones drive technology sales. However, certain office supply products showed negative profitability despite high sales, highlighting potential pricing or cost inefficiencies.
  
- **Handling Missing Quantities:** By estimating missing order quantities using derived unit prices, we improved data completeness and accuracy. This method ensures better inventory tracking and sales performance assessment without distorting existing sales data.

- **Data Visualization Insights:** Observing sales trends, profitability, and market segmentation revealed potential areas for business strategy improvements. The findings suggest optimizing product pricing, discount strategies, and stock management for better profitability.

Overall, this project demonstrated the power of SQL for sales analysis, allowing for data-driven decisions to enhance store performance and operational efficiency.





