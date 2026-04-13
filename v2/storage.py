import os
import json

from datetime import datetime
from error import StorageError, BusinessError, ValidationError

DATA_FILE = os.path.join(os.getcwd(), "data", "records.json")

def normalize_category(category):
    if category is None:
        return "uncategorized"

    value = str(category).strip()
    if value == "" or value == "-" or value.lower() == "uncategorized":
        return "uncategorized"

    return value

def validate_date_format(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise ValidationError("Invalid date format. Please use YYYY-MM-DD.")
    
def save_records(records):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2, ensure_ascii=False)
    except OSError as e:
        raise StorageError(f"Failed to save records file: {e}")


def load_records(record_type="all", category=None, startAt=None, endAt=None, sortBy="created_at", order="desc"):
    if not os.path.exists(DATA_FILE):
        return []

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()

            if not content:
                return []

            records = json.loads(content)

        if record_type is None or record_type == "all":
            result = records
        elif record_type == "income":
            result = [record for record in records if record["type"] == "income"]
        elif record_type == "expense":
            result = [record for record in records if record["type"] == "expense"]
        
        if category:
            
            filtered = [record for record in result if record.get("category").lower() == category.lower()]

            if not filtered:
                raise BusinessError(f"No records found for category '{category}'.")

            result = filtered

        if startAt:
            start = validate_date_format(startAt)
            result = [record for record in result if datetime.strptime(record["created_at"][:10], "%Y-%m-%d") >= start]

            if not result:
                raise BusinessError("No record at that time.")

        if endAt:
            end = validate_date_format(endAt)
            result = [record for record in result if datetime.strptime(record["created_at"][:10], "%Y-%m-%d") <= end]

            if not result:
                raise BusinessError("No record at that time.")
        
        if order is not None and order not in ["desc", "asc"]:
            raise ValidationError("Please type asc or desc")
        elif order == "desc":
            reverse = True
        elif order == "asc":
            reverse = False

        if sortBy is not None and sortBy not in ["amount", "created_at"]:
            raise ValidationError("Invalid sort value")
        
        if sortBy == "created_at":
            result.sort(
                key = lambda record: record["created_at"], reverse = reverse
            )
        else: 
            result.sort(
                key = lambda record: record["amount"],
                reverse = reverse
            )

        return result
    
    except json.JSONDecodeError as e:
        raise StorageError(f"Failed to parse records file: {e}")
    except OSError as e:
        raise StorageError(f"Failed to load records file: {e}")
