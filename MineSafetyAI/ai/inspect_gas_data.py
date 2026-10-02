import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# LOAD DATA
# ============================================================

file_path = "data/synthetic/gas/synthetic_gas_data.csv"

df = pd.read_csv(file_path)

print("Dataset shape:", df.shape)

print("\nRisk distribution:")
print(df["risk_level"].value_counts())


# ============================================================
# 1. RISK DISTRIBUTION
# ============================================================

df["risk_level"].value_counts().reindex(
    ["SAFE", "WARNING", "DANGER", "CRITICAL"]
).plot(kind="bar")

plt.title("Risk Level Distribution")
plt.xlabel("Risk Level")
plt.ylabel("Number of Readings")
plt.tight_layout()
plt.show()


# ============================================================
# 2. SENSOR DISTRIBUTIONS
# ============================================================

sensor_columns = [
    "CH4",
    "CO",
    "CO2",
    "O2",
    "temperature",
    "humidity"
]

df[sensor_columns].hist(figsize=(12, 8))

plt.suptitle("Sensor Value Distributions")
plt.tight_layout()
plt.show()


# ============================================================
# 3. SENSOR VALUES BY RISK LEVEL
# ============================================================

risk_order = [
    "SAFE",
    "WARNING",
    "DANGER",
    "CRITICAL"
]

for column in sensor_columns:

    df.boxplot(
        column=column,
        by="risk_level",
        grid=False
    )

    plt.title(f"{column} vs Risk Level")
    plt.suptitle("")
    plt.xlabel("Risk Level")
    plt.ylabel(column)
    plt.show()


# ============================================================
# 4. CORRELATION MATRIX
# ============================================================

correlation = df[sensor_columns].corr()

print("\nCorrelation matrix:")
print(correlation.round(2))

plt.figure(figsize=(8, 6))

plt.imshow(
    correlation,
    cmap="viridis",
    aspect="auto"
)

plt.colorbar()

plt.xticks(
    range(len(sensor_columns)),
    sensor_columns,
    rotation=45
)

plt.yticks(
    range(len(sensor_columns)),
    sensor_columns
)

plt.title("Sensor Correlation Matrix")

plt.tight_layout()
plt.show()


# ============================================================
# 5. TIME SERIES EXAMPLE
# ============================================================

location = "L01"

location_data = df[
    df["location_id"] == location
].copy()

location_data["timestamp"] = pd.to_datetime(
    location_data["timestamp"]
)

plt.figure(figsize=(12, 5))

plt.plot(
    location_data["timestamp"],
    location_data["CH4"]
)

plt.title(f"CH4 Time Series - {location}")
plt.xlabel("Time")
plt.ylabel("CH4")

plt.xticks(rotation=45)

plt.tight_layout()
plt.show()


print("\nEDA completed successfully.")