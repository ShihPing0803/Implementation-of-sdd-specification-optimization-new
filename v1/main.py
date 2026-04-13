import sys
from commands import build_parser
from service import add_record, update_record, delete_record, total_records, find_record_by_id
from storage import load_records
from display import print_records, choose_type
from error import ValidationError, BusinessError, StorageError

def main():
    parser = build_parser()
    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        return
    if args.command == "add":
        recordType = args.type if args.type else choose_type()
        result, new_record = add_record(args.name, recordType, args.amount, args.category, args.note)
        print(f"Added: [{new_record['id']}] {new_record['name']}")
    elif args.command == "list":
        result = load_records(args.type)

    elif args.command == "update":
        records = load_records("all")
        if not records:
            print("[ERROR] BusinessError: No records available.")
            sys.exit(1)

        try:
            record_id = int(input("Please enter the ID you want to update: ").strip())
        except ValueError:
            print("[ERROR] ValidationError: Invalid ID. Please enter a number.")
            sys.exit(1)

        record = find_record_by_id(records, record_id)
        if not record:
            print(f"[ERROR] BusinessError: Record with ID {record_id} not found.")
            sys.exit(1)

        update_data = {}

        update_name = input(f"Please input a new name or press Enter to skip (current: {record['name']}): ").strip()
        if update_name:
            update_data["name"] = update_name

        while True:
            update_type = input(f"Please input the type (income/expense) or press Enter to skip (current: {record['type']}): ").strip().lower()
            if update_type == "":
                break
            if update_type in ("income", "expense"):
                update_data["type"] = update_type
                break
            print("[ERROR] ValidationError: Type must be 'income' or 'expense', or press Enter to keep the current value.")

        update_amount = input(f"Please input a new amount or press Enter to skip (current: {record['amount']:.2f}): ").strip()
        if update_amount:
            try:
                amount_value = float(update_amount)
                if amount_value > 0:
                    update_data["amount"] = amount_value
                else:
                    print("[ERROR] ValidationError: Amount must be greater than 0. Keeping original value.")
            except ValueError:
                print("[ERROR] ValidationError: Invalid amount format. Keeping original value.")

        update_category = input(f"Please input a new category or press Enter to skip (current: {record.get('category', '-')}): ").strip()
        if update_category:
            update_data["category"] = update_category

        update_note = input(f"Please input a new note or press Enter to skip (current: {record.get('note', '')}): ").strip()
        if update_note:
            update_data["note"] = update_note

        result, new_record = update_record(record_id, update_data)
        if new_record is not None:
            print(f"Updated: [{new_record['id']}] {new_record['name']}")
    elif args.command == "delete":
        result, del_record = delete_record(args.id)

        if del_record is None:
            return
        else:
            print(f"Deleted: [{del_record['id']}] {del_record['name']}")

    else:
        result = []
    income_total, expense_total = total_records(result)
    print_records(result, income_total, expense_total)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("[ERROR] Operation cancelled by user.")
        sys.exit(1)
    except ValidationError as e:
        print(f"[ERROR] ValidationError: {e}")
        sys.exit(1)
    except BusinessError as e:
        print(f"[ERROR] BusinessError: {e}")
        sys.exit(1)
    except StorageError as e:
        print(f"[ERROR] StorageError: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] SystemError: {e}")
        sys.exit(1)