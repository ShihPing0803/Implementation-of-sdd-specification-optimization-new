from datetime import datetime
from storage import load_records, save_records
from error import ValidationError, BusinessError


def generate_id(records):
    if not records:
        return 1
    return max(record["id"] for record in records) + 1


def total_records(records):
    income_total = sum(record["amount"] for record in records if record["type"] == "income")
    expense_total = sum(record["amount"] for record in records if record["type"] == "expense")
    return income_total, expense_total


def find_record_by_id(records, record_id):
    for record in records:
        if record["id"] == record_id:
            return record
    return None


def validate_record_input(name, record_type, amount):
    if record_type not in ("income", "expense"):
        raise ValidationError("Type must be 'income' or 'expense'.")
    if not name or not name.strip():
        raise ValidationError("Name cannot be empty.")
    if amount <= 0:
        raise ValidationError("Amount must be greater than 0.")


def add_record(name, record_type, amount, category, note):
    records = load_records()

    validate_record_input(name, record_type, float(amount))

    new_record = {
        "id": generate_id(records),
        "type": record_type,
        "name": name.strip(),
        "amount": float(amount),
        "category": category.strip() if category and category.strip() else "-",
        "note": note.strip() if note and note.strip() else "",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    records.append(new_record)
    save_records(records)
    return records, new_record

def update_record(record_id, update_data):
    records = load_records("all")
    if not records:
        raise BusinessError("No records available.")

    record = find_record_by_id(records, record_id)
    if not record:
        raise BusinessError(f"Record with ID {record_id} not found.")
    if "name" in update_data:
        record["name"] = update_data["name"]
        
    if "type" in update_data:
        if update_data["type"] not in ("income", "expense"):
            raise ValidationError("Type must be 'income' or 'expense'.")
        record["type"] = update_data["type"]
        
    if "amount" in update_data:
        if update_data["amount"] <= 0:
            raise ValidationError("Amount must be greater than 0.")
        record["amount"] = float(update_data["amount"])
        
    if "category" in update_data:
        record["category"] = update_data["category"]
        
    if "note" in update_data:
        record["note"] = update_data["note"]

    save_records(records)
    return records, record


def delete_record(record_id):
    records = load_records()
    record = find_record_by_id(records, record_id)
    del_record = record
    if not record:
        raise BusinessError(f"Record with ID {record_id} not found.")

    records.remove(record)
    save_records(records)
    return records,del_record