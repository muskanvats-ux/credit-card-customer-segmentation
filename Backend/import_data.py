import pandas as pd
from database import engine

# Read the dataset
df = pd.read_csv("../Data/Credit Card Customer Data.csv")

print("Dataset loaded successfully!")
print("Number of rows:", len(df))
print("Columns:", df.columns.tolist())

# Rename columns to match MySQL table
df = df.rename(columns={
    "Sl_No": "sl_no",
    "Customer Key": "customer_key",
    "Avg_Credit_Limit": "avg_credit_limit",
    "Total_Credit_Cards": "total_credit_cards",
    "Total_visits_bank": "total_visits_bank",
    "Total_visits_online": "total_visits_online",
    "Total_calls_made": "total_calls_made"
})

# Keep only the columns that we want to store
df = df[
    [
        "sl_no",
        "customer_key",
        "avg_credit_limit",
        "total_credit_cards",
        "total_visits_bank",
        "total_visits_online",
        "total_calls_made"
    ]
]

# Insert the data into MySQL
df.to_sql(
    "customers",
    con=engine,
    if_exists="replace",
    index=False
)

print("✅ Dataset successfully imported into MySQL!")