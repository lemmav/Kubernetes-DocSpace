"""Kubernetes-level health: every pod is up and stable."""
import pytest

pytestmark = pytest.mark.cluster


def _running_pods(pods):
    # Completed jobs (db init, etc.) are expected to be not Ready.
    return [p for p in pods if p["status"]["phase"] != "Succeeded"]


def _is_ready(pod):
    conditions = pod["status"].get("conditions", [])
    return any(c["type"] == "Ready" and c["status"] == "True" for c in conditions)


def _restart_count(pod):
    return sum(c["restartCount"] for c in pod["status"].get("containerStatuses", []))


def test_all_pods_are_ready(pods):
    not_ready = [p["metadata"]["name"] for p in _running_pods(pods) if not _is_ready(p)]

    assert not not_ready, f"pods not Ready: {not_ready}"


def test_no_pod_has_restarted(pods):
    restarted = {p["metadata"]["name"]: _restart_count(p) for p in pods if _restart_count(p) > 0}

    assert not restarted, f"pods with container restarts: {restarted}"
