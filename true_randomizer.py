import json
import os
import secrets


TRUE_RANDOM_HISTORY_FILE = "true_random_history.json"
TRUE_RANDOM_TRACK_CACHE_FILE = "true_random_track_cache.json"
TRUE_RANDOM_HISTORY_SIZE = 30
TRUE_RANDOM_QUEUE_LIMIT = 100
TRUE_RANDOM_TRACK_CACHE_MAX_AGE_SECONDS = 7 * 24 * 60 * 60


def dedupe_track_uris(track_uris):
    unique_tracks = []
    seen = set()

    for uri in track_uris:
        if not isinstance(uri, str) or not uri or ":local:" in uri:
            continue
        if uri in seen:
            continue
        seen.add(uri)
        unique_tracks.append(uri)

    return unique_tracks


def build_true_random_queue(track_uris, recent_history=None, queue_limit=TRUE_RANDOM_QUEUE_LIMIT, rng=None):
    rng = rng or secrets.SystemRandom()
    recent_history = recent_history or []

    unique_tracks = dedupe_track_uris(track_uris)
    recent_tracks = set(recent_history)
    non_recent = [uri for uri in unique_tracks if uri not in recent_tracks]
    recent = [uri for uri in unique_tracks if uri in recent_tracks]

    rng.shuffle(non_recent)
    rng.shuffle(recent)

    return (non_recent + recent)[:queue_limit]


def update_true_random_history(existing_history, selected_tracks, history_size=TRUE_RANDOM_HISTORY_SIZE):
    updated = []
    seen = set()

    for uri in list(selected_tracks) + list(existing_history or []):
        if not isinstance(uri, str) or not uri or uri in seen:
            continue
        seen.add(uri)
        updated.append(uri)
        if len(updated) >= history_size:
            break

    return updated


def load_true_random_history(history_path, logger=None):
    try:
        with open(history_path, "r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as exc:
        if logger:
            logger(f"True Randomizer: history file is malformed, starting fresh. {exc}")
        return {}
    except Exception as exc:
        if logger:
            logger(f"True Randomizer: failed to load history, starting fresh. {exc}")
        return {}

    if not isinstance(data, dict):
        if logger:
            logger("True Randomizer: history file has invalid structure, starting fresh.")
        return {}

    history = {}
    for playlist_id, tracks in data.items():
        if isinstance(playlist_id, str) and isinstance(tracks, list):
            history[playlist_id] = [uri for uri in tracks if isinstance(uri, str) and uri]

    return history


def save_true_random_history(history_path, history, logger=None):
    try:
        directory = os.path.dirname(history_path)
        if directory:
            os.makedirs(directory, exist_ok=True)

        temp_path = f"{history_path}.tmp"
        with open(temp_path, "w", encoding="utf-8") as file:
            json.dump(history, file, indent=4)
        os.replace(temp_path, history_path)
        return True
    except Exception as exc:
        if logger:
            logger(f"True Randomizer: failed to save history. {exc}")
        return False


def load_true_random_track_cache(cache_path, logger=None):
    try:
        with open(cache_path, "r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as exc:
        if logger:
            logger(f"True Randomizer: track cache is malformed, starting fresh. {exc}")
        return {}
    except Exception as exc:
        if logger:
            logger(f"True Randomizer: failed to load track cache, starting fresh. {exc}")
        return {}

    if not isinstance(data, dict):
        if logger:
            logger("True Randomizer: track cache has invalid structure, starting fresh.")
        return {}

    return data


def save_true_random_track_cache(cache_path, cache, logger=None):
    try:
        directory = os.path.dirname(cache_path)
        if directory:
            os.makedirs(directory, exist_ok=True)

        temp_path = f"{cache_path}.tmp"
        with open(temp_path, "w", encoding="utf-8") as file:
            json.dump(cache, file, indent=4)
        os.replace(temp_path, cache_path)
        return True
    except Exception as exc:
        if logger:
            logger(f"True Randomizer: failed to save track cache. {exc}")
        return False
