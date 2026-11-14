import csv
import tkinter as tk
from decimal import Decimal
from tkinter import filedialog, messagebox, ttk

from finance_tracker import load_transactions, parse_amount, parse_date, save_transactions


class FinanceTrackerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Personal Finance Tracker")
        self.geometry("980x650")
        self.minsize(820, 560)
        self.configure(bg="#f4f7fb")
        self.transactions = load_transactions()
        self.search_var = tk.StringVar()
        self.type_filter_var = tk.StringVar(value="all")

        self._configure_styles()
        self._build_header()
        self._build_summary()
        self._build_form()
        self._build_table()
        self.refresh()

    def _configure_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background="#f4f7fb")
        style.configure("Card.TFrame", background="#ffffff")
        style.configure("TLabel", background="#f4f7fb", foreground="#243047")
        style.configure("Card.TLabel", background="#ffffff", foreground="#243047")
        style.configure("Title.TLabel", background="#f4f7fb", foreground="#17233c", font=("Segoe UI", 24, "bold"))
        style.configure("Subtitle.TLabel", background="#f4f7fb", foreground="#69758a", font=("Segoe UI", 10))
        style.configure("Metric.TLabel", background="#ffffff", foreground="#17233c", font=("Segoe UI", 18, "bold"))
        style.configure("MetricName.TLabel", background="#ffffff", foreground="#69758a", font=("Segoe UI", 9))
        style.configure("TButton", font=("Segoe UI", 9, "bold"), padding=(9, 7))
        style.configure("Accent.TButton", background="#3478f6", foreground="#ffffff")
        style.map("Accent.TButton", background=[("active", "#2463d4")])
        style.configure("Treeview", background="#ffffff", fieldbackground="#ffffff", rowheight=34, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", background="#eaf0fa", foreground="#33415c", font=("Segoe UI", 9, "bold"), padding=8)
        style.map("Treeview", background=[("selected", "#dce9ff")], foreground=[("selected", "#17233c")])

    def _build_header(self):
        header = ttk.Frame(self)
        header.pack(fill="x", padx=28, pady=(24, 14))
        ttk.Label(header, text="Personal Finance Tracker", style="Title.TLabel").pack(anchor="w")
        ttk.Label(header, text="A clear view of where your money comes from and where it goes.", style="Subtitle.TLabel").pack(anchor="w", pady=(4, 0))

    def _build_summary(self):
        self.summary_frame = ttk.Frame(self)
        self.summary_frame.pack(fill="x", padx=28, pady=(0, 14))
        self.metric_labels = {}
        for key, title, color in (("income", "Income", "#16805b"), ("expenses", "Expenses", "#c04b4b"), ("balance", "Balance", "#3478f6")):
            card = ttk.Frame(self.summary_frame, style="Card.TFrame", padding=18)
            card.pack(side="left", fill="x", expand=True, padx=(0, 10))
            ttk.Label(card, text=title.upper(), style="MetricName.TLabel").pack(anchor="w")
            label = ttk.Label(card, text="$0.00", style="Metric.TLabel", foreground=color)
            label.pack(anchor="w", pady=(7, 0))
            self.metric_labels[key] = label

    def _build_form(self):
        form = ttk.Frame(self, style="Card.TFrame", padding=16)
        form.pack(fill="x", padx=28, pady=(0, 14))
        fields = (("type", "Type", ("income", "expense")), ("category", "Category", None), ("amount", "Amount", None), ("date", "Date", None), ("description", "Description", None))
        self.inputs = {}
        positions = {"type": (0, 0), "category": (0, 1), "amount": (0, 2), "date": (2, 0), "description": (2, 1)}
        for key, label, values in fields:
            row, column = positions[key]
            ttk.Label(form, text=label, style="Card.TLabel").grid(row=row, column=column, sticky="w", padx=5, pady=(0, 4))
            if values:
                widget = ttk.Combobox(form, values=values, state="readonly", width=12)
                widget.set(values[1])
            else:
                widget = ttk.Entry(form)
            span = 3 if key == "description" else 1
            widget.grid(row=row + 1, column=column, columnspan=span, sticky="ew", padx=5, pady=(0, 10))
            self.inputs[key] = widget
        for column in range(4):
            form.columnconfigure(column, weight=1 if column in (1, 2, 3) else 0)
        ttk.Button(form, text="Add transaction", style="Accent.TButton", command=self.add_transaction).grid(row=3, column=4, padx=(10, 5), pady=(0, 10), sticky="e")

    def _build_table(self):
        table_frame = ttk.Frame(self, style="Card.TFrame", padding=16)
        table_frame.pack(fill="both", expand=True, padx=28, pady=(0, 28))
        toolbar = ttk.Frame(table_frame, style="Card.TFrame")
        toolbar.pack(fill="x", pady=(0, 10))
        ttk.Label(toolbar, text="Recent transactions", style="Card.TLabel", font=("Segoe UI", 13, "bold")).pack(side="left")
        ttk.Button(toolbar, text="Delete selected", command=self.delete_selected).pack(side="right", padx=(8, 0))
        ttk.Button(toolbar, text="Export CSV", command=self.export_csv).pack(side="right", padx=(8, 0))
        type_filter = ttk.Combobox(toolbar, textvariable=self.type_filter_var, values=("all", "income", "expense"), state="readonly", width=10)
        type_filter.pack(side="right", padx=(8, 0))
        type_filter.bind("<<ComboboxSelected>>", lambda _event: self.refresh())
        search = ttk.Entry(toolbar, textvariable=self.search_var, width=22)
        search.pack(side="right", padx=(8, 0))
        search.bind("<KeyRelease>", lambda _event: self.refresh())
        ttk.Label(toolbar, text="Search", style="Card.TLabel").pack(side="right")

        columns = ("date", "type", "category", "amount", "description")
        self.table = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
        headings = {"date": "Date", "type": "Type", "category": "Category", "amount": "Amount", "description": "Description"}
        widths = {"date": 110, "type": 100, "category": 150, "amount": 120, "description": 300}
        for column in columns:
            self.table.heading(column, text=headings[column])
            self.table.column(column, width=widths[column], anchor="e" if column == "amount" else "w")
        self.table.tag_configure("income", foreground="#16805b")
        self.table.tag_configure("expense", foreground="#c04b4b")
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=scrollbar.set)
        self.table.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def add_transaction(self):
        transaction_type = self.inputs["type"].get()
        category = self.inputs["category"].get().strip() or "Other"
        description = self.inputs["description"].get().strip()
        amount_text = self.inputs["amount"].get().strip()
        transaction_date = self.inputs["date"].get().strip()

        try:
            amount = float(parse_amount(amount_text))
        except ValueError as error:
            messagebox.showerror("Invalid amount", str(error))
            return
        try:
            transaction_date = parse_date(transaction_date)
        except ValueError as error:
            messagebox.showerror("Invalid date", str(error))
            return
        if not transaction_type:
            messagebox.showerror("Missing type", "Choose income or expense.")
            return
        if not description:
            description = "No description"

        self.transactions.append({"type": transaction_type, "amount": amount, "category": category, "description": description, "date": transaction_date})
        try:
            save_transactions(self.transactions)
        except OSError as error:
            self.transactions.pop()
            messagebox.showerror("Could not save", f"The transaction could not be saved.\n{error}")
            return
        self.inputs["category"].delete(0, "end")
        self.inputs["amount"].delete(0, "end")
        self.inputs["description"].delete(0, "end")
        self.inputs["date"].delete(0, "end")
        self.refresh()

    def delete_selected(self):
        selection = self.table.selection()
        if not selection:
            messagebox.showinfo("Delete transaction", "Select a transaction first.")
            return
        if not messagebox.askyesno("Delete transaction", "Delete the selected transaction? This cannot be undone."):
            return
        index = int(selection[0])
        removed = self.transactions.pop(index)
        try:
            save_transactions(self.transactions)
        except OSError as error:
            self.transactions.insert(index, removed)
            messagebox.showerror("Could not save", f"The transaction could not be deleted.\n{error}")
            return
        self.refresh()

    def export_csv(self):
        if not self.transactions:
            messagebox.showinfo("Export transactions", "There are no transactions to export.")
            return
        output_path = filedialog.asksaveasfilename(
            title="Export transactions",
            defaultextension=".csv",
            filetypes=(("CSV files", "*.csv"), ("All files", "*.*")),
            initialfile="finance_transactions.csv",
        )
        if not output_path:
            return
        try:
            with open(output_path, "w", newline="", encoding="utf-8-sig") as file:
                writer = csv.DictWriter(file, fieldnames=("date", "type", "category", "amount", "description"))
                writer.writeheader()
                writer.writerows(self.transactions)
        except OSError as error:
            messagebox.showerror("Export failed", f"Could not write the CSV file.\n{error}")
            return
        messagebox.showinfo("Export complete", f"Exported {len(self.transactions)} transactions.")

    def refresh(self):
        for item in self.table.get_children():
            self.table.delete(item)
        query = self.search_var.get().strip().casefold()
        selected_type = self.type_filter_var.get()
        filtered = []
        for index, transaction in enumerate(self.transactions):
            searchable = " ".join(str(transaction.get(key, "")) for key in ("date", "type", "category", "description"))
            if selected_type != "all" and transaction["type"] != selected_type:
                continue
            if query and query not in searchable.casefold():
                continue
            filtered.append((index, transaction))
        for index, transaction in reversed(filtered):
            self.table.insert("", "end", iid=str(index), values=(transaction["date"], transaction["type"].title(), transaction["category"], f"${transaction['amount']:,.2f}", transaction["description"]), tags=(transaction["type"],))

        income = sum((Decimal(str(item["amount"])) for item in self.transactions if item["type"] == "income"), Decimal("0"))
        expenses = sum((Decimal(str(item["amount"])) for item in self.transactions if item["type"] == "expense"), Decimal("0"))
        self.metric_labels["income"].config(text=f"${income:,.2f}")
        self.metric_labels["expenses"].config(text=f"${expenses:,.2f}")
        self.metric_labels["balance"].config(text=f"${income - expenses:,.2f}")
        self.title("Personal Finance Tracker")


if __name__ == "__main__":
    FinanceTrackerApp().mainloop()