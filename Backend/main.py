from fastapi import FastAPI
from sqlalchemy import text
from database import engine
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans


app = FastAPI(
    title="Credit Card Customer Segmentation API",
    description="Backend API for K-Means customer segmentation",
    version="1.0"
)
app.mount(
    "/static",
    StaticFiles(directory="../Frontend"),
    name="static"
)

@app.get("/")
def home():
    return FileResponse("../Frontend/index.html")


@app.get("/customers")
def get_customers():

    query = text("""
        SELECT *
        FROM customers
        LIMIT 100
    """)

    with engine.connect() as connection:
        result = connection.execute(query)

        customers = [
            dict(row._mapping)
            for row in result
        ]

    return customers


@app.get("/clusters")
def get_clusters():

    query = text("""
        SELECT
            cluster,
            segment,
            COUNT(*) AS total_customers
        FROM customers
        GROUP BY cluster, segment
        ORDER BY cluster
    """)

    with engine.connect() as connection:
        result = connection.execute(query)

        clusters = [
            dict(row._mapping)
            for row in result
        ]

    return clusters

@app.get("/customers/{customer_key}")
def get_customer(customer_key: int):

    query = text("""
        SELECT
            customer_key,
            avg_credit_limit,
            total_credit_cards,
            total_visits_bank,
            total_visits_online,
            total_calls_made
        FROM customers
        WHERE customer_key = :customer_key
    """)

    all_data_query = text("""
        SELECT
            avg_credit_limit,
            total_credit_cards,
            total_visits_bank,
            total_visits_online,
            total_calls_made
        FROM customers
    """)

    with engine.connect() as connection:

        customer_result = connection.execute(
            query,
            {"customer_key": customer_key}
        )

        customer = customer_result.fetchone()

        if customer is None:
            return {
                "message": "Customer not found"
            }

        all_result = connection.execute(all_data_query)

        data = [
            dict(row._mapping)
            for row in all_result
        ]

    df = pd.DataFrame(data)

    features = [
        "avg_credit_limit",
        "total_credit_cards",
        "total_visits_bank",
        "total_visits_online",
        "total_calls_made"
    ]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df[features])

    kmeans = KMeans(
        n_clusters=3,
        random_state=42,
        n_init=20
    )

    kmeans.fit(X_scaled)

    customer_data = [[
        customer.avg_credit_limit,
        customer.total_credit_cards,
        customer.total_visits_bank,
        customer.total_visits_online,
        customer.total_calls_made
    ]]

    customer_scaled = scaler.transform(customer_data)

    cluster = int(
        kmeans.predict(customer_scaled)[0]
    )

    segment_names = {
        0: "Moderate-Value Customers",
        1: "Lower-Value Customers",
        2: "High-Value Customers"
    }

    result = dict(customer._mapping)

    result["cluster"] = cluster
    result["segment"] = segment_names[cluster]

    return result

@app.get("/stats")
def get_stats():

    query = text("""
        SELECT
            avg_credit_limit,
            total_credit_cards,
            total_visits_bank,
            total_visits_online,
            total_calls_made
        FROM customers
    """)

    with engine.connect() as connection:
        result = connection.execute(query)

        data = [
            dict(row._mapping)
            for row in result
        ]

    df = pd.DataFrame(data)

    features = [
        "avg_credit_limit",
        "total_credit_cards",
        "total_visits_bank",
        "total_visits_online",
        "total_calls_made"
    ]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df[features])

    kmeans = KMeans(
        n_clusters=3,
        random_state=42,
        n_init=20
    )

    clusters = kmeans.fit_predict(X_scaled)

    df["cluster"] = clusters

    segment_names = {
        0: "Moderate-Value Customers",
        1: "Lower-Value Customers",
        2: "High-Value Customers"
    }

    df["segment"] = df["cluster"].map(segment_names)

    cluster_counts = (
        df.groupby(["cluster", "segment"])
        .size()
        .reset_index(name="total_customers")
    )

    return {
        "total_customers": len(df),
        "average_credit_limit": round(
            float(df["avg_credit_limit"].mean()), 2
        ),
        "clusters": cluster_counts.to_dict(orient="records")
    }
@app.get("/predict")
def predict_segment(
    avg_credit_limit: float,
    total_credit_cards: int,
    total_visits_bank: int,
    total_visits_online: int,
    total_calls_made: int
):

    query = text("""
        SELECT
            avg_credit_limit,
            total_credit_cards,
            total_visits_bank,
            total_visits_online,
            total_calls_made
        FROM customers
    """)

    with engine.connect() as connection:
        result = connection.execute(query)

        data = [
            dict(row._mapping)
            for row in result
        ]

    df = pd.DataFrame(data)

    features = [
        "avg_credit_limit",
        "total_credit_cards",
        "total_visits_bank",
        "total_visits_online",
        "total_calls_made"
    ]

    scaler = StandardScaler()

    X_scaled = scaler.fit_transform(df[features])

    kmeans = KMeans(
        n_clusters=3,
        random_state=42,
        n_init=20
    )

    kmeans.fit(X_scaled)

    new_customer = [[
        avg_credit_limit,
        total_credit_cards,
        total_visits_bank,
        total_visits_online,
        total_calls_made
    ]]

    new_customer_scaled = scaler.transform(new_customer)

    cluster = int(
        kmeans.predict(new_customer_scaled)[0]
    )

    segment_names = {
        0: "Moderate-Value Customers",
        1: "Lower-Value Customers",
        2: "High-Value Customers"
    }

    return {
        "cluster": cluster,
        "segment": segment_names[cluster]
    }