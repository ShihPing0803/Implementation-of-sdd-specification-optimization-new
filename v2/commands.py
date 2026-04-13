import argparse

def build_parser():
    parser = argparse.ArgumentParser(description="CLI")
    subparsers = parser.add_subparsers(dest="command")

    add_parser = subparsers.add_parser("add", help="Add a new record")
    add_parser.add_argument("--type", choices=["expense", "income"])
    add_parser.add_argument("--name", required=True)
    add_parser.add_argument("--amount", required=True, type=float)
    add_parser.add_argument("--note")
    add_parser.add_argument("--category")

    list_parser = subparsers.add_parser("list", help="List records")
    list_parser.add_argument("--type", choices=["expense", "income", "all"], default="all")
    list_parser.add_argument("--category")
    list_parser.add_argument("--startAt")
    list_parser.add_argument("--endAt")
    list_parser.add_argument("--sortBy", choices=["amount", "created_at"], default="created_at")
    list_parser.add_argument("--order", choices=["desc", "asc"], default="desc")

    subparsers.add_parser("update", help="Update a record interactively")

    delete_parser = subparsers.add_parser("delete", help="Delete a record using id")
    delete_parser.add_argument("--id", required=True, type=int)

    summary_parser = subparsers.add_parser("summary", help="Summary record based on category")
    summary_parser.add_argument("--type", choices=["income", "expense", "all"], default="all")

    import_parser = subparsers.add_parser("import", help="Import records from a CSV file")
    import_parser.add_argument("--file", required=True, help="Path to the CSV file to import")
    
    return parser
