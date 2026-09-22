import numpy as np
import pandas as pd

from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


# ============================================================
# UNISHIELD — AI SECURITY SIMULATION
# ============================================================

RANDOM_STATE = 42
np.random.seed(RANDOM_STATE)


# ------------------------------------------------------------
# 1. UNIVERSITY USERS
# ------------------------------------------------------------

USERS = [
    {
        "user_id": "STU001",
        "role": "Student",
        "normal_hour": 9,
        "normal_download": 150,
    },
    {
        "user_id": "STU002",
        "role": "Student",
        "normal_hour": 14,
        "normal_download": 200,
    },
    {
        "user_id": "STU003",
        "role": "Student",
        "normal_hour": 19,
        "normal_download": 250,
    },
    {
        "user_id": "STU004",
        "role": "Student",
        "normal_hour": 11,
        "normal_download": 180,
    },
    {
        "user_id": "STF001",
        "role": "Staff",
        "normal_hour": 10,
        "normal_download": 400,
    },
    {
        "user_id": "STF002",
        "role": "Staff",
        "normal_hour": 15,
        "normal_download": 350,
    },
]


# ------------------------------------------------------------
# 2. GENERATE NORMAL UNIVERSITY ACTIVITY
# ------------------------------------------------------------

def generate_normal_activity(records=1000):

    rows = []

    for _ in range(records):

        user = np.random.choice(USERS)

        hour = int(
            np.clip(
                np.random.normal(user["normal_hour"], 2),
                0,
                23
            )
        )

        failed_logins = np.random.poisson(0.3)

        session_duration = max(
            5,
            np.random.normal(45, 15)
        )

        resources_accessed = max(
            1,
            int(np.random.normal(8, 3))
        )

        sensitive_resources = np.random.binomial(
            resources_accessed,
            0.05
        )

        downloads = max(
            1,
            int(np.random.normal(
                user["normal_download"],
                user["normal_download"] * 0.25
            ))
        )

        device_changed = np.random.choice(
            [0, 1],
            p=[0.95, 0.05]
        )

        ip_changes = np.random.poisson(0.2)

        geo_distance = max(
            0,
            np.random.normal(10, 8)
        )

        concurrent_sessions = np.random.choice(
            [1, 2],
            p=[0.9, 0.1]
        )

        rows.append({

            "user_id": user["user_id"],
            "role": user["role"],

            "hour": hour,

            "failed_logins": failed_logins,

            "session_duration": round(
                session_duration,
                2
            ),

            "resources_accessed":
                resources_accessed,

            "sensitive_resources":
                sensitive_resources,

            "downloads_mb":
                downloads,

            "device_changed":
                device_changed,

            "ip_changes":
                ip_changes,

            "geo_distance_km":
                round(geo_distance, 2),

            "concurrent_sessions":
                concurrent_sessions,

            "attack_type": "NORMAL"
        })

    return pd.DataFrame(rows)


# ------------------------------------------------------------
# 3. ATTACK GENERATORS
# ------------------------------------------------------------

def generate_credential_attack(user):

    return {
        "user_id": user,
        "role": "Student",

        "hour": 3,

        "failed_logins": 14,

        "session_duration": 7,

        "resources_accessed": 5,

        "sensitive_resources": 3,

        "downloads_mb": 80,

        "device_changed": 1,

        "ip_changes": 5,

        "geo_distance_km": 4800,

        "concurrent_sessions": 1,

        "attack_type": "CREDENTIAL_COMPROMISE"
    }


def generate_data_exfiltration_attack(user):

    return {
        "user_id": user,
        "role": "Staff",

        "hour": 2,

        "failed_logins": 0,

        "session_duration": 180,

        "resources_accessed": 85,

        "sensitive_resources": 42,

        "downloads_mb": 8500,

        "device_changed": 0,

        "ip_changes": 1,

        "geo_distance_km": 15,

        "concurrent_sessions": 3,

        "attack_type": "DATA_EXFILTRATION"
    }


def generate_bot_attack(user):

    return {
        "user_id": user,
        "role": "Student",

        "hour": 4,

        "failed_logins": 2,

        "session_duration": 2,

        "resources_accessed": 300,

        "sensitive_resources": 12,

        "downloads_mb": 1200,

        "device_changed": 1,

        "ip_changes": 15,

        "geo_distance_km": 1000,

        "concurrent_sessions": 8,

        "attack_type": "AUTOMATED_BOT"
    }


# ------------------------------------------------------------
# 4. TRAIN ISOLATION FOREST
# ------------------------------------------------------------

FEATURES = [

    "hour",
    "failed_logins",
    "session_duration",
    "resources_accessed",
    "sensitive_resources",
    "downloads_mb",
    "device_changed",
    "ip_changes",
    "geo_distance_km",
    "concurrent_sessions"
]


def train_model(normal_data):

    X = normal_data[FEATURES]

    scaler = StandardScaler()

    X_scaled = scaler.fit_transform(X)

    model = IsolationForest(

        n_estimators=200,

        contamination=0.05,

        random_state=RANDOM_STATE
    )

    model.fit(X_scaled)

    return model, scaler


# ------------------------------------------------------------
# 5. EXPLANATION ENGINE
# ------------------------------------------------------------

def explain_event(row):

    reasons = []

    if row["failed_logins"] >= 5:
        reasons.append(
            "High number of failed login attempts"
        )

    if row["device_changed"] == 1:
        reasons.append(
            "Login from a new device"
        )

    if row["geo_distance_km"] > 500:
        reasons.append(
            "Unusual geographic location"
        )

    if row["ip_changes"] >= 5:
        reasons.append(
            "Rapid IP address changes"
        )

    if row["sensitive_resources"] >= 10:
        reasons.append(
            "Unusually high sensitive-resource access"
        )

    if row["downloads_mb"] > 2000:
        reasons.append(
            "Abnormally high data download volume"
        )

    if row["concurrent_sessions"] >= 4:
        reasons.append(
            "Multiple concurrent sessions detected"
        )

    if row["resources_accessed"] > 100:
        reasons.append(
            "Abnormally high resource access"
        )

    if row["hour"] <= 5:
        reasons.append(
            "Activity occurred during unusual hours"
        )

    return reasons


# ------------------------------------------------------------
# 6. RISK CALCULATION
# ------------------------------------------------------------

def calculate_risk(anomaly_score, reasons):

    # Isolation Forest gives higher values to normal behaviour.
    # Convert the model score into a rough 0–100 risk scale.

    risk = 50 - (anomaly_score * 100)

    # Additional evidence increases the risk score.

    risk += len(reasons) * 7

    risk = np.clip(
        risk,
        0,
        100
    )

    return round(float(risk), 2)


def risk_level(risk):

    if risk >= 75:
        return "CRITICAL"

    if risk >= 50:
        return "HIGH"

    if risk >= 25:
        return "MEDIUM"

    return "LOW"


# ------------------------------------------------------------
# 7. SECURITY RESPONSE
# ------------------------------------------------------------

def security_response(level):

    if level == "CRITICAL":

        return (
            "BLOCK SESSION + "
            "LOCK ACCOUNT + "
            "ALERT SECURITY TEAM"
        )

    if level == "HIGH":

        return (
            "CHALLENGE LOGIN + "
            "MONITOR SESSION + "
            "ALERT ADMIN"
        )

    if level == "MEDIUM":

        return (
            "INCREASE MONITORING"
        )

    return "ALLOW"


# ------------------------------------------------------------
# 8. ANALYZE EVENT
# ------------------------------------------------------------

def analyze_event(row, model, scaler):

    X = pd.DataFrame(
        [row],
        columns=FEATURES
    )

    X_scaled = scaler.transform(X)

    prediction = model.predict(X_scaled)[0]

    anomaly_score = model.decision_function(
        X_scaled
    )[0]

    reasons = explain_event(row)

    risk = calculate_risk(
        anomaly_score,
        reasons
    )

    level = risk_level(risk)

    response = security_response(level)

    return {

        "user_id":
            row["user_id"],

        "attack_type":
            row["attack_type"],

        "anomaly":
            "ANOMALY" if prediction == -1
            else "NORMAL",

        "anomaly_score":
            round(float(anomaly_score), 4),

        "risk_score":
            risk,

        "risk_level":
            level,

        "explanation":
            reasons,

        "response":
            response
    }


# ------------------------------------------------------------
# 9. MAIN SIMULATION
# ------------------------------------------------------------

def main():

    print("\n")
    print("=" * 65)
    print("                 UNISHIELD AI SIMULATION")
    print("=" * 65)

    print("\n[1] Generating normal university activity...")

    normal_data = generate_normal_activity(
        records=1500
    )

    print(
        f"    Generated {len(normal_data)} normal events."
    )

    print("\n[2] Training Isolation Forest...")

    model, scaler = train_model(
        normal_data
    )

    print("    Model trained successfully.")

    print("\n[3] Creating simulated attacks...")

    attacks = [

        generate_credential_attack(
            "STU001"
        ),

        generate_data_exfiltration_attack(
            "STF001"
        ),

        generate_bot_attack(
            "STU003"
        )

    ]

    print(
        f"    Injected {len(attacks)} attack scenarios."
    )

    print("\n[4] Running AI detection...")
    print("-" * 65)

    for attack in attacks:

        result = analyze_event(
            attack,
            model,
            scaler
        )

        print("\nUSER:", result["user_id"])

        print(
            "ATTACK:",
            result["attack_type"]
        )

        print(
            "AI CLASSIFICATION:",
            result["anomaly"]
        )

        print(
            "ANOMALY SCORE:",
            result["anomaly_score"]
        )

        print(
            "RISK SCORE:",
            result["risk_score"],
            "/ 100"
        )

        print(
            "RISK LEVEL:",
            result["risk_level"]
        )

        print("\nWHY?")

        for reason in result["explanation"]:

            print(
                "  •",
                reason
            )

        print("\nSECURITY RESPONSE:")

        print(
            "  →",
            result["response"]
        )

        print("-" * 65)


if __name__ == "__main__":
    main()