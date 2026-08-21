import pandas as pd
from sqlalchemy import text
from database import engine

from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans


# -----------------------------------
# 1. Read customer data from MySQL
# -----------------------------------

query = """
SELECT
    id,
    customer_key,
    avg_credit_limit,
    total_credit_cards,
    total_visits_bank,
    total_visits_online,
    total_calls_made
FROM customers
"""

df = pd.read_sql(query, engine)

print("Data loaded from MySQL!")
print("Number of customers:", len(df))


# -----------------------------------
# 2. Select features for K-Means
# -----------------------------------

features = [
    "avg_credit_limit",
    "total_credit_cards",
    "total_visits_bank",
    "total_visits_online",
    "total_calls_made"
]

X = df[features]


# -----------------------------------
# 3. Standardize the data
# -----------------------------------

scaler = StandardScaler()

X_scaled = scaler.fit_transform(X)


# -----------------------------------
# 4. Train K-Means
# -----------------------------------

kmeans = KMeans(
    n_clusters=3,
    random_state=42,
    n_init=20
)

df["cluster"] = kmeans.fit_predict(X_scaled)


# -----------------------------------
# 5. Create segment names
# -----------------------------------

segment_names = {
    0: "Moderate-Value Customers",
    1: "Lower-Value Customers",
    2: "High-Value Customers"
}

df["segment"] = df["cluster"].map(segment_names)


# -----------------------------------
# 6. Update MySQL
# -----------------------------------

with engine.begin() as connection:

    for _, row in df.iterrows():

        update_query = text("""
            UPDATE customers
            SET cluster = :cluster,
                segment = :segment
            WHERE id = :id
        """)

        connection.execute(
            update_query,
            {
                "cluster": int(row["cluster"]),
                "segment": row["segment"],
                "id": int(row["id"])
            }
        )


print("✅ K-Means completed!")
print("✅ Cluster results saved to MySQL!")

print("\nCluster distribution:")
print(df["cluster"].value_counts().sort_index())