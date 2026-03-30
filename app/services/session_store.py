from threading import Lock

SESSION_MEMORY = {
    "last_prediction": None
}
SESSION_LOCK = Lock()


def set_last_prediction(data: dict):
    with SESSION_LOCK:
        SESSION_MEMORY["last_prediction"] = data


def get_last_prediction():
    with SESSION_LOCK:
        return SESSION_MEMORY.get("last_prediction")
