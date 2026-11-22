
const API_URL = "/api";

// HTML elements
const stationCount = document.getElementById("station-count");
const measurementCount = document.getElementById("measurement-count");
const averageNoise = document.getElementById("average-noise");
const maximumNoise = document.getElementById("maximum-noise");

const measurementsTable = document.getElementById("measurements-table");
const resultsMessage = document.getElementById("results-message");

const apiStatus = document.getElementById("api-status-text");
let noiseChart = null;
// Retrieve measurements from FastAPI
async function getMeasurements(filters = {}) {

    try {
        const params = new URLSearchParams();

        // Add filters to the URL only when provided
        for (const [key, value] of Object.entries(filters)) {
            if (value !== "") {
                params.append(key, value);
            }
        }

        const queryString = params.toString();

        const url = queryString
            ? `${API_URL}/measurements?${queryString}`
            : `${API_URL}/measurements`;

        const response = await fetch(url);

        if (!response.ok) {
            throw new Error(`HTTP error: ${response.status}`);
        }

        const measurements = await response.json();

        // Update dashboard
        displayMeasurements(measurements);

        apiStatus.textContent = "API Connected";

    } catch (error) {

        console.error("Error retrieving measurements:", error);

        apiStatus.textContent = "API Disconnected";
        resultsMessage.textContent = "Could not load measurements.";
        measurementsTable.innerHTML = "";
    }
}




let stationNames = {};
let aircraftNames = {};

// Display measurements and calculate statistics
function displayMeasurements(measurements) {
    updateNoiseChart(measurements);
    // Total measurements
    measurementCount.textContent = measurements.length;

    // Average and maximum noise
    if (measurements.length > 0) {

        const noiseLevels = measurements.map(
            measurement => measurement.noise_level_db
        );

        const average = noiseLevels.reduce(
            (sum, level) => sum + level, 0
        ) / noiseLevels.length;

        const maximum = Math.max(...noiseLevels);

        averageNoise.textContent = `${average.toFixed(2)} dB`;
        maximumNoise.textContent = `${maximum.toFixed(2)} dB`;

    } else {

        averageNoise.textContent = "-- dB";
        maximumNoise.textContent = "-- dB";
    }

    // Clear previous table rows
    measurementsTable.innerHTML = "";

    resultsMessage.textContent =
        `${measurements.length} measurement(s) found`;

    // Create a table row for each measurement
    measurements.forEach(measurement => {

        const row = document.createElement("tr");

        const values = [
            measurement.id,
            stationNames[measurement.station_id] || `Station ${measurement.station_id}`,
            aircraftNames[measurement.aircraft_id] || `Aircraft ${measurement.aircraft_id}`,
            `${measurement.noise_level_db} dB`,
            new Date(measurement.timestamp).toLocaleString()
        ];

        values.forEach(value => {
            const cell = document.createElement("td");
            cell.textContent = value;
            row.appendChild(cell);
        });

        measurementsTable.appendChild(row);
    });
}


// Apply filters
document.getElementById("filter-button").addEventListener("click", () => {

    const filters = {
        station_id: document.getElementById("station-filter").value,
        aircraft_id: document.getElementById("aircraft-filter").value,
        min_noise_level: document.getElementById("min-noise-filter").value
    };

    getMeasurements(filters);
});


// Reset filters
document.getElementById("reset-button").addEventListener("click", () => {

    document.getElementById("station-filter").value = "";
    document.getElementById("aircraft-filter").value = "";
    document.getElementById("min-noise-filter").value = "";

    getMeasurements();
});





// --------------------------------------------------
// ADD MONITORING STATION
// --------------------------------------------------

document.getElementById("station-form").addEventListener("submit", async (event) => {
    event.preventDefault();

    const stationData = {
        name: document.getElementById("station-name").value,
        latitude: Number(document.getElementById("station-latitude").value),
        longitude: Number(document.getElementById("station-longitude").value)
    };

    const message = document.getElementById("station-message");

    try {
        const response = await fetch(`${API_URL}/stations`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(stationData)
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.detail || "Could not create station");
        }

        message.textContent = `Station "${result.name}" created successfully!`;
        message.style.color = "green";

        document.getElementById("station-form").reset();

        // Refresh station count
        getStations();
        // Refresh station dropdown in measurement form
        loadMeasurementOptions();

    } catch (error) {
        message.textContent = error.message;
        message.style.color = "red";
    }
});

// --------------------------------------------------
// ADD AIRCRAFT
// --------------------------------------------------

document.getElementById("aircraft-form").addEventListener("submit", async (event) => {
    event.preventDefault();

    const aircraftData = {
        flight_number: document.getElementById("flight-number").value,
        airline: document.getElementById("airline").value,
        aircraft_type: document.getElementById("aircraft-type").value,
        registration: document.getElementById("registration").value,
        origin: document.getElementById("origin").value,
        destination: document.getElementById("destination").value
    };

    const message = document.getElementById("aircraft-message");

    try {
        const response = await fetch(`${API_URL}/aircraft`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(aircraftData)
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.detail || "Could not register aircraft");
        }

        message.textContent = `Aircraft "${result.flight_number}" registered successfully!`;
        message.style.color = "green";

        document.getElementById("aircraft-form").reset();
        getAircraft();

        // Refresh aircraft dropdown in measurement form
        loadMeasurementOptions();

    } catch (error) {
        message.textContent = error.message;
        message.style.color = "red";
    }
});
// Retrieve monitoring stations
async function getStations() {
    try {
        const response = await fetch(`${API_URL}/stations`);

        if (!response.ok) {
            throw new Error("Could not retrieve stations");
        }

        const stations = await response.json();
        stationNames = {};

        stations.forEach(station => {
            stationNames[station.id] = station.name;
        });

        // Update dashboard counter
        stationCount.textContent = stations.length;

        // Populate stations table
        const stationsTable = document.getElementById("stations-table");
        stationsTable.innerHTML = "";

        stations.forEach(station => {
            const row = document.createElement("tr");

            const values = [
                station.id,
                station.name,
                station.latitude,
                station.longitude
            ];

            values.forEach(value => {
                const cell = document.createElement("td");
                cell.textContent = value;
                row.appendChild(cell);
            });

            stationsTable.appendChild(row);
        });

    } catch (error) {
        console.error("Error retrieving stations:", error);
        stationCount.textContent = "--";
    }
}

// --------------------------------------------------
// RETRIEVE AND DISPLAY AIRCRAFT
// --------------------------------------------------

async function getAircraft() {
    try {
        const response = await fetch(`${API_URL}/aircraft`);

        if (!response.ok) {
            throw new Error("Could not retrieve aircraft");
        }

        const aircraft = await response.json();
        aircraftNames = {};

        aircraft.forEach(item => {
            aircraftNames[item.id] = item.flight_number;
        });
        const aircraftTable = document.getElementById("aircraft-table");
        aircraftTable.innerHTML = "";

        aircraft.forEach(item => {
            const row = document.createElement("tr");

            const values = [
                item.id,
                item.flight_number,
                item.airline,
                item.aircraft_type,
                item.registration,
                item.origin,
                item.destination
            ];

            values.forEach(value => {
                const cell = document.createElement("td");
                cell.textContent = value;
                row.appendChild(cell);
            });

            aircraftTable.appendChild(row);
        });

    } catch (error) {
        console.error("Error retrieving aircraft:", error);
    }
}
// --------------------------------------------------
// MEASUREMENT FORM
// --------------------------------------------------

// Set current local date and time as the default
function setCurrentDateTime() {
    const now = new Date();

    const localDateTime =
        now.getFullYear() + "-" +
        String(now.getMonth() + 1).padStart(2, "0") + "-" +
        String(now.getDate()).padStart(2, "0") + "T" +
        String(now.getHours()).padStart(2, "0") + ":" +
        String(now.getMinutes()).padStart(2, "0");

    document.getElementById("measurement-timestamp").value =
        localDateTime;
}


// Load stations and aircraft into the dropdowns
async function loadMeasurementOptions() {
    try {
        const [stationResponse, aircraftResponse] = await Promise.all([
            fetch(`${API_URL}/stations`),
            fetch(`${API_URL}/aircraft`)
        ]);

        if (!stationResponse.ok || !aircraftResponse.ok) {
            throw new Error("Could not load stations or aircraft");
        }

        const stations = await stationResponse.json();
        const aircraft = await aircraftResponse.json();

        const stationSelect =
            document.getElementById("measurement-station");

        const aircraftSelect =
            document.getElementById("measurement-aircraft");

        stationSelect.innerHTML =
            '<option value="">Select a station</option>';

        aircraftSelect.innerHTML =
            '<option value="">Select an aircraft</option>';

        stations.forEach(station => {
            const option = document.createElement("option");

            option.value = station.id;
            option.textContent = `${station.name} (ID: ${station.id})`;

            stationSelect.appendChild(option);
        });

        aircraft.forEach(item => {
            const option = document.createElement("option");

            option.value = item.id;
            option.textContent =
                `${item.flight_number} - ${item.airline}`;

            aircraftSelect.appendChild(option);
        });

    } catch (error) {
        console.error("Error loading measurement options:", error);
    }
}


// Submit a new measurement
document.getElementById("measurement-form")
    .addEventListener("submit", async (event) => {

        event.preventDefault();

        const message =
            document.getElementById("measurement-message");

        const timestampInput =
            document.getElementById("measurement-timestamp").value;

        const measurementData = {
            station_id: Number(
                document.getElementById("measurement-station").value
            ),
            aircraft_id: Number(
                document.getElementById("measurement-aircraft").value
            ),
            noise_level_db: Number(
                document.getElementById("noise-level").value
            ),
            timestamp: new Date(timestampInput).toISOString()
        };

        try {
            const response = await fetch(`${API_URL}/measurements`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(measurementData)
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(
                    result.detail || "Could not save measurement"
                );
            }

            message.textContent =
                `Measurement #${result.id} saved successfully!`;

            message.style.color = "green";

            document.getElementById("measurement-form").reset();

            setCurrentDateTime();

            getMeasurements();

        } catch (error) {
            message.textContent = error.message;
            message.style.color = "red";
        }
    });


function updateNoiseChart(measurements) {

    const canvas = document.getElementById("noise-chart");

    // Group measurements by station
    const stationGroups = {};

    measurements.forEach(measurement => {
        const stationId = measurement.station_id;

        if (!stationGroups[stationId]) {
            stationGroups[stationId] = [];
        }

        stationGroups[stationId].push(measurement);
    });

    // Get all unique timestamps and sort them chronologically
    const timestamps = [
        ...new Set(
            measurements.map(m => new Date(m.timestamp).getTime())
        )
    ].sort((a, b) => a - b);

    // Convert timestamps into readable labels
    const labels = timestamps.map(timestamp =>
        new Date(timestamp).toLocaleString()
    );

    const colors = [
        "rgb(54, 162, 235)",
        "rgb(255, 99, 132)",
        "rgb(75, 192, 192)",
        "rgb(255, 159, 64)",
        "rgb(153, 102, 255)"
    ];

    // Create one dataset per station
    const datasets = Object.entries(stationGroups).map(
        ([stationId, stationMeasurements], index) => {

            const valuesByTimestamp = new Map();

            stationMeasurements.forEach(measurement => {
                const timestamp = new Date(
                    measurement.timestamp
                ).getTime();

                valuesByTimestamp.set(
                    timestamp,
                    measurement.noise_level_db
                );
            });

            return {
                label: stationNames[stationId] || `Station ${stationId}`,
                data: timestamps.map(timestamp =>
                    valuesByTimestamp.get(timestamp) ?? null
                ),
                borderColor: colors[index % colors.length],
                backgroundColor: colors[index % colors.length],
                borderWidth: 2,
                tension: 0.3,
                spanGaps: true
            };
        }
    );

    if (noiseChart) {
        noiseChart.destroy();
    }

    noiseChart = new Chart(canvas, {
        type: "line",
        data: {
            labels: labels,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    title: {
                        display: true,
                        text: "Measurement Time"
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: "Noise Level (dB)"
                    },
                    beginAtZero: true
                }
            }
        }
    });
}


// Initialize measurement form
setCurrentDateTime();
loadMeasurementOptions();
// Initial dashboard loading
getStations();
getAircraft();
getMeasurements();