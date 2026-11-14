import json
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path


DATA_FILE = Path(__file__).with_name("finance_data.json")


def parse_amount(value):
    """Return a positive monetary amount with at most two decimal places."""
    try:
        amount = Decimal(str(value).strip().replace(",", ""))
    except InvalidOperation as error:
        raise ValueError("Enter a valid amount.") from error

    if not amount.is_finite() or amount <= 0 or amount.as_tuple().exponent < -2:
        raise ValueError("Amount must be positive with no more than 2 decimal places.")
    return amount


def parse_date(value):
    """Validate an ISO date, defaulting an empty value to today's date."""
    value = str(value).strip()
    if not value:
        return date.today().isoformat()
    try:
        parsed_date = datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as error:
        raise ValueError("Use a valid date in YYYY-MM-DD format.") from error
    return parsed_date.isoformat()


def load_transactions():
    if not DATA_FILE.exists():
        return []

    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            transactions = json.load(file)
    except (OSError, json.JSONDecodeError):
        print("Could not read the data file. Starting with an empty tracker.")
        return []

    return transactions if isinstance(transactions, list) else []


def save_transactions(transactions):
    with DATA_FILE.open("w", encoding="utf-8") as file:
        json.dump(transactions, file, indent=2)


def read_amount(prompt):
    while True:
        value = input(prompt).strip()
        try:
            return float(parse_amount(value))
        except ValueError as error:
            print(error)


def read_date():
    while True:
        value = input(f"Date [{date.today().isoformat()}]: ")
        try:
            return parse_date(value)
        except ValueError as error:
            print(error)


def add_transaction(transactions):
    transaction_type = input("Type (income/expense): ").strip().lower()
    if transaction_type not in {"income", "expense"}:
        print("Type must be income or expense.")
        return

    transaction = {
        "type": transaction_type,
        "amount": read_amount("Amount: "),
        "category": input("Category: ").strip() or "Other",
        "description": input("Description: ").strip() or "No description",
        "date": read_date(),
    }
    transactions.append(transaction)
    save_transactions(transactions)
    print("Transaction saved.")


def list_transactions(transactions):
    if not transactions:
        print("No transactions yet.")
        return

    print("\n#  Date        Type     Category          Amount       Description")
    print("-" * 72)
    for index, transaction in enumerate(transactions, start=1):
        amount = f"{transaction['amount']:>9.2f}"
        print(
            f"{index:<3}{transaction['date']:<12}"
            f"{transaction['type']:<9}{transaction['category']:<18}"
            f"{amount}   {transaction['description']}"
        )


def show_summary(transactions):
    income = sum(
        Decimal(str(item["amount"]))
        for item in transactions
        if item["type"] == "income"
    )
    expenses = sum(
        Decimal(str(item["amount"]))
        for item in transactions
        if item["type"] == "expense"
    )
    balance = income - expenses

    print("\nFinancial summary")
    print(f"Income:   {income:,.2f}")
    print(f"Expenses: {expenses:,.2f}")
    print(f"Balance:  {balance:,.2f}")

    if transactions:
        by_category = {}
        for item in transactions:
            if item["type"] == "expense":
                category = item["category"]
                by_category[category] = by_category.get(category, 0) + item["amount"]
        if by_category:
            print("\nExpenses by category")
            for category, amount in sorted(by_category.items(), key=lambda pair: -pair[1]):
                print(f"{category}: {amount:,.2f}")


def delete_transaction(transactions):
    list_transactions(transactions)
    if not transactions:
        return

    try:
        choice = int(input("Transaction number to delete (0 to cancel): "))
        if choice == 0:
            return
        removed = transactions.pop(choice - 1)
    except (ValueError, IndexError):
        print("That is not a valid transaction number.")
        return

    save_transactions(transactions)
    print(f"Deleted: {removed['description']}.")


def main():
    transactions = load_transactions()
    actions = {
        "1": add_transaction,
        "2": list_transactions,
        "3": show_summary,
        "4": delete_transaction,
    }

    while True:
        print("\nPersonal Finance Tracker")
        print("1. Add transaction")
        print("2. List transactions")
        print("3. Show summary")
        print("4. Delete transaction")
        print("5. Exit")
        choice = input("Choose an option: ").strip()

        if choice == "5":
            print("Goodbye.")
            return
        if choice in actions:
            actions[choice](transactions)
        else:
            print("Choose an option from 1 to 5.")


if __name__ == "__main__":
    main()