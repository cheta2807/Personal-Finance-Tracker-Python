# Personal Finance Tracker

A small desktop and command-line app for recording personal income and expenses. It uses only Python's standard library, stores records in a local JSON file, and includes a Tkinter interface.

## Features

- Add income and expense transactions with category, description, amount, and date
- View income, expenses, and balance totals
- Search transactions and filter by income or expense
- Delete a selected transaction with confirmation
- Export transactions to CSV
- Keep transaction data local on your computer

## Requirements

- Python 3.10 or later
- Tkinter (included with most Windows Python installations)

No third-party packages are required.

## Start the desktop app

From this folder, run:

```bash
python finance_frontend.py
```

## Start the command-line app

```bash
python finance_tracker.py
```

## Run the tests

```bash
python -m unittest discover -s tests -v
```

## Data and privacy

Transactions are stored in `finance_data.json` beside the application. This file is ignored by Git so your personal records are not included when you publish the project. CSV exports are also ignored. Back up your JSON file privately if you want to preserve your records.
