// Load dashboard statistics
async function loadStats() {

    try {

        const response = await fetch("/stats");
        const data = await response.json();

        document.getElementById("totalCustomers").textContent =
            data.total_customers;

        document.getElementById("averageCredit").textContent =
            "₹" + Number(data.average_credit_limit).toLocaleString();

        const clustersContainer =
            document.getElementById("clusters");

        clustersContainer.innerHTML = "";

        data.clusters.forEach(cluster => {

            const div = document.createElement("div");

            div.className = "cluster";

            div.innerHTML = `
                <h3>${cluster.segment}</h3>
                <p>${cluster.total_customers}</p>
                <small>Cluster ${cluster.cluster}</small>
            `;

            clustersContainer.appendChild(div);
        });
        const labels = data.clusters.map(
    cluster => cluster.segment
);

const values = data.clusters.map(
    cluster => cluster.total_customers
);

new Chart(
    document.getElementById("clusterChart"),
    {
        type: "bar",

        data: {
            labels: labels,

            datasets: [
                {
                    label: "Number of Customers",
                    data: values
                }
            ]
        },

        options: {
            responsive: true,

            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    }
);

    } catch (error) {

        console.error("Error loading statistics:", error);

    }
}


// Search customer
async function searchCustomer() {

    const customerKey =
        document.getElementById("customerKey").value;

    const result =
        document.getElementById("customerResult");

    if (!customerKey) {

        result.innerHTML =
            "<p>Please enter a customer key.</p>";

        return;
    }

    try {

        const response =
            await fetch(`/customers/${customerKey}`);

        const data = await response.json();

        if (data.message) {

            result.innerHTML =
                `<p>${data.message}</p>`;

            return;
        }

        result.innerHTML = `
            <div class="customer-card">

                <h3>Customer ${data.customer_key}</h3>

                <p>
                    <strong>Average Credit Limit:</strong>
                    ₹${Number(data.avg_credit_limit).toLocaleString()}
                </p>

                <p>
                    <strong>Total Credit Cards:</strong>
                    ${data.total_credit_cards}
                </p>

                <p>
                    <strong>Bank Visits:</strong>
                    ${data.total_visits_bank}
                </p>

                <p>
                    <strong>Online Visits:</strong>
                    ${data.total_visits_online}
                </p>

                <p>
                    <strong>Calls Made:</strong>
                    ${data.total_calls_made}
                </p>

                <p>
                    <strong>Cluster:</strong>
                    ${data.cluster}
                </p>

                <p>
                    <strong>Segment:</strong>
                    ${data.segment}
                </p>

            </div>
        `;

    } catch (error) {

        result.innerHTML =
            "<p>Unable to connect to the server.</p>";

        console.error(error);
    }
}


// Load data when page opens
loadStats();
async function loadCustomers() {

    try {

        const response = await fetch("/customers");

        const customers = await response.json();

        const table =
            document.getElementById("customerTable");

        table.innerHTML = "";

        customers.forEach(customer => {

            const row = document.createElement("tr");

            row.innerHTML = `
                <td>${customer.customer_key}</td>

                <td>
                    ₹${Number(
                        customer.avg_credit_limit
                    ).toLocaleString()}
                </td>

                <td>${customer.total_credit_cards}</td>

                <td>${customer.total_visits_bank}</td>

                <td>${customer.total_visits_online}</td>

                <td>${customer.total_calls_made}</td>

                <td>${customer.cluster}</td>

                <td>${customer.segment}</td>
            `;

            table.appendChild(row);

        });

    } catch (error) {

        console.error(
            "Error loading customers:",
            error
        );

    }
}

loadCustomers();
async function predictSegment() {

    const creditLimit =
        document.getElementById("creditLimit").value;

    const creditCards =
        document.getElementById("creditCards").value;

    const bankVisits =
        document.getElementById("bankVisits").value;

    const onlineVisits =
        document.getElementById("onlineVisits").value;

    const callsMade =
        document.getElementById("callsMade").value;

    const result =
        document.getElementById("predictionResult");

    if (
        !creditLimit ||
        !creditCards ||
        !bankVisits ||
        !onlineVisits ||
        !callsMade
    ) {
        result.innerHTML =
            "<p>Please fill all fields.</p>";
        return;
    }

    try {

        const url =
            `https://credit-card-customer-segmentation-production.up.railway.app/predict?` +
            `avg_credit_limit=${encodeURIComponent(creditLimit)}` +
            `&total_credit_cards=${encodeURIComponent(creditCards)}` +
            `&total_visits_bank=${encodeURIComponent(bankVisits)}` +
            `&total_visits_online=${encodeURIComponent(onlineVisits)}` +
            `&total_calls_made=${encodeURIComponent(callsMade)}`;

        console.log("Prediction URL:", url);

        const response = await fetch(url);

        console.log("Response status:", response.status);

        if (!response.ok) {
            throw new Error(
                `Prediction request failed: ${response.status}`
            );
        }

        const data = await response.json();
        console.log("ACTUAL PREDICTION RESPONSE:", data);

        console.log("Prediction response:", data);

        result.innerHTML = `
            <div class="customer-card">

                <h3>Prediction Result</h3>

                <p>
                    <strong>Cluster:</strong>
                    ${data.cluster}
                </p>

                <p>
                    <strong>Predicted Segment:</strong>
                    ${data.segment}
                </p>

            </div>
        `;

    } catch (error) {

        console.error("Prediction error:", error);

        result.innerHTML =
            "<p>Unable to get prediction from the server.</p>";
    }
}
async function loadSegmentChart() {
    try {
        const response = await fetch("/stats");
        const data = await response.json();

        const ctx = document.getElementById("segmentChart");

        new Chart(ctx, {
            type: "doughnut",
            data: {
                labels: [
                    "Moderate-Value Customers",
                    "Lower-Value Customers",
                    "High-Value Customers"
                ],
                datasets: [{
                    data: [
                        data["Moderate-Value Customers"],
                        data["Lower-Value Customers"],
                        data["High-Value Customers"]
                    ]
                }]
            },
            options: {
                responsive: true
            }
        });

    } catch (error) {
        console.error("Unable to load chart:", error);
    }
}

loadSegmentChart();