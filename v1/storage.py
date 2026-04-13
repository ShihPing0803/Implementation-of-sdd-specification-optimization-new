import os
import json

from error import StorageError

DATA_FILE = os.path.join(os.getcwd(), "data", "records.json")


def save_records(records):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2, ensure_ascii=False)
    except OSError as e:
        raise StorageError(f"Failed to save records file: {e}")


def load_records(record_type=None):
    if not os.path.exists(DATA_FILE):
        return []

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()

            if not content:
                return []

            records = json.loads(content)

        if record_type is None or record_type == "all":
            return records
        if record_type == "income":
            return [record for record in records if record["type"] == "income"]
        if record_type == "expense":
            return [record for record in records if record["type"] == "expense"]

        raise StorageError(f"Failed to load records file: invalid record type '{record_type}'.")

    except json.JSONDecodeError as e:
        raise StorageError(f"Failed to parse records file: {e}")
    except OSError as e:
        raise StorageError(f"Failed to load records file: {e}")