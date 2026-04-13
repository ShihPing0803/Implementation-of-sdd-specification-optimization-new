from rich.table import Table
from rich.console import Console

def choose_type():
    print("Please choose a type:")
    print("1. Income")
    print("2. Expense")
    choice = input("Please input 1 or 2: ").strip()

    if choice == "1":
        return "income"
    elif choice == "2":
        return "expense"
    else:
        print("[ERROR] ValidationError: Type must be 'income' or 'expense', or press Enter to keep the current value.")
        return choose_type()


def print_records(records, income_total=None, expense_total=None):
    console = Console()
    table = Table(title="All Records")

    table.add_column("ID")
    table.add_column("Type")
    table.add_column("Name")
    table.add_column("Amount", justify="right")
    table.add_column("Category")
    table.add_column("Note")

    for r in records:
        table.add_row(
            str(r['id']),
            r['type'],
            r['name'],
            f"{r['amount']:.2f}",
            r.get('category', '-'),
            r.get('note', '')
        )

    console.print(table)

    console.print(f"Total Income: {income_total:.2f}")
    console.print(f"Total Expense: {expense_total:.2f}")
    console.print(f"Balance: {income_total - expense_total:.2f}")