import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Getting and Preparing the Data
orders = pd.read_csv('orders.csv')
products = pd.read_csv('products.csv')
or_prod = orders.merge(products, on='product_id')

top_five_products_each_category = pd.read_csv('top_five_products_each_category.csv')
top_five_products_each_category.rename(columns={'product_total_sales': 'Total Sales'}, inplace=True)
top_five_products_each_category.rename(columns={'category': 'Category'}, inplace=True)


# Sales by Category and Market - Heatmap
sales_pivot = or_prod.pivot_table(values='sales', index='category', columns='market', aggfunc='sum')

plt.figure(figsize=(18, 6))
sns.heatmap(sales_pivot, annot=True, cmap='coolwarm', fmt='.2f', linewidths=0.5)
plt.title('Sales by Category and Market')
plt.xlabel('Market')
plt.ylabel('Category')
plt.show()

# Sales by Category and Region - Heatmap
sales_pivot = or_prod.pivot_table(values='sales', index='category', columns='region', aggfunc='sum')

plt.figure(figsize=(18, 6))
sns.heatmap(sales_pivot, annot=True, cmap='coolwarm', fmt='.2f', linewidths=0.5)
plt.title('Sales by Category and Region')
plt.xlabel('Region')
plt.ylabel('Category')
plt.show()

# Top 5 Products by Category 
sns.scatterplot(x='product_total_profit', y='product_name', data=top_five_products_each_category, hue='Category', size='Total Sales', sizes=(20, 200), palette='magma')
plt.xlabel('Product Total Profit')
plt.ylabel('Product Name')
plt.show()

# Profit vs Sales with Quantity (Bubble Chart)
plt.figure(figsize=(12, 6))
sns.scatterplot(x='sales', y='profit', data=or_prod, hue='category', size='quantity', sizes=(20, 200), alpha=0.75, palette='magma_r')
plt.xlabel('Total Sales')
plt.ylabel('Total Profit')
plt.legend(title='Product ', loc='upper right')
plt.show()
