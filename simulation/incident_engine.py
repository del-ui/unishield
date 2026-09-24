import time


class UserBehavior:

    def __init__(self, user_id):
        self.user_id = user_id

        self.events = []

        self.failed_logins = 0
        self.new_device = False
        self.unusual_location = False
        self.sensitive_access = 0
        self.download_mb = 0
        self.risk_history = []

    def add_event(self, event, ai_result):

        self.events.append({
            "timestamp": time.strftime("%H:%M:%S"),
            "event": event,
            "ai_result": ai_result
        })

        self.failed_logins += event.get(
            "failed_logins",
            0
        )

        if event.get("device_changed", 0) == 1:
            self.new_device = True

        if event.get("geo_distance_km", 0) > 500:
            self.unusual_location = True

        self.sensitive_access += event.get(
            "sensitive_resources",
            0
        )

        self.download_mb += event.get(
            "downloads_mb",
            0
        )

        self.risk_history.append(
            ai_result["risk_score"]
        )

        # Keep only the recent behaviour window
        self.events = self.events[-20:]
        self.risk_history = self.risk_history[-20:]

    def calculate_behavior_risk(self):

        risk = 0

        # Failed authentication
        if self.failed_logins >= 3:
            risk += 15

        if self.failed_logins >= 8:
            risk += 15

        # New device
        if self.new_device:
            risk += 15

        # Geographic anomaly
        if self.unusual_location:
            risk += 20

        # Sensitive access
        if self.sensitive_access >= 5:
            risk += 15

        if self.sensitive_access >= 20:
            risk += 15

        # Data movement
        if self.download_mb >= 1000:
            risk += 15

        if self.download_mb >= 5000:
            risk += 20

        # Multiple elevated AI scores
        if len(self.risk_history) >= 3:

            recent = self.risk_history[-3:]

            if sum(
                score >= 60
                for score in recent
            ) >= 2:

                risk += 20

        return min(
            risk,
            100
        )

    def detect_attack_pattern(self):

        behavior_risk = (
            self.calculate_behavior_risk()
        )

        reasons = []

        if self.failed_logins >= 3:
            reasons.append(
                "Repeated authentication failures"
            )

        if self.new_device:
            reasons.append(
                "New device detected"
            )

        if self.unusual_location:
            reasons.append(
                "Unusual geographic activity"
            )

        if self.sensitive_access >= 5:
            reasons.append(
                "Sensitive resources accessed"
            )

        if self.download_mb >= 1000:
            reasons.append(
                "Abnormal data transfer"
            )

        if len(self.risk_history) >= 3:

            recent = self.risk_history[-3:]

            if sum(
                score >= 60
                for score in recent
            ) >= 2:

                reasons.append(
                    "Multiple elevated AI "
                    "risk events detected"
                )

        attack_detected = (
            behavior_risk >= 60
        )

        if behavior_risk >= 80:

            level = "CRITICAL"

        elif behavior_risk >= 60:

            level = "HIGH"

        elif behavior_risk >= 30:

            level = "MEDIUM"

        else:

            level = "LOW"

        return {

            "user_id": self.user_id,

            "behavior_risk":
                behavior_risk,

            "attack_detected":
                attack_detected,

            "level":
                level,

            "reasons":
                reasons
        }


# ============================================================
# RESPONSE ENGINE
# ============================================================

def generate_incident_response(
    incident
):

    if not incident["attack_detected"]:

        return {
            "action":
                "ALLOW",

            "message":
                "Continue monitoring user behaviour."
        }

    if incident["level"] == "CRITICAL":

        return {
            "action":
                "ISOLATE SESSION",

            "message":
                "Session isolated. "
                "Account flagged for investigation."
        }

    if incident["level"] == "HIGH":

        return {
            "action":
                "STEP-UP AUTHENTICATION",

            "message":
                "Require additional authentication "
                "and notify security personnel."
        }

    return {
        "action":
            "INCREASE MONITORING",

        "message":
            "Increase monitoring of the user session."
    }