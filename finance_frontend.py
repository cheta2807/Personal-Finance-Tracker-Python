import tkinter as tk
from tkinter import messagebox, ttk

from finance_tracker import DATA_FILE, load_transactions, save_transactions


class FinanceTrackerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Personal Finance Tracker")
        self.geometry("980x650")
        self.minsize(820, 560)
        self.configure(bg="#f4f7fb")
        self.transactions = load_transactions()

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
        style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=(12, 8))
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
        for index, (key, label, values) in enumerate(fields):
            form.columnconfigure(index, weight=1)
            ttk.Label(form, text=label, style="Card.TLabel").grid(row=0, column=index, sticky="w", padx=5)
            if values:
                widget = ttk.Combobox(form, values=values, state="readonly", width=12)
                widget.set(values[1])
            else:
                widget = ttk.Entry(form)
                if key == "date":
                    widget.insert(0, "YYYY-MM-DD")
                elif key == "description":
                    widget.insert(0, "What was this for?")
            widget.grid(row=1, column=index, sticky="ew", padx=5, pady=(6, 0))
            self.inputs[key] = widget
        ttk.Button(form, text="Add transaction", style="Accent.TButton", command=self.add_transaction).grid(row=1, column=5, padx=(10, 5), pady=(6, 0))

    def _build_table(self):
        table_frame = ttk.Frame(self, style="Card.TFrame", padding=16)
        table_frame.pack(fill="both", expand=True, padx=28, pady=(0, 28))
        toolbar = ttk.Frame(table_frame, style="Card.TFrame")
        toolbar.pack(fill="x", pady=(0, 10))
        ttk.Label(toolbar, text="Recent transactions", style="Card.TLabel", font=("Segoe UI", 13, "bold")).pack(side="left")
        ttk.Button(toolbar, text="Delete selected", command=self.delete_selected).pack(side="right")

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
        amount_text = self.inputs["amount"].get().strip().replace(",", "")
        transaction_date = self.inputs["date"].get().strip()

        try:
            amount = round(float(amount_text), 2)
            if amount <= 0 or round(amount, 2) != amount:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid amount", "Enter a positive amount with no more than 2 decimal places.")
            return
        if not description or description == "What was this for?":
            description = "No description"
        if not transaction_date or transaction_date == "YYYY-MM-DD":
            messagebox.showerror("Invalid date", "Enter a date in YYYY-MM-DD format.")
            return

        self.transactions.append({"type": transaction_type, "amount": amount, "category": category, "description": description, "date": transaction_date})
        save_transactions(self.transactions)
        self.inputs["category"].delete(0, "end")
        self.inputs["amount"].delete(0, "end")
        self.inputs["description"].delete(0, "end")
        self.inputs["date"].delete(0, "end")
        self.inputs["date"].insert(0, "YYYY-MM-DD")
        self.inputs["description"].insert(0, "What was this for?")
        self.refresh()

    def delete_selected(self):
        selection = self.table.selection()
        if not selection:
            messagebox.showinfo("Delete transaction", "Select a transaction first.")
            return
        index = int(selection[0])
        self.transactions.pop(index)
        save_transactions(self.transactions)
        self.refresh()

    def refresh(self):
        for item in self.table.get_children():
            self.table.delete(item)
        for index, transaction in reversed(list(enumerate(self.transactions))):
            self.table.insert("", "end", iid=str(index), values=(transaction["date"], transaction["type"].title(), transaction["category"], f"${transaction['amount']:,.2f}", transaction["description"]), tags=(transaction["type"],))

        income = sum(item["amount"] for item in self.transactions if item["type"] == "income")
        expenses = sum(item["amount"] for item in self.transactions if item["type"] == "expense")
        self.metric_labels["income"].config(text=f"${income:,.2f}")
        self.metric_labels["expenses"].config(text=f"${expenses:,.2f}")
        self.metric_labels["balance"].config(text=f"${income - expenses:,.2f}")
        self.title(f"Personal Finance Tracker - {DATA_FILE.name}")


if __name__ == "__main__":
    FinanceTrackerApp().mainloop()