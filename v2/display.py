from rich.table import Table
from rich.console import Console
from storage import normalize_category

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
            normalize_category(r.get('category')),
            r.get('note', '')
        )

    console.print(table)

    console.print(f"Total Income: {income_total:.2f}")
    console.print(f"Total Expense: {expense_total:.2f}")
    console.print(f"Balance: {income_total - expense_total:.2f}")

def make_bar(value, max_value, width=20):
    if max_value <= 0:
        return ""
    bar_len = int((value / max_value) * width)
    bar_len = max(1, bar_len)  
    return "█" * bar_len


def print_summary(result):
    console = Console()
    table = Table(title="Summary by Category")

    table.add_column("Category")
    table.add_column("Income", justify="right")
    table.add_column("Expense", justify="right")
    table.add_column("Count", justify="right")
    table.add_column("Chart")

    summary = result["summary"]

    max_value = 0
    for data in summary.values():
        max_value = max(max_value, data["income"], data["expense"])

    for category, data in summary.items():
        value = max(data["income"], data["expense"])

        bar = make_bar(value, max_value)
        category = normalize_category(category)

        table.add_row(
            category,
            f"{data['income']:.2f}",
            f"{data['expense']:.2f}",
            str(data["count"]),
            bar
        )

    console.print(table)

    console.print(f"Total Income : {result['total_income']:.2f}")
    console.print(f"Total Expense: {result['total_expense']:.2f}")
    console.print(f"Balance      : {result['balance']:.2f}")