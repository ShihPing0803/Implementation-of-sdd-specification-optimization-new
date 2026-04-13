import csv
from datetime import datetime
from os import name
from storage import load_records, save_records, normalize_category
from error import ValidationError, BusinessError, StorageError


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

def summary_record(record_type):
    records = load_records(record_type)

    if not records:
        raise BusinessError("No records found.")

    summary = {}
    
    for r in records:
        category = normalize_category(r.get("category"))

        if category not in summary:
            summary[category] = {
                "income": 0.0,
                "expense": 0.0,
                "count": 0
            }

        if r["type"] == "income":
            summary[category]["income"] += r["amount"]
        elif r["type"] == "expense":
            summary[category]["expense"] += r["amount"]

        summary[category]["count"] += 1

    total_income = sum(r["amount"] for r in records if r["type"] == "income")
    total_expense = sum(r["amount"] for r in records if r["type"] == "expense")

    return {
        "summary": summary,
        "total_income": total_income,
        "total_expense": total_expense,
        "balance": total_income - total_expense
    }

def import_records(file_path):
    records = load_records("all")

    rows = None
    for encoding in ("utf-8-sig", "utf-8", "cp950"):
        try:
            with open(file_path, "r", encoding=encoding, newline="") as f:
                rows = list(csv.DictReader(f))
            break
        except UnicodeDecodeError:
            continue
        except FileNotFoundError:
            raise StorageError("File not found.")

    if rows is None:
        raise BusinessError("Failed to read file: unsupported encoding.")

    required_fields = {"type", "name", "amount"}
    if not rows:
        message = f"成功 0 筆、跳過 0 筆"
        return message
        
    if not required_fields.issubset(rows[0].keys()):
        raise BusinessError("Invalid CSV header. Required: type,name,amount")

    success_count = 0
    skipped_count = 0
    imported_records = []

    next_id = generate_id(records)

    for row in rows:
        try:
            record_type = (row.get("type") or "").strip().lower()
            name = (row.get("name") or "").strip()
            amount_raw = (row.get("amount") or "").strip()

            if amount_raw == "":
                raise ValidationError("Amount is required.")

            amount = float(amount_raw)
            validate_record_input(name, record_type, amount)

            category = (row.get("category") or "").strip() or "-"
            note = (row.get("note") or "").strip()

            new_record = {
                "id": next_id,
                "type": record_type,
                "name": name,
                "amount": amount,
                "category": category,
                "note": note,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

            records.append(new_record)
            imported_records.append(new_record)
            next_id += 1
            success_count += 1

        except (ValidationError, ValueError, KeyError):
            skipped_count += 1
            continue

    if success_count > 0:
        save_records(records)

    message = f"成功 {success_count} 筆、跳過 {skipped_count} 筆"
    return message