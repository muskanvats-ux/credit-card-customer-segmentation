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
        SELECT *
        FROM customers
        WHERE customer_key = :customer_key
    """)

    with engine.connect() as connection:
        result = connection.execute(
            query,
            {"customer_key": customer_key}
        )

        customer = result.fetchone()

    if customer is None:
        return {
            "message": "Customer not found"
        }

    return dict(customer._mapping)
@app.get("/stats")
def get_stats():

    query = text("""
        SELECT
            COUNT(*) AS total_customers,
            AVG(avg_credit_limit) AS average_credit_limit
        FROM customers
    """)

    cluster_query = text("""
        SELECT
            cluster,
            segment,
            COUNT(*) AS total_customers
        FROM customers
        GROUP BY cluster, segment
        ORDER BY cluster
    """)

    with engine.connect() as connection:

        stats_result = connection.execute(query).fetchone()

        cluster_result = connection.execute(cluster_query)

        clusters = [
            dict(row._mapping)
            for row in cluster_result
        ]

    return {
        "total_customers": stats_result.total_customers,
        "average_credit_limit": round(
            float(stats_result.average_credit_limit), 2
        ),
        "clusters": clusters
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