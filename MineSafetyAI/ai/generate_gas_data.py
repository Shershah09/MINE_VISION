import numpy as np
import pandas as pd
from pathlib import Path


# ============================================================
# SETTINGS
# ============================================================

SEED = 42

NUM_LOCATIONS = 20
READINGS_PER_LOCATION = 500

INTERVAL_SECONDS = 5

np.random.seed(SEED)


# ============================================================
# SIMULATED MINE LOCATIONS
# ============================================================

LOCATION_TYPES = [
    "main_tunnel",
    "ventilation_area",
    "coal_face",
    "narrow_tunnel",
    "equipment_zone",
    "storage_area",
    "transport_tunnel",
    "junction",
    "maintenance_area",
    "return_airway"
]


# ============================================================
# SCENARIOS
# ============================================================

SCENARIOS = [
    "normal",
    "methane_buildup",
    "co_buildup",
    "low_oxygen",
    "co2_buildup",
    "ventilation_failure",
    "fire_heat",
    "combined_hazard"
]


# ============================================================
# LOCATION BASELINES
# ============================================================

def create_location_profile():

    profile = {

        "CH4": np.random.uniform(0.08, 0.20),

        "CO": np.random.uniform(3, 8),

        "CO2": np.random.uniform(0.04, 0.10),

        "O2": np.random.uniform(20.4, 20.8),

        "temperature": np.random.uniform(25, 29),

        "humidity": np.random.uniform(65, 78)
    }

    return profile


# ============================================================
# SCENARIO TARGET
# ============================================================

def get_scenario_target(scenario, baseline):

    target = baseline.copy()

    if scenario == "normal":

        target["CH4"] = np.random.uniform(0.15, 0.35)
        target["CO"] = np.random.uniform(5, 12)
        target["CO2"] = np.random.uniform(0.05, 0.15)
        target["O2"] = np.random.uniform(20.2, 20.8)

        target["temperature"] = np.random.uniform(26, 30)
        target["humidity"] = np.random.uniform(65, 80)

    elif scenario == "methane_buildup":

        target["CH4"] = np.random.uniform(0.70, 1.10)
        target["CO"] = np.random.uniform(8, 20)
        target["CO2"] = np.random.uniform(0.10, 0.25)
        target["O2"] = np.random.uniform(19.8, 20.4)

        target["temperature"] = np.random.uniform(27, 31)
        target["humidity"] = np.random.uniform(70, 85)

    elif scenario == "co_buildup":

        target["CH4"] = np.random.uniform(0.25, 0.60)
        target["CO"] = np.random.uniform(30, 70)
        target["CO2"] = np.random.uniform(0.10, 0.30)
        target["O2"] = np.random.uniform(19.5, 20.5)

        target["temperature"] = np.random.uniform(28, 34)
        target["humidity"] = np.random.uniform(70, 88)

    elif scenario == "low_oxygen":

        target["CH4"] = np.random.uniform(0.30, 0.70)
        target["CO"] = np.random.uniform(10, 30)
        target["CO2"] = np.random.uniform(0.20, 0.45)
        target["O2"] = np.random.uniform(18.2, 19.4)

        target["temperature"] = np.random.uniform(28, 33)
        target["humidity"] = np.random.uniform(75, 90)

    elif scenario == "co2_buildup":

        target["CH4"] = np.random.uniform(0.20, 0.60)
        target["CO"] = np.random.uniform(8, 25)
        target["CO2"] = np.random.uniform(0.30, 0.60)
        target["O2"] = np.random.uniform(19.0, 20.2)

        target["temperature"] = np.random.uniform(27, 32)
        target["humidity"] = np.random.uniform(75, 90)

    elif scenario == "ventilation_failure":

        target["CH4"] = np.random.uniform(0.70, 1.20)
        target["CO"] = np.random.uniform(25, 60)
        target["CO2"] = np.random.uniform(0.30, 0.65)
        target["O2"] = np.random.uniform(18.5, 19.5)

        target["temperature"] = np.random.uniform(30, 35)
        target["humidity"] = np.random.uniform(80, 94)

    elif scenario == "fire_heat":

        target["CH4"] = np.random.uniform(0.30, 0.90)
        target["CO"] = np.random.uniform(40, 90)
        target["CO2"] = np.random.uniform(0.20, 0.50)
        target["O2"] = np.random.uniform(18.8, 19.8)

        target["temperature"] = np.random.uniform(35, 45)
        target["humidity"] = np.random.uniform(70, 90)

    elif scenario == "combined_hazard":

        target["CH4"] = np.random.uniform(0.90, 1.30)
        target["CO"] = np.random.uniform(50, 100)
        target["CO2"] = np.random.uniform(0.40, 0.75)
        target["O2"] = np.random.uniform(17.8, 19.0)

        target["temperature"] = np.random.uniform(35, 45)
        target["humidity"] = np.random.uniform(82, 96)

    return target


# ============================================================
# SMOOTH TRANSITION
# ============================================================

def generate_transition(start, end, steps):

    values = np.linspace(start, end, steps)

    noise = np.random.normal(
        0,
        abs(end - start) * 0.015 + 0.001,
        steps
    )

    return values + noise


# ============================================================
# RISK LABEL
# ============================================================

def calculate_risk(
    ch4,
    co,
    co2,
    o2,
    temperature
):

    score = 0

    # Synthetic development rules
    # These are NOT official mine safety limits.

    if ch4 >= 0.75:
        score += 2
    elif ch4 >= 0.50:
        score += 1

    if co >= 50:
        score += 3
    elif co >= 25:
        score += 2
    elif co >= 10:
        score += 1

    if co2 >= 0.50:
        score += 3
    elif co2 >= 0.30:
        score += 2
    elif co2 >= 0.15:
        score += 1

    if o2 < 19:
        score += 3
    elif o2 < 19.5:
        score += 2
    elif o2 < 20:
        score += 1

    if temperature >= 40:
        score += 3
    elif temperature >= 35:
        score += 2
    elif temperature >= 32:
        score += 1

    if score >= 8:
        return "CRITICAL"

    elif score >= 5:
        return "DANGER"

    elif score >= 2:
        return "WARNING"

    else:
        return "SAFE"


# ============================================================
# GENERATE LOCATION DATA
# ============================================================

def generate_location_data(location_id, location_type):

    rows = []

    profile = create_location_profile()

    current = profile.copy()

    start_time = pd.Timestamp("2026-01-01 08:00:00")

    segment_size = READINGS_PER_LOCATION // len(SCENARIOS)

    for scenario_index, scenario in enumerate(SCENARIOS):

        start = scenario_index * segment_size

        if scenario_index == len(SCENARIOS) - 1:
            end = READINGS_PER_LOCATION
        else:
            end = (scenario_index + 1) * segment_size

        steps = end - start

        target = get_scenario_target(
            scenario,
            current
        )

        ch4_values = generate_transition(
            current["CH4"],
            target["CH4"],
            steps
        )

        co_values = generate_transition(
            current["CO"],
            target["CO"],
            steps
        )

        co2_values = generate_transition(
            current["CO2"],
            target["CO2"],
            steps
        )

        o2_values = generate_transition(
            current["O2"],
            target["O2"],
            steps
        )

        temperature_values = generate_transition(
            current["temperature"],
            target["temperature"],
            steps
        )

        humidity_values = generate_transition(
            current["humidity"],
            target["humidity"],
            steps
        )

        for i in range(steps):

            timestamp = (
                start_time
                + pd.Timedelta(
                    seconds=(start + i) * INTERVAL_SECONDS
                )
            )

            ch4 = max(ch4_values[i], 0)

            co = max(co_values[i], 0)

            co2 = max(co2_values[i], 0)

            o2 = max(o2_values[i], 0)

            temperature = temperature_values[i]

            humidity = np.clip(
                humidity_values[i],
                0,
                100
            )

            risk = calculate_risk(
                ch4,
                co,
                co2,
                o2,
                temperature
            )

            rows.append({

                "timestamp": timestamp,

                "location_id": location_id,

                "location_type": location_type,

                "CH4": round(ch4, 4),

                "CO": round(co, 2),

                "CO2": round(co2, 4),

                "O2": round(o2, 3),

                "temperature": round(
                    temperature,
                    2
                ),

                "humidity": round(
                    humidity,
                    2
                ),

                "risk_level": risk,

                "scenario": scenario
            })

        # IMPORTANT:
        # Next scenario starts from the previous
        # scenario's final condition.

        current = target.copy()

    return rows


# ============================================================
# GENERATE COMPLETE DATASET
# ============================================================

all_rows = []

for number in range(
    1,
    NUM_LOCATIONS + 1
):

    location_id = f"L{number:02d}"

    location_type = LOCATION_TYPES[
        (number - 1) % len(LOCATION_TYPES)
    ]

    print(
        f"Generating {location_id} - "
        f"{location_type}"
    )

    rows = generate_location_data(
        location_id,
        location_type
    )

    all_rows.extend(rows)


# ============================================================
# CREATE DATAFRAME
# ============================================================

df = pd.DataFrame(all_rows)

df = df.sort_values(
    [
        "location_id",
        "timestamp"
    ]
).reset_index(drop=True)


# ============================================================
# SAVE
# ============================================================

output_path = Path(
    "data/synthetic/gas/"
    "synthetic_gas_data_v2.csv"
)

df.to_csv(
    output_path,
    index=False
)


# ============================================================
# SUMMARY
# ============================================================

print("\n========================================")
print("Synthetic Gas Dataset V2")
print("========================================")

print(f"Rows       : {len(df)}")

print(
    f"Locations  : "
    f"{df['location_id'].nunique()}"
)

print(
    f"Columns    : "
    f"{len(df.columns)}"
)

print("\nLocation types:")

print(
    df[
        [
            "location_id",
            "location_type"
        ]
    ]
    .drop_duplicates()
    .to_string(index=False)
)

print("\nRisk distribution:")

print(
    df["risk_level"]
    .value_counts()
)

print("\nMissing values:")

print(
    df.isnull().sum()
)

print("\nSaved to:")

print(output_path)