"""Kubernetes pods as seen by kubectl."""
import json
import subprocess

SUCCEEDED = "Succeeded"


def fetch_pods(namespace):
    """All pods of the namespace as parsed `kubectl get pods -o json` items."""
    result = subprocess.run(
        ["kubectl", "get", "pods", "-n", namespace, "-o", "json"],
        capture_output=True, text=True, check=True,
    )
    return json.loads(result.stdout)["items"]


def running_pods(pods):
    """Completed jobs (db init, etc.) are expected to be not Ready, so they are left out."""
    return [pod for pod in pods if pod["status"]["phase"] != SUCCEEDED]


def is_ready(pod):
    conditions = pod["status"].get("conditions", [])
    return any(c["type"] == "Ready" and c["status"] == "True" for c in conditions)


def restart_count(pod):
    return sum(c["restartCount"] for c in pod["status"].get("containerStatuses", []))
