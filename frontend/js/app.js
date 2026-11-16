
const API_URL = "http://127.0.0.1:8000/api";

// HTML elements
const stationCount = document.getElementById("station-count");
const measurementCount = document.getElementById("measurement-count");
const averageNoise = document.getElementById("average-noise");
const maximumNoise = document.getElementById("maximum-noise");

const measurementsTable = document.getElementById("measurements-table");
const resultsMessage = document.getElementById("results-message");

const apiStatus = document.getElementById("api-status-text");

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


// Retrieve monitoring stations
async function getStations() {

    try {
        const response = await fetch(`${API_URL}/stations`);

        if (!response.ok) {
            throw new Error(`HTTP error: ${response.status}`);
        }

        const stations = await response.json();

        stationCount.textContent = stations.length;

    } catch (error) {
        console.error("Error retrieving stations:", error);
        stationCount.textContent = "--";
    }
}


// Display measurements and calculate statistics
function displayMeasurements(measurements) {

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
            measurement.station_id,
            measurement.aircraft_id,
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


// Initial dashboard loading
getStations();
getMeasurements();
