import tkinter as tk
from tkinter import messagebox, ttk
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pymongo import MongoClient

#DATABASE SETUP 
client = MongoClient("mongodb://localhost:27017/")
db = client["expense_tracker"]
collection = db["expenses"]

#FUNCTIONS
def add_expense():
    desc = desc_box.get()
    amount = amount_box.get()
    category = category_box.get()
    date = date_box.get()

    if desc and amount and category and date:
        try:
            amount = float(amount)

            collection.insert_one({
                "description": desc,
                "amount": amount,
                "category": category,
                "date": date
            })

            messagebox.showinfo("Success", "Expense Added Successfully")
            clear_fields()
            show_expenses()

        except ValueError:
            messagebox.showerror("Error", "Amount must be a number")
    else:
        messagebox.showwarning("Warning", "Please fill all fields")


def clear_fields():
    desc_box.delete(0, tk.END)
    amount_box.delete(0, tk.END)
    category_box.delete(0, tk.END)
    date_box.delete(0, tk.END)


def show_expenses():
    for row in tree.get_children():
        tree.delete(row)

    data = collection.find()

    for item in data:
        tree.insert("", tk.END, values=(
            item["description"],
            item["amount"],
            item["category"],
            item["date"]
        ))


def delete_expense():
    selected = tree.focus()

    if not selected:
        messagebox.showwarning("Select", "Please select a record")
        return

    values = tree.item(selected, "values")

    if values:
        collection.delete_one({
            "description": values[0],
            "amount": float(values[1])
        })

        messagebox.showinfo("Deleted", "Expense Deleted")
        show_expenses()


def show_chart():
    data = list(collection.find())

    if not data:
        messagebox.showinfo("No Data", "No expenses to show")
        return

    df = pd.DataFrame(data)

    category_sum = df.groupby("category")["amount"].sum()

    category_sum.plot(kind="bar", color="skyblue")
    plt.title("Category-wise Expenses")
    plt.xlabel("Category")
    plt.ylabel("Amount")
    plt.tight_layout()
    plt.show()


def show_total():
    data = list(collection.find())

    amounts = [item["amount"] for item in data]

    total = np.sum(amounts)

    messagebox.showinfo("Total Expense", f"Total Spending: ₹{total}")


# GUI SETUP
root = tk.Tk()
root.title("Personal Expense Tracker")
root.geometry("600x500")

tk.Label(root, text="Description").pack()
desc_box = tk.Entry(root)
desc_box.pack()

tk.Label(root, text="Amount").pack()
amount_box = tk.Entry(root)
amount_box.pack()

tk.Label(root, text="Category").pack()
category_box = tk.Entry(root)
category_box.pack()

tk.Label(root, text="Date (DD-MM-YYYY)").pack()
date_box = tk.Entry(root)
date_box.pack()

tk.Button(root, text="Add Expense", command=add_expense, bg="green", fg="white").pack(pady=5)
tk.Button(root, text="Show Chart", command=show_chart).pack(pady=5)
tk.Button(root, text="Total Expense", command=show_total).pack(pady=5)
tk.Button(root, text="Delete Selected", command=delete_expense, bg="red", fg="white").pack(pady=5)

tree = ttk.Treeview(root, columns=("Description", "Amount", "Category", "Date"), show="headings")

for col in ("Description", "Amount", "Category", "Date"):
    tree.heading(col, text=col)

tree.pack(fill=tk.BOTH, expand=True)

show_expenses()

root.mainloop()
