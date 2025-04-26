import pandas as pd

# Load & Clean data
df = pd.read_csv("Chocolate Sales.csv")
df["Date"] = pd.to_datetime(df["Date"], format="%d-%b-%y")
df["Amount"] = (
    df["Amount"].str.replace(r"[\$,]","",regex=True).astype(float)
)

# Create Key KPIs
total_revenue = df["Amount"].sum()
total_units = df["Boxes Shipped"].sum()
total_orders = len(df)
aov = total_revenue / total_orders
rpb = total_revenue / total_units

print(f"Total Revenue: ${total_revenue:,.2f}")
print(f"Total Boxes Sold: {total_units:,}")
print(f"Total Orders: {total_orders:,}")
print(f"Average Order Value: ${aov:,.2f}")
print(f"Revenue Per Box: ${rpb:,.2f}")

# Top 5 Products & Countries
country_revenue = df.groupby("Country")["Amount"].sum().sort_values(ascending=False)
product_revenue = df.groupby("Product")["Amount"].sum().sort_values(ascending=False)

print("\n", "Top 5 Products by Revenue:")
print(product_revenue.head(5),"\n")

print("Top 5 Countries by Revenue:")
print(country_revenue.head(5),"\n")

# Sales Leaderboard
sales_leaderboard = df.groupby("Sales Person")["Amount"].sum().sort_values(ascending=False)

print("Sales by Salesperson:")
print(sales_leaderboard.head(10), "\n")

# Monthly Trend
monthly = df.set_index("Date").resample("ME")["Amount"].sum()
mom_pct = monthly.pct_change().fillna(0) * 100

print("Monthly Revenue: ")
print(monthly.round(2), "\n")

print("Month-over-Month Growth (%):")
print(mom_pct.round(1).astype(str) + "%")