import pandas as pd

# load the data
df = pd.read_csv("Chocolate Sales.csv")

# Clean the date column
df["Date"] = pd.to_datetime(df["Date"], format="%d-%b-%y")

# Clean amount column
df["Amount"] = (
    df["Amount"]
        .str.replace(r"[\$,]","",regex=True)
        .astype(float)
)

# Extract year and month
df["Year"] = df["Date"].dt.year
df["Month"] = df["Date"].dt.month

# QA
print(df.dtypes)
print(df.head())