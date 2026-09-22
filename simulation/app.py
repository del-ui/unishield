import time
import random
import pandas as pd
import streamlit as st

from unishield_ai import (
    generate_normal_activity,
    generate_credential_attack,
    generate_data_exfiltration_attack,
    generate_bot_attack,
    train_model,
    analyze_event
)


# ============================================================
# UNISHIELD — AI SECURITY OPERATIONS CENTER
# ============================================================

st.set_page_config(
    page_title="UniShield SOC",
    page_icon="🛡️",
    layout="wide"
)


# ============================================================
# SESSION STATE
# ============================================================

if "events" not in st.session_state:
    st.session_state.events = []

if "running" not in st.session_state:
    st.session_state.running = False

if "model" not in st.session_state:

    normal_data = generate_normal_activity(
        records=2000
    )

    model, scaler = train_model(
        normal_data
    )

    st.session_state.model = model
    st.session_state.scaler = scaler


# ============================================================
# EVENT PROCESSOR
# ============================================================

def run_event(event):

    result = analyze_event(
        event,
        st.session_state.model,
        st.session_state.scaler
    )

    result["timestamp"] = time.strftime(
        "%H:%M:%S"
    )

    # Store original behavioural values
    result["failed_logins"] = event["failed_logins"]
    result["downloads_mb"] = event["downloads_mb"]
    result["resources_accessed"] = event["resources_accessed"]
    result["sensitive_resources"] = event["sensitive_resources"]
    result["geo_distance_km"] = event["geo_distance_km"]
    result["device_changed"] = event["device_changed"]

    st.session_state.events.insert(
        0,
        result
    )

    st.session_state.events = (
        st.session_state.events[:100]
    )


# ============================================================
# LIVE EVENT GENERATOR
# ============================================================

def generate_live_event():

    probability = random.random()

    if probability < 0.85:

        event = generate_normal_activity(
            records=1
        ).iloc[0].to_dict()

    elif probability < 0.91:

        event = generate_credential_attack(
            random.choice(
                ["STU001", "STU002", "STU003"]
            )
        )

    elif probability < 0.96:

        event = generate_bot_attack(
            random.choice(
                ["STU001", "STU002", "STU003"]
            )
        )

    else:

        event = generate_data_exfiltration_attack(
            random.choice(
                ["STF001", "STF002"]
            )
        )

    run_event(event)


# ============================================================
# HEADER
# ============================================================

st.title("🛡️ UniShield")

st.caption(
    "AI-Powered University Cybersecurity "
    "Operations Center"
)


# ============================================================
# SYSTEM STATUS
# ============================================================

s1, s2, s3, s4 = st.columns(4)

with s1:

    if st.session_state.running:
        st.success("🟢 MONITORING ACTIVE")
    else:
        st.warning("⏸️ MONITORING PAUSED")

with s2:
    st.success("🧠 AI MODEL ONLINE")

with s3:
    st.success("🔐 RESPONSE ENGINE ONLINE")

with s4:
    st.success("📡 EVENT STREAM ONLINE")


# ============================================================
# TOP METRICS
# ============================================================

events = st.session_state.events

total_events = len(events)

anomalies = sum(
    1 for e in events
    if e["anomaly"] == "ANOMALY"
)

critical = sum(
    1 for e in events
    if e["risk_level"] == "CRITICAL"
)

high = sum(
    1 for e in events
    if e["risk_level"] == "HIGH"
)


st.divider()

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric(
        "Events Analyzed",
        total_events
    )

with c2:
    st.metric(
        "Anomalies Detected",
        anomalies
    )

with c3:
    st.metric(
        "High Risk",
        high
    )

with c4:
    st.metric(
        "Critical Threats",
        critical
    )


# ============================================================
# CONTROLS
# ============================================================

st.divider()

st.subheader("🎮 Simulation Controls")

c1, c2, c3 = st.columns(3)

with c1:

    if st.button(
        "▶️ START MONITORING",
        use_container_width=True
    ):

        st.session_state.running = True
        st.rerun()


with c2:

    if st.button(
        "⏸️ STOP",
        use_container_width=True
    ):

        st.session_state.running = False
        st.rerun()


with c3:

    if st.button(
        "🗑️ CLEAR",
        use_container_width=True
    ):

        st.session_state.events = []
        st.rerun()


# ============================================================
# ATTACK INJECTION
# ============================================================

st.subheader(
    "🎯 Simulate Security Event"
)

a1, a2, a3, a4 = st.columns(4)


with a1:

    if st.button(
        "Normal Activity",
        use_container_width=True
    ):

        event = generate_normal_activity(
            records=1
        ).iloc[0].to_dict()

        run_event(event)

        st.rerun()


with a2:

    if st.button(
        "🔑 Credential Attack",
        use_container_width=True
    ):

        run_event(
            generate_credential_attack(
                "STU001"
            )
        )

        st.rerun()


with a3:

    if st.button(
        "📤 Data Exfiltration",
        use_container_width=True
    ):

        run_event(
            generate_data_exfiltration_attack(
                "STF001"
            )
        )

        st.rerun()


with a4:

    if st.button(
        "🤖 Bot Attack",
        use_container_width=True
    ):

        run_event(
            generate_bot_attack(
                "STU003"
            )
        )

        st.rerun()


# ============================================================
# LATEST THREAT
# ============================================================

if events:

    latest = events[0]

    st.divider()

    st.subheader(
        "🚨 Current Security Assessment"
    )

    left, middle, right = st.columns(3)

    with left:

        st.metric(
            "User",
            latest["user_id"]
        )

    with middle:

        st.metric(
            "Risk Score",
            f'{latest["risk_score"]}/100'
        )

    with right:

        st.metric(
            "Threat Level",
            latest["risk_level"]
        )


    # --------------------------------------------------------
    # BEHAVIOUR METRICS
    # --------------------------------------------------------

    st.subheader(
        "📊 Observed Behaviour"
    )

    b1, b2, b3, b4, b5 = st.columns(5)

    with b1:
        st.metric(
            "Failed Logins",
            latest["failed_logins"]
        )

    with b2:
        st.metric(
            "Downloads",
            f'{latest["downloads_mb"]} MB'
        )

    with b3:
        st.metric(
            "Resources",
            latest["resources_accessed"]
        )

    with b4:
        st.metric(
            "Sensitive",
            latest["sensitive_resources"]
        )

    with b5:
        st.metric(
            "Location Change",
            "YES"
            if latest["geo_distance_km"] > 500
            else "NO"
        )


    # --------------------------------------------------------
    # AI EXPLANATION
    # --------------------------------------------------------

    st.subheader(
        "🧠 AI Explanation"
    )

    if latest["explanation"]:

        for reason in latest["explanation"]:

            st.write(
                "🔎",
                reason
            )

    else:

        st.success(
            "Behaviour is consistent with the "
            "learned baseline."
        )


    # --------------------------------------------------------
    # RESPONSE
    # --------------------------------------------------------

    st.subheader(
        "🔐 Security Response"
    )

    st.info(
        latest["response"]
    )


# ============================================================
# RISK TIMELINE
# ============================================================

if len(events) >= 2:

    st.divider()

    st.subheader(
        "📈 AI Risk Timeline"
    )

    timeline = list(
        reversed(events[:30])
    )

    chart_data = pd.DataFrame({

        "Risk Score": [
            event["risk_score"]
            for event in timeline
        ]

    })

    st.line_chart(
        chart_data,
        height=300
    )


# ============================================================
# BEHAVIOUR CHART
# ============================================================

if len(events) >= 2:

    st.subheader(
        "📊 Behaviour Analysis"
    )

    timeline = list(
        reversed(events[:30])
    )

    behaviour = pd.DataFrame({

        "Downloads (MB)": [
            event["downloads_mb"]
            for event in timeline
        ],

        "Resources": [
            event["resources_accessed"]
            for event in timeline
        ],

        "Sensitive Resources": [
            event["sensitive_resources"]
            for event in timeline
        ]

    })

    st.line_chart(
        behaviour,
        height=300
    )


# ============================================================
# LIVE SECURITY STREAM
# ============================================================

st.divider()

st.subheader(
    "📡 Live Security Event Stream"
)

if events:

    history = []

    for event in events[:30]:

        history.append({

            "Time":
                event["timestamp"],

            "User":
                event["user_id"],

            "Event":
                event["attack_type"],

            "AI":
                event["anomaly"],

            "Risk":
                event["risk_score"],

            "Level":
                event["risk_level"],

            "Response":
                event["response"]

        })

    st.dataframe(
        pd.DataFrame(history),
        use_container_width=True,
        hide_index=True
    )

else:

    st.info(
        "No security events yet."
    )


# ============================================================
# CONTINUOUS MODE
# ============================================================

if st.session_state.running:

    generate_live_event()

    time.sleep(1)

    st.rerun()
