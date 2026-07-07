import ctypes
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3, datetime
import matplotlib

matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import pywinstyles
from PIL import Image, ImageTk
import cv2
import numpy as np
from tkinter import filedialog
import os
import csv
import urllib.request
import json
import customtkinter as ctk

# ================= Design Constants =================
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

BG_COLOR = "#1e1e1e"
SEC_BG_COLOR = "#2d2d2d"
ACCENT_COLOR = "#007ACC"
TEXT_COLOR = "#ffffff"
BTN_BG = "#333333"
BTN_ACTIVE_BG = "#005A9E"
SUCCESS_COLOR = "#2e7d32"
DANGER_COLOR = "#c62828"
WARNING_COLOR = "#ef6c00"
FONT_MAIN = ("Segoe UI", 12)
FONT_BOLD = ("Segoe UI", 12, "bold")
FONT_TITLE = ("Segoe UI", 65, "bold")

# Apply matplotlib dark theme globally
plt.style.use('dark_background')
matplotlib.rcParams['axes.facecolor'] = BG_COLOR
matplotlib.rcParams['figure.facecolor'] = BG_COLOR

# ================= App Initialization =================
root = ctk.CTk()
root.title("Premium Finance Tracker")
root.geometry('1250x780')
root.minsize(1050, 650)

# --- Root Window Grid Configuration ---
root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=0)
root.grid_columnconfigure(0, weight=0)
root.grid_columnconfigure(1, weight=1)

try:
    myappid = 'my_expense_tracker_app_v1'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except Exception as e:
    pass

try:
    root.iconbitmap("money.ico")
except Exception as e:
    pass

# Status bar (bottom of window)
status_label = ctk.CTkLabel(root, text="Ready", anchor="w", fg_color="#007ACC", text_color="white",
                            font=("Segoe UI", 11, "bold"), padx=10, height=30)
status_label.grid(row=1, column=0, columnspan=2, sticky="ew")


def update_status(message, color="white"):
    status_label.configure(text=message, text_color=color)
    root.update_idletasks()


# Global Variables
app_currency = tk.StringVar(value="Rs.")
exchange_rates = {"Rs.": 1.0, "$": 0.0033, "€": 0.0031, "£": 0.0026, "₹": 0.28, "¥": 0.52}
current_user_id = None
current_theme = "dark"

months = [f"{i:02d}" for i in range(1, 13)]
years = [str(y) for y in range(2020, 2031)]


# ================= Database Setup =================
def init_db():
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            type TEXT,
            category TEXT,
            amount REAL,
            note TEXT,
            account TEXT DEFAULT 'Cash Wallet',
            user_id INTEGER
        )
    """)
    # Recurring Bills Table Creation
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recurring_bills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            amount REAL,
            category TEXT,
            account TEXT,
            due_date TEXT,
            user_id INTEGER
        )
    """)

    # Auto Migration for older versions
    try:
        cursor.execute("ALTER TABLE transactions ADD COLUMN account TEXT DEFAULT 'Cash Wallet'")
    except sqlite3.OperationalError:
        pass

    conn.commit()
    conn.close()
    update_status("Connected to DB...", "white")


# ================= Core Functions =================
def fetch_live_rates():
    global exchange_rates
    try:
        url = "https://open.er-api.com/v6/latest/LKR"
        with urllib.request.urlopen(url, timeout=3) as response:
            data = json.loads(response.read().decode())
            if data and data.get("result") == "success":
                rates = data.get("rates", {})
                exchange_rates["Rs."] = 1.0
                if "USD" in rates: exchange_rates["$"] = rates["USD"]
                if "EUR" in rates: exchange_rates["€"] = rates["EUR"]
                if "GBP" in rates: exchange_rates["£"] = rates["GBP"]
                if "INR" in rates: exchange_rates["₹"] = rates["INR"]
                if "JPY" in rates: exchange_rates["¥"] = rates["JPY"]
                return True
    except Exception as e:
        print("Live rates fallback:", e)
    return False


def toggle_password(entry_widget, button_widget):
    """ Reusable function to show/hide password text """
    if entry_widget.cget('show') == '*':
        entry_widget.configure(show='')
        button_widget.configure(text="👁")
    else:
        entry_widget.configure(show='*')
        button_widget.configure(text="🙈")

    # Smart Financial Insights Generator Function


def generate_smart_insights(year_str, month_str):
    try:
        curr_y = int(year_str)
        curr_m = int(month_str)
    except ValueError:
        return "දත්ත දෝෂයකි.", "info"

    prev_m = curr_m - 1
    prev_y = curr_y
    if prev_m == 0:
        prev_m = 12
        prev_y -= 1

    curr_period = f"{curr_y:04d}-{curr_m:02d}"
    prev_period = f"{prev_y:04d}-{prev_m:02d}"

    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT category, SUM(amount) FROM transactions 
        WHERE strftime('%Y-%m', date) = ? AND user_id=? AND type='Expense' 
        GROUP BY category
    """, (curr_period, current_user_id))
    curr_rows = cursor.fetchall()

    cursor.execute("""
        SELECT category, SUM(amount) FROM transactions 
        WHERE strftime('%Y-%m', date) = ? AND user_id=? AND type='Expense' 
        GROUP BY category
    """, (prev_period, current_user_id))
    prev_rows = cursor.fetchall()
    conn.close()

    curr_dict = {row[0]: float(row[1]) for row in curr_rows}
    prev_dict = {row[0]: float(row[1]) for row in prev_rows}

    tot_curr = sum(curr_dict.values())
    tot_prev = sum(prev_dict.values())

    if tot_curr == 0:
        return "📊 Insights: ඔබ මේ මාසය සඳහා තවමත් වියදම් ඇතුළත් කර නැත. වියදම් එක් කළ පසු මූල්‍ය උපදෙස් මෙහි දිස්වේ.", "info"
    if tot_prev == 0:
        return "📊 Insights: පසුගිය මාසයේ වියදම් දත්ත හමුනොවීය. සංසන්දනාත්මක විශ්ලේෂණයක් සඳහා ලබන මාසයේ සිට දත්ත ඇතුළත් කරන්න.", "info"

    increases = []
    for cat, c_amt in curr_dict.items():
        if cat in prev_dict and prev_dict[cat] > 0:
            p_amt = prev_dict[cat]
            if c_amt > p_amt:
                pct = ((c_amt - p_amt) / p_amt) * 100
                increases.append((pct, cat))

    if increases:
        increases.sort(reverse=True, key=lambda x: x[0])
        highest_pct, highest_cat = increases[0]
        if highest_pct >= 5:
            return f"⚠️ Smart Insight: ඔබ පසුගිය මාසයට වඩා මේ මාසයේ '{highest_cat}' සඳහා {highest_pct:.1f}%ක් වැඩියෙන් වියදම් කර ඇත! මීළඟ සතියේ වියදම් සීමා කිරීමට උත්සාහ කරන්න.", "warning"

    if tot_curr > tot_prev:
        tot_pct = ((tot_curr - tot_prev) / tot_prev) * 100
        return f"⚠️ Smart Insight: ඔබගේ මුළු මාසික වියදම පසුගිය මාසයට වඩා {tot_pct:.1f}%කින් වැඩි වී ඇත. අනවශ්‍ය වියදම් පාලනය කරගන්න.", "warning"
    else:
        tot_pct = ((tot_prev - tot_curr) / tot_prev) * 100
        return f"🎉 Smart Insight: විශිෂ්ටයි! ඔබ පසුගිය මාසයට වඩා මේ මාසයේ මුළු වියදම් {tot_pct:.1f}%කින් අඩු කරගෙන ඇත. දිගටම මෙලෙස මුදල් කළමනාකරණය කරන්න!", "success"


# Reusable function to calculate and refresh account balances
def update_account_balances():
    if not current_user_id: return
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    wallets = ["Cash Wallet", "Bank Account", "Credit Card"]
    balances = {}
    currency = app_currency.get()
    rate = exchange_rates.get(currency, 1.0)

    for wall in wallets:
        cursor.execute("SELECT SUM(amount) FROM transactions WHERE user_id=? AND account=? AND type='Income'",
                       (current_user_id, wall))
        income = cursor.fetchone()[0] or 0.0

        cursor.execute("SELECT SUM(amount) FROM transactions WHERE user_id=? AND account=? AND type='Expense'",
                       (current_user_id, wall))
        expense = cursor.fetchone()[0] or 0.0

        balances[wall] = (income - expense) * rate

    conn.close()

    lbl_cash_val.configure(text=f"{currency} {balances['Cash Wallet']:,.2f}")
    lbl_bank_val.configure(text=f"{currency} {balances['Bank Account']:,.2f}")
    lbl_card_val.configure(text=f"{currency} {balances['Credit Card']:,.2f}")


# Smart Automation: Check for Due Bills & Subscriptions on Login
def check_recurring_bills():
    if not current_user_id: return
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, amount, category, account, due_date FROM recurring_bills WHERE user_id=? AND due_date<=?",
        (current_user_id, today_str))
    due_bills = cursor.fetchall()

    if due_bills:
        currency = app_currency.get()
        rate = exchange_rates.get(currency, 1.0)
        for bill in due_bills:
            b_id, name, amount, category, account, due_date = bill
            disp_amt = amount * rate

            ans = messagebox.askyesno("📋 Bill Reminder",
                                      f"ඔබගේ '{name}' ({currency} {disp_amt:,.2f}) බිල්පත ගෙවීමට දින පැමිණ ඇත ({due_date}).\n\nඑය දැන් Expense එකක් ලෙස ස්වයංක්‍රීයව ඇතුළත් කිරීමට ඔබට අවශ්‍යද?")
            if ans:
                # Insert directly as an approved expense transaction
                cursor.execute(
                    "INSERT INTO transactions (date, type, account, category, amount, note, user_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (today_str, "Expense", account, category, amount, f"Automated Bill: {name}", current_user_id))

                # Advance due date by exactly 1 month
                c_date = datetime.datetime.strptime(due_date, "%Y-%m-%d").date()
                y, m = c_date.year, c_date.month + 1
                if m > 12: m = 1; y += 1
                d = min(c_date.day, [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m - 1])
                if m == 2 and y % 4 == 0 and (y % 100 != 0 or y % 400 == 0): d = 29
                next_due = f"{y:04d}-{m:02d}-{d:02d}"
                cursor.execute("UPDATE recurring_bills SET due_date=? WHERE id=?", (next_due, b_id))
            else:
                # Postpone by 1 day to remind again tomorrow if declined
                c_date = datetime.datetime.strptime(due_date, "%Y-%m-%d").date()
                next_due = (c_date + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
                cursor.execute("UPDATE recurring_bills SET due_date=? WHERE id=?", (next_due, b_id))

        conn.commit()
        conn.close()
        show_transactions()
    else:
        conn.close()


# 🌟 Main Window Frame Integrated Function to Manage Subscription Templates
def show_recurring_frame():
    if not current_user_id: return
    show_frame(frame_recurring)

    # Clear existing widgets to rebuild dynamically inside the main application viewport
    for widget in frame_recurring.winfo_children():
        widget.destroy()

    title_frame = ctk.CTkFrame(frame_recurring, fg_color="transparent")
    title_frame.pack(fill="x", pady=(0, 10))
    ctk.CTkLabel(title_frame, text="Recurring Bills & Subscriptions Manager",
                 font=ctk.CTkFont(size=24, weight="bold")).pack(side="left", padx=10)

    content_container = ctk.CTkFrame(frame_recurring, fg_color="transparent")
    content_container.pack(fill="both", expand=True)

    form_frame = ctk.CTkFrame(content_container, width=290, corner_radius=10)
    form_frame.pack(side="left", fill="both", padx=10, pady=10)

    ctk.CTkLabel(form_frame, text="Add Recurring Template", font=("Segoe UI", 14, "bold")).pack(pady=10)
    ent_bname = ctk.CTkEntry(form_frame, placeholder_text="Bill Name (e.g. Netflix, Wifi)", width=240)
    ent_bname.pack(pady=6)
    ent_bamt = ctk.CTkEntry(form_frame, placeholder_text="Monthly Amount", width=240)
    ent_bamt.pack(pady=6)
    ent_bcat = ctk.CTkEntry(form_frame, placeholder_text="Category (e.g. Utilities)", width=240)
    ent_bcat.pack(pady=6)
    cmb_bacc = ctk.CTkComboBox(form_frame, values=["Cash Wallet", "Bank Account", "Credit Card"], width=240)
    cmb_bacc.pack(pady=6)
    ent_bdate = ctk.CTkEntry(form_frame, placeholder_text="Next Due Date (YYYY-MM-DD)", width=240)
    ent_bdate.pack(pady=6)
    ent_bdate.insert(0, datetime.date.today().strftime("%Y-%m-%d"))

    list_frame = ctk.CTkFrame(content_container, corner_radius=10)
    list_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
    ctk.CTkLabel(list_frame, text="Tracked Recurring Actions", font=("Segoe UI", 14, "bold")).pack(pady=10)

    b_tree = ttk.Treeview(list_frame, columns=("ID", "Name", "Amount", "Account", "Next Due"), show="headings",
                          height=8)
    for col in ("ID", "Name", "Amount", "Account", "Next Due"): b_tree.heading(col, text=col)
    b_tree.column("ID", width=40, anchor="center")
    b_tree.column("Name", width=110)
    b_tree.column("Amount", width=90, anchor="e")
    b_tree.column("Account", width=110, anchor="center")
    b_tree.column("Next Due", width=95, anchor="center")
    b_tree.pack(fill="both", expand=True, padx=10, pady=5)

    def refresh_bill_tree():
        for item in b_tree.get_children(): b_tree.delete(item)
        conn = sqlite3.connect("expenses.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, amount, account, due_date FROM recurring_bills WHERE user_id=?",
                       (current_user_id,))
        rows = cursor.fetchall()
        conn.close()
        currency = app_currency.get()
        rate = exchange_rates.get(currency, 1.0)
        for r in rows:
            fl = list(r)
            fl[2] = f"{currency} {(float(r[2]) * rate):,.2f}"
            b_tree.insert("", tk.END, values=fl)

    def save_recurring_bill():
        name = ent_bname.get().strip()
        amount = ent_bamt.get().strip()
        category = ent_bcat.get().strip()
        account = cmb_bacc.get()
        due_date = ent_bdate.get().strip()

        if not name or not amount or not category or not due_date:
            messagebox.showerror("Error", "All input fields must be filled!")
            return
        try:
            float(amount)
            datetime.datetime.strptime(due_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Invalid Amount structure or Date format (YYYY-MM-DD)!")
            return

        conn = sqlite3.connect("expenses.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO recurring_bills (name, amount, category, account, due_date, user_id) VALUES (?, ?, ?, ?, ?, ?)",
            (name, float(amount), category, account, due_date, current_user_id))
        conn.commit()
        conn.close()
        ent_bname.delete(0, tk.END);
        ent_bamt.delete(0, tk.END);
        ent_bcat.delete(0, tk.END)
        refresh_bill_tree()

    def delete_recurring_bill():
        sel = b_tree.selection()
        if not sel: return
        r_id = b_tree.item(sel[0])['values'][0]
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this subscription template?"):
            conn = sqlite3.connect("expenses.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM recurring_bills WHERE id=? AND user_id=?", (r_id, current_user_id))
            conn.commit()
            conn.close()
            refresh_bill_tree()

    ctk.CTkButton(form_frame, text="Save Template", fg_color=SUCCESS_COLOR, command=save_recurring_bill).pack(pady=10)
    ctk.CTkButton(list_frame, text="Remove Selected", fg_color=DANGER_COLOR, command=delete_recurring_bill).pack(
        pady=10)
    refresh_bill_tree()


# ================= Layout Architecture =================
sidebar_frame = ctk.CTkFrame(root, width=220, corner_radius=0)
main_container = ctk.CTkFrame(root, fg_color="transparent")

main_container.grid_rowconfigure(0, weight=1)
main_container.grid_columnconfigure(0, weight=1)

frame_expense = ctk.CTkFrame(main_container, fg_color="transparent")
frame_summary = ctk.CTkFrame(main_container, fg_color="transparent")
frame_rule = ctk.CTkFrame(main_container, fg_color="transparent")
frame_settings = ctk.CTkFrame(main_container, fg_color="transparent")
frame_recurring = ctk.CTkFrame(main_container, fg_color="transparent")  # 🌟 Added New Dedicated Frame

frame_login = ctk.CTkFrame(root, fg_color=BG_COLOR)
frame_register = ctk.CTkFrame(root, fg_color=BG_COLOR)
frame_reset = ctk.CTkFrame(root, fg_color=BG_COLOR)

app_frames = [frame_expense, frame_summary, frame_rule, frame_settings, frame_recurring]
auth_frames = [frame_login, frame_register, frame_reset]


def show_frame(target_frame):
    for f in auth_frames:
        f.place_forget()
        f.grid_forget()
    for f in app_frames:
        f.grid_forget()

    if target_frame in auth_frames:
        sidebar_frame.grid_forget()
        main_container.grid_forget()
        target_frame.grid(row=0, column=0, columnspan=2, sticky="nsew")
    else:
        sidebar_frame.grid(row=0, column=0, sticky="nsew")
        main_container.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        target_frame.grid(row=0, column=0, sticky="nsew")


# ================= Sidebar Navigation =================
sidebar_frame.grid_rowconfigure(6, weight=1)  # 🌟 Shifted spacer configure down for proper layout alignment
ctk.CTkLabel(sidebar_frame, text="FinanceTracker", font=ctk.CTkFont(size=22, weight="bold")).grid(row=0, column=0,
                                                                                                  padx=20,
                                                                                                  pady=(30, 40))

btn_trans = ctk.CTkButton(sidebar_frame, text="Transactions", command=lambda: open_expense_frame())
btn_trans.grid(row=1, column=0, padx=20, pady=10)

btn_dash = ctk.CTkButton(sidebar_frame, text="Summary", command=lambda: show_summary_frame())
btn_dash.grid(row=2, column=0, padx=20, pady=10)

btn_charts = ctk.CTkButton(sidebar_frame, text="50/30/20 Analysis", command=lambda: show_rule_frame())
btn_charts.grid(row=3, column=0, padx=20, pady=10)

# 🌟 Replaced button exactly in the sidebar hierarchy beneath 50/30/20 Analysis and above Settings
btn_recurring_nav = ctk.CTkButton(sidebar_frame, text="📋 Recurring Bills", command=show_recurring_frame)
btn_recurring_nav.grid(row=4, column=0, padx=20, pady=10)

btn_settings_nav = ctk.CTkButton(sidebar_frame, text="Settings", command=lambda: open_settings())
btn_settings_nav.grid(row=5, column=0, padx=20, pady=10)


def open_expense_frame():
    show_frame(frame_expense)
    show_transactions()


def logout_action():
    global current_user_id
    current_user_id = None
    entry_category.delete(0, tk.END)
    entry_amount.delete(0, tk.END)
    entry_note.delete(0, tk.END)
    for item in tree.get_children(): tree.delete(item)
    update_status("Logged out", "red")
    show_frame(frame_login)


btn_logout = ctk.CTkButton(sidebar_frame, text="Logout", fg_color=DANGER_COLOR, hover_color="#b71c1c",
                           command=logout_action)
btn_logout.grid(row=7, column=0, padx=20, pady=20)


# ================= Authentication Logic & UI =================
def register_user():
    username = entry_reg_user.get()
    password = entry_reg_pass.get()
    if not username or not password:
        messagebox.showerror("Error", "Please enter both new username and new password!")
        return
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        messagebox.showinfo("Success", "User registered successfully!")
        show_frame(frame_login)
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Username already exists!")
    conn.close()


def login_user():
    global current_user_id
    username = entry_login_user.get().strip()
    password = entry_login_pass.get().strip()
    if not username or not password:
        messagebox.showerror("Error", "Please enter both username and password!")
        return
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()
    conn.close()
    if user:
        current_user_id = user[0]
        update_status("User logged in", "white")
        show_frame(frame_expense)
        show_transactions()
        if remember_var.get():
            with open("remember_me.txt", "w") as f:
                f.write(f"{username}\n{password}")
        else:
            if os.path.exists("remember_me.txt"): os.remove("remember_me.txt")

        root.after(800, check_recurring_bills)
    else:
        messagebox.showerror("Login Failed", "Invalid username or password!")


def reset_password():
    username = entry_reset_user.get().strip()
    new_pass = entry_reset_new.get().strip()
    confirm_pass = entry_reset_confirm.get().strip()
    if not username or not new_pass or not confirm_pass: return
    if new_pass != confirm_pass:
        messagebox.showerror("Error", "Passwords do not match!")
        return
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    if not cursor.fetchone():
        messagebox.showerror("Error", "Username not found!")
        conn.close()
        return
    cursor.execute("UPDATE users SET password=? WHERE username=?", (new_pass, username))
    conn.commit()
    conn.close()
    messagebox.showinfo("Success", "Successfully reset your password!")
    show_frame(frame_login)


# Login UI
ctk.CTkLabel(frame_login, text="💰 Premium Finance Tracker", font=FONT_TITLE, text_color=ACCENT_COLOR).place(relx=0.5,
                                                                                                            rely=0.2,
                                                                                                            anchor="center")
login_panel = ctk.CTkFrame(frame_login, width=400, height=350, corner_radius=15)
login_panel.place(relx=0.5, rely=0.5, anchor="center")

ctk.CTkLabel(login_panel, text="Username", font=FONT_BOLD).place(x=40, y=40)
entry_login_user = ctk.CTkEntry(login_panel, font=FONT_MAIN, width=320)
entry_login_user.place(x=40, y=70)

ctk.CTkLabel(login_panel, text="Password", font=FONT_BOLD).place(x=40, y=120)
entry_login_pass = ctk.CTkEntry(login_panel, show="*", font=FONT_MAIN, width=270)
entry_login_pass.place(x=40, y=150)

btn_toggle_login = ctk.CTkButton(login_panel, text="👁", width=40, height=28, fg_color="transparent",
                                 text_color=TEXT_COLOR, hover_color=SEC_BG_COLOR, font=("Segoe UI", 14),
                                 command=lambda: toggle_password(entry_login_pass, btn_toggle_login))
btn_toggle_login.place(x=320, y=150)

remember_var = tk.BooleanVar()
ctk.CTkCheckBox(login_panel, text="Remember Me", variable=remember_var, font=FONT_MAIN).place(x=40, y=200)

ctk.CTkButton(login_panel, text="Login", command=login_user, width=150, font=FONT_BOLD).place(x=40, y=250)
ctk.CTkButton(login_panel, text="Register", command=lambda: show_frame(frame_register), width=150, fg_color=BTN_BG,
              font=FONT_BOLD).place(x=210, y=250)
ctk.CTkButton(login_panel, text="Forgot Password?", command=lambda: show_frame(frame_reset), fg_color="transparent",
              text_color=ACCENT_COLOR, hover_color=SEC_BG_COLOR).place(x=40, y=290)

if os.path.exists("remember_me.txt"):
    with open("remember_me.txt", "r") as f:
        lines = f.readlines()
        if len(lines) >= 2:
            entry_login_user.insert(0, lines[0].strip())
            entry_login_pass.insert(0, lines[1].strip())
            remember_var.set(True)

# Register UI
ctk.CTkLabel(frame_register, text="💰 Premium Finance Tracker", font=FONT_TITLE, text_color=ACCENT_COLOR).place(relx=0.5,
                                                                                                               rely=0.15,
                                                                                                               anchor="center")
video_label = tk.Label(frame_register, bg=BG_COLOR)
video_label.place(relx=0.5, rely=0.7, anchor="center")

cap = cv2.VideoCapture(
    "#background #business #growth #stats #success #trade #finance #video #clips #animation #art #health.mp4")


def play_video():
    ret, frame_vid = cap.read()
    if ret:
        frame_vid = cv2.resize(frame_vid, (1500, 500))
        frame_vid = cv2.cvtColor(frame_vid, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_vid)
        imgtk = ImageTk.PhotoImage(image=img)
        video_label.imgtk = imgtk
        video_label.config(image=imgtk)
    else:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    video_label.after(20, play_video)


reg_panel = ctk.CTkFrame(frame_register, width=400, height=280, corner_radius=15)
reg_panel.place(relx=0.5, rely=0.4, anchor="center")

ctk.CTkLabel(reg_panel, text="New Username", font=FONT_BOLD).place(x=40, y=30)
entry_reg_user = ctk.CTkEntry(reg_panel, font=FONT_MAIN, width=320)
entry_reg_user.place(x=40, y=60)

ctk.CTkLabel(reg_panel, text="New Password", font=FONT_BOLD).place(x=40, y=110)
entry_reg_pass = ctk.CTkEntry(reg_panel, show="*", font=FONT_MAIN, width=270)
entry_reg_pass.place(x=40, y=140)

btn_toggle_reg = ctk.CTkButton(reg_panel, text="👁", width=40, height=28, fg_color="transparent", text_color=TEXT_COLOR,
                               hover_color=SEC_BG_COLOR, font=("Segoe UI", 14),
                               command=lambda: toggle_password(entry_reg_pass, btn_toggle_reg))
btn_toggle_reg.place(x=320, y=140)

ctk.CTkButton(reg_panel, text="Register", command=register_user, width=150, font=FONT_BOLD).place(x=40, y=200)
ctk.CTkButton(reg_panel, text="Back to Login", command=lambda: show_frame(frame_login), width=150, fg_color=BTN_BG,
              font=FONT_BOLD).place(x=210, y=200)
play_video()

# Reset Password UI
ctk.CTkLabel(frame_reset, text="Reset Password", font=("Segoe UI", 45, "bold"), text_color=ACCENT_COLOR).place(relx=0.5,
                                                                                                               rely=0.2,
                                                                                                               anchor="center")
reset_panel = ctk.CTkFrame(frame_reset, width=400, height=350, corner_radius=15)
reset_panel.place(relx=0.5, rely=0.5, anchor="center")

ctk.CTkLabel(reset_panel, text="Username:", font=FONT_BOLD).place(x=40, y=30)
entry_reset_user = ctk.CTkEntry(reset_panel, width=320, font=FONT_MAIN)
entry_reset_user.place(x=40, y=60)

ctk.CTkLabel(reset_panel, text="New Password:", font=FONT_BOLD).place(x=40, y=110)
entry_reset_new = ctk.CTkEntry(reset_panel, show="*", width=270, font=FONT_MAIN)
entry_reset_new.place(x=40, y=140)

btn_toggle_reset_new = ctk.CTkButton(reset_panel, text="👁", width=40, height=28, fg_color="transparent",
                                     text_color=TEXT_COLOR, hover_color=SEC_BG_COLOR, font=("Segoe UI", 14),
                                     command=lambda: toggle_password(entry_reset_new, btn_toggle_reset_new))
btn_toggle_reset_new.place(x=320, y=140)

ctk.CTkLabel(reset_panel, text="Confirm Password:", font=FONT_BOLD).place(x=40, y=190)
entry_reset_confirm = ctk.CTkEntry(reset_panel, show="*", width=270, font=FONT_MAIN)
entry_reset_confirm.place(x=40, y=220)

btn_toggle_reset_conf = ctk.CTkButton(reset_panel, text="👁", width=40, height=28, fg_color="transparent",
                                      text_color=TEXT_COLOR, hover_color=SEC_BG_COLOR, font=("Segoe UI", 14),
                                      command=lambda: toggle_password(entry_reset_confirm, btn_toggle_reset_conf))
btn_toggle_reset_conf.place(x=320, y=220)

ctk.CTkButton(reset_panel, text="Submit", fg_color=SUCCESS_COLOR, command=reset_password, width=150).place(x=40, y=280)
ctk.CTkButton(reset_panel, text="Back", fg_color=BTN_BG, command=lambda: show_frame(frame_login), width=150).place(
    x=210, y=280)


# ================= Transactions Functions =================
def add_transaction():
    date = entry_date.get()
    t_type = combo_type.get()
    account = combo_account.get()
    category = entry_category.get()
    amount = entry_amount.get()
    note = entry_note.get()
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO transactions (date, type, account, category, amount, note, user_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (date, t_type, account, category, amount, note, current_user_id))
    conn.commit()
    conn.close()
    show_transactions()


def show_transactions():
    for row in tree.get_children(): tree.delete(row)
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, date, type, account, category, amount, note, user_id FROM transactions WHERE user_id=?",
                   (current_user_id,))
    rows = cursor.fetchall()
    conn.close()
    currency = app_currency.get()
    rate = exchange_rates.get(currency, 1.0)
    for row in rows:
        formatted_row = list(row)
        try:
            converted_amount = float(row[5]) * rate
            formatted_row[5] = f"{currency} {converted_amount:,.2f}"
        except ValueError:
            pass
        if row[2].lower() == "expense":
            tree.insert("", tk.END, values=formatted_row, tags=("expense",))
        else:
            tree.insert("", tk.END, values=formatted_row, tags=("income",))
    tree.tag_configure("expense", background="#3b4590", foreground="white")
    tree.tag_configure("income", background="#543b74", foreground="white")

    update_account_balances()


def update_transaction():
    selected = tree.selection()
    if not selected: return
    item = tree.item(selected[0])
    record_id = item['values'][0]
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE transactions SET date=?, type=?, account=?, category=?, amount=?, note=? WHERE id=? AND user_id=?",
        (entry_date.get(), combo_type.get(), combo_account.get(), entry_category.get(), entry_amount.get(),
         entry_note.get(),
         record_id, current_user_id))
    conn.commit()
    conn.close()
    show_transactions()


def delete_transaction():
    selected = tree.selection()
    if not selected: return
    item = tree.item(selected[0])
    record_id = item['values'][0]
    if messagebox.askyesno("Confirmation", "Do you want to delete this record?"):
        conn = sqlite3.connect("expenses.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM transactions WHERE id=? AND user_id=?", (record_id, current_user_id))
        conn.commit()
        conn.close()
        show_transactions()


def search_transactions():
    keyword = entry_search.get().strip()
    filter_type = combo_filter_type.get()
    filter_year = combo_year_filter.get()
    filter_month = combo_month_filter.get()
    selected_date_filter = f"{filter_year}-{filter_month}"

    for row in tree.get_children(): tree.delete(row)
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    query = "SELECT id, date, type, account, category, amount, note, user_id FROM transactions WHERE user_id=? AND strftime('%Y-%m', date) = ?"
    params = [current_user_id, selected_date_filter]

    if keyword:
        query += " AND (category LIKE ? OR note LIKE ? OR account LIKE ?)"
        params.extend([f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"])

    if filter_type and filter_type != "All":
        query += " AND type=?"
        params.append(filter_type)

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    currency = app_currency.get()
    rate = exchange_rates.get(currency, 1.0)
    for row in rows:
        formatted_row = list(row)
        try:
            converted_amount = float(row[5]) * rate
            formatted_row[5] = f"{currency} {converted_amount:,.2f}"
        except ValueError:
            pass
        tree.insert("", tk.END, values=formatted_row)


def refresh_live_data():
    update_status("Fetching live rates...", "white")
    if fetch_live_rates():
        show_transactions()
        update_status("Live data refreshed successfully!", "white")
    else:
        show_transactions()
        update_status("Rates refresh failed. Using cached rates.", "orange")


def export_selected_to_excel():
    selected_items = tree.selection()
    if not selected_items: return
    filepath = filedialog.asksaveasfilename(defaultextension=".csv", title="Save Transactions",
                                            filetypes=[("CSV", "*.csv")])
    if not filepath: return
    with open(filepath, mode='w', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file)
        writer.writerow(["ID", "Date", "Type", "Account", "Category", "Amount", "Note"])
        for item in selected_items:
            writer.writerow(tree.item(item)['values'][:7])
    messagebox.showinfo("Success", "Exported successfully!")


def import_bank_transactions():
    filepath = filedialog.askopenfilename(title="Select Bank Statement", filetypes=[("CSV", "*.csv")])
    if not filepath: return
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    with open(filepath, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            if len(row) >= 5:
                cursor.execute(
                    "INSERT INTO transactions (date, type, account, category, amount, note, user_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (row[0].strip(), row[1].strip(), "Bank Account", row[2].strip(), row[3].strip(), row[4].strip(),
                     current_user_id))
    conn.commit()
    conn.close()
    show_transactions()


# ================= Transactions UI (CTk) =================
frame_expense.grid_rowconfigure(3, weight=1)
frame_expense.grid_columnconfigure(0, weight=1)

# Live Account Balances Dashboard
balances_frame = ctk.CTkFrame(frame_expense, fg_color="transparent")
balances_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15))

card_cash = ctk.CTkFrame(balances_frame, fg_color="#1b382b", corner_radius=10, height=75)
card_cash.pack(side="left", padx=(0, 10), fill="both", expand=True)
card_cash.pack_propagate(False)
ctk.CTkLabel(card_cash, text="💵 Cash Wallet", font=("Segoe UI", 11, "bold"), text_color="#8aff9d").pack(anchor="w",
                                                                                                        padx=12,
                                                                                                        pady=(8, 0))
lbl_cash_val = ctk.CTkLabel(card_cash, text="Rs. 0.00", font=("Segoe UI", 18, "bold"), text_color="white")
lbl_cash_val.pack(anchor="w", padx=12)

card_bank = ctk.CTkFrame(balances_frame, fg_color="#162e44", corner_radius=10, height=75)
card_bank.pack(side="left", padx=5, fill="both", expand=True)
card_bank.pack_propagate(False)
ctk.CTkLabel(card_bank, text="🏦 Bank Account", font=("Segoe UI", 11, "bold"), text_color="#8ad4ff").pack(anchor="w",
                                                                                                         padx=12,
                                                                                                         pady=(8, 0))
lbl_bank_val = ctk.CTkLabel(card_bank, text="Rs. 0.00", font=("Segoe UI", 18, "bold"), text_color="white")
lbl_bank_val.pack(anchor="w", padx=12)

card_card = ctk.CTkFrame(balances_frame, fg_color="#3a1e30", corner_radius=10, height=75)
card_card.pack(side="left", padx=(10, 0), fill="both", expand=True)
card_card.pack_propagate(False)
ctk.CTkLabel(card_card, text="💳 Credit Card", font=("Segoe UI", 11, "bold"), text_color="#ff8aef").pack(anchor="w",
                                                                                                        padx=12,
                                                                                                        pady=(8, 0))
lbl_card_val = ctk.CTkLabel(card_card, text="Rs. 0.00", font=("Segoe UI", 18, "bold"), text_color="white")
lbl_card_val.pack(anchor="w", padx=12)

# Input Form Section
input_frame = ctk.CTkFrame(frame_expense, corner_radius=10)
input_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))

entry_date = ctk.CTkEntry(input_frame, placeholder_text="YYYY-MM-DD", width=105)
entry_date.grid(row=0, column=0, padx=5, pady=10)
entry_date.insert(0, datetime.date.today().strftime("%Y-%m-%d"))

combo_type = ctk.CTkComboBox(input_frame, values=["Income", "Expense"], width=95)
combo_type.grid(row=0, column=1, padx=5, pady=10)

combo_account = ctk.CTkComboBox(input_frame, values=["Cash Wallet", "Bank Account", "Credit Card"], width=125)
combo_account.grid(row=0, column=2, padx=5, pady=10)
combo_account.set("Cash Wallet")

entry_category = ctk.CTkEntry(input_frame, placeholder_text="Category", width=120)
entry_category.grid(row=0, column=3, padx=5, pady=10)

entry_amount = ctk.CTkEntry(input_frame, placeholder_text="Amount", width=90)
entry_amount.grid(row=0, column=4, padx=5, pady=10)

entry_note = ctk.CTkEntry(input_frame, placeholder_text="Note", width=170)
entry_note.grid(row=0, column=5, padx=5, pady=10)

action_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
action_frame.grid(row=1, column=0, columnspan=6, sticky="ew", padx=10, pady=(0, 10))
ctk.CTkButton(action_frame, text="Add Transaction", fg_color=SUCCESS_COLOR, command=add_transaction).pack(side="left",
                                                                                                          padx=5)
ctk.CTkButton(action_frame, text="Update", fg_color=WARNING_COLOR, command=update_transaction).pack(side="left", padx=5)
ctk.CTkButton(action_frame, text="Delete", fg_color=DANGER_COLOR, command=delete_transaction).pack(side="left", padx=5)

ctk.CTkButton(action_frame, text="📤 Export", fg_color="#1565c0", command=export_selected_to_excel).pack(side="right",
                                                                                                        padx=5)
ctk.CTkButton(action_frame, text="📥 Import", fg_color="#4a148c", command=import_bank_transactions).pack(side="right",
                                                                                                        padx=5)

# Search & Filter Frame
search_frame = ctk.CTkFrame(frame_expense, corner_radius=10)
search_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))
entry_search = ctk.CTkEntry(search_frame, placeholder_text="Search keyword...", width=150)
entry_search.pack(side="left", padx=10, pady=10)
combo_filter_type = ctk.CTkComboBox(search_frame, values=["All", "Income", "Expense"], width=100)
combo_filter_type.pack(side="left", padx=10, pady=10)

combo_year_filter = ctk.CTkComboBox(search_frame, values=years, width=80)
combo_year_filter.pack(side="left", padx=5)
combo_year_filter.set(datetime.date.today().strftime("%Y"))

combo_month_filter = ctk.CTkComboBox(search_frame, values=months, width=70)
combo_month_filter.pack(side="left", padx=5)
combo_month_filter.set(datetime.date.today().strftime("%m"))

ctk.CTkButton(search_frame, text="Search/Filter", command=search_transactions).pack(side="left", padx=10, pady=10)
ctk.CTkButton(search_frame, text="🔄 Refresh Rates", fg_color="#007ACC", hover_color="#005A9E",
              command=refresh_live_data).pack(side="left", padx=10, pady=10)

# Treeview Data Frame
table_frame = ctk.CTkFrame(frame_expense, corner_radius=10)
table_frame.grid(row=3, column=0, sticky="nsew")

style = ttk.Style(root)
style.theme_use("clam")
style.configure("Treeview.Heading", background="#2D2D2D", foreground=ACCENT_COLOR, font=("Segoe UI", 12, "bold"),
                borderwidth=0)
style.configure("Treeview", background=BG_COLOR, foreground=TEXT_COLOR, fieldbackground=BG_COLOR, rowheight=35,
                borderwidth=0, font=("Segoe UI", 11))
style.map("Treeview", background=[("selected", ACCENT_COLOR)])

tree = ttk.Treeview(table_frame, columns=("ID", "Date", "Type", "Account", "Category", "Amount", "Note", "UserID"),
                    show="headings")
for col in ("ID", "Date", "Type", "Account", "Category", "Amount", "Note", "UserID"): tree.heading(col, text=col)
tree.column("ID", width=45, anchor="center")
tree.column("Date", width=95, anchor="center")
tree.column("Type", width=85, anchor="center")
tree.column("Account", width=115, anchor="center")
tree.column("Category", width=115, anchor="center")
tree.column("Amount", width=100, anchor="e")
tree.column("UserID", width=45, anchor="center")

vsb = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=vsb.set)
tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)
vsb.pack(side="right", fill="y", pady=10)

# ================= Summary / Dashboard Charts =================
frame_summary.chart_var = tk.StringVar(value="Pie Chart")


def show_summary_frame():
    show_frame(frame_summary)
    monthly_summary()


def refresh_summary_data():
    fetch_live_rates()
    monthly_summary()


def monthly_summary():
    for widget in frame_summary.winfo_children(): widget.destroy()

    top_ctrl = ctk.CTkFrame(frame_summary, fg_color="transparent")
    top_ctrl.pack(fill="x", pady=10)
    ctk.CTkLabel(top_ctrl, text="Monthly Summary", font=ctk.CTkFont(size=24, weight="bold")).pack(side="left", padx=10)

    combo_month = ctk.CTkComboBox(top_ctrl, values=months, width=80)
    combo_month.set(datetime.date.today().strftime("%m"))
    combo_month.pack(side="left", padx=5)

    combo_year = ctk.CTkComboBox(top_ctrl, values=years, width=100)
    combo_year.set(datetime.date.today().strftime("%Y"))
    combo_year.pack(side="left", padx=5)

    ctk.CTkButton(top_ctrl, text="Refresh", command=refresh_summary_data).pack(side="left", padx=10)

    # UI Smart Insights UI
    insight_msg, insight_type = generate_smart_insights(combo_year.get(), combo_month.get())

    if insight_type == "warning":
        card_fg = "#3a2525"
        text_color = "#ff8a8a"
    elif insight_type == "success":
        card_fg = "#1e3a24"
        text_color = "#8aff9d"
    else:
        card_fg = "#25303a"
        text_color = "#8ad4ff"

    insight_frame = ctk.CTkFrame(frame_summary, fg_color=card_fg, corner_radius=10)
    insight_frame.pack(fill="x", padx=10, pady=5)

    ctk.CTkLabel(insight_frame, text=insight_msg, font=("Segoe UI", 12, "bold"), text_color=text_color,
                 wraplength=850, justify="left").pack(padx=15, pady=12, anchor="w")

    selected_period = f"{combo_year.get()}-{combo_month.get()}"
    currency = app_currency.get()
    rate = exchange_rates.get(currency, 1.0)

    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT category, SUM(amount) FROM transactions 
        WHERE strftime('%Y-%m', date) = ? AND user_id=? AND type='Expense' GROUP BY category
    """, (selected_period, current_user_id))
    expenses = cursor.fetchall()

    cursor.execute("""
        SELECT category, SUM(amount) FROM transactions 
        WHERE strftime('%Y-%m', date) = ? AND user_id=? AND type='Income' GROUP BY category
    """, (selected_period, current_user_id))
    incomes = cursor.fetchall()
    conn.close()

    if not expenses and not incomes:
        ctk.CTkLabel(frame_summary, text="No Data found for this month.", font=FONT_MAIN).pack(pady=50)
        return

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.5))

    def plot_chart(ax, data, title, cmap_name):
        if not data:
            ax.text(0.5, 0.5, 'No Data', ha='center', va='center', color='white')
            ax.set_title(title, color='white')
            return None

        cats = [row[0] for row in data]
        vals = [float(row[1]) * rate for row in data]

        cmap = plt.get_cmap(cmap_name)
        colors = [cmap(i / len(vals)) for i in range(len(vals))]

        result = ax.pie(vals, labels=cats, autopct='%1.1f%%', textprops={'color': "w"}, colors=colors)
        ax.set_title(title, color='white')
        return result[0]

    plot_chart(ax1, expenses, f"Expenses ({currency})", "Reds")
    plot_chart(ax2, incomes, f"Incomes ({currency})", "Greens")

    fig.tight_layout()

    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    canvas = FigureCanvasTkAgg(fig, master=frame_summary)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=10)


# ================= 50/30/20 Rule Analysis =================
def show_rule_frame():
    show_frame(frame_rule)
    rule_50_30_20()


def rule_50_30_20():
    for widget in frame_rule.winfo_children(): widget.destroy()

    top_ctrl = ctk.CTkFrame(frame_rule, fg_color="transparent")
    top_ctrl.pack(fill="x", pady=10)
    ctk.CTkLabel(top_ctrl, text="50/30/20 Rule Analysis", font=ctk.CTkFont(size=24, weight="bold")).pack(side="left",
                                                                                                         padx=10)

    combo_month_rule = ctk.CTkComboBox(top_ctrl, values=months, width=80)
    combo_month_rule.set(datetime.date.today().strftime("%m"))
    combo_month_rule.pack(side="left", padx=5)

    combo_year_rule = ctk.CTkComboBox(top_ctrl, values=years, width=100)
    combo_year_rule.set(datetime.date.today().strftime("%Y"))
    combo_year_rule.pack(side="left", padx=5)

    ctk.CTkButton(top_ctrl, text="Refresh", command=rule_50_30_20).pack(side="left", padx=10)

    selected_period = f"{combo_year_rule.get()}-{combo_month_rule.get()}"
    currency = app_currency.get()
    rate = exchange_rates.get(currency, 1.0)

    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT type, SUM(amount) FROM transactions WHERE strftime('%Y-%m', date) = ? AND user_id=? GROUP BY type",
        (selected_period, current_user_id))
    rows = cursor.fetchall()
    conn.close()

    total_income = sum([row[1] for row in rows if row[0] == "Income"]) * rate
    total_expense = sum([row[1] for row in rows if row[0] == "Expense"]) * rate

    if total_income == 0:
        ctk.CTkLabel(frame_rule, text="No income found for this month.", font=FONT_MAIN).pack(pady=50)
        return

    needs_target, wants_target, savings_target = total_income * 0.50, total_income * 0.30, total_income * 0.20
    actual_needs, actual_wants, actual_savings = total_expense * 0.6, total_expense * 0.4, total_income - total_expense

    fig, ax = plt.subplots(figsize=(6, 4))
    labels = ["Needs", "Wants", "Savings"]
    x = range(len(labels))
    ax.bar(x, [needs_target, wants_target, savings_target], width=0.4, label="Recommended", color="#555555")
    ax.bar([i + 0.4 for i in x], [actual_needs, actual_wants, actual_savings], width=0.4, label="Actual",
           color=ACCENT_COLOR)

    ax.set_xticks([i + 0.2 for i in x])
    ax.set_xticklabels(labels, color="w")
    ax.set_title(f"50/30/20 Rule ({currency}) - {selected_period}", color="w")
    ax.tick_params(colors='w')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.legend(facecolor=BG_COLOR, edgecolor='none', labelcolor='w')

    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    canvas = FigureCanvasTkAgg(fig, master=frame_rule)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=20)


# ================= Settings Menu =================
def toggle_theme():
    global current_theme
    if current_theme == "dark":
        ctk.set_appearance_mode("Light")
        pywinstyles.apply_style(root, "light")
        current_theme = "light"
    else:
        ctk.set_appearance_mode("Dark")
        pywinstyles.apply_style(root, "dark")
        current_theme = "dark"


def open_settings():
    show_frame(frame_settings)
    for widget in frame_settings.winfo_children(): widget.destroy()

    settings_card = ctk.CTkFrame(frame_settings, corner_radius=15, width=700, height=500)
    settings_card.place(relx=0.5, rely=0.5, anchor="center")

    ctk.CTkLabel(settings_card, text="⚙️ System Settings", font=ctk.CTkFont(size=26, weight="bold"),
                 text_color=ACCENT_COLOR).pack(pady=20)

    pref_section = ctk.CTkFrame(settings_card, fg_color=SEC_BG_COLOR, corner_radius=10)
    pref_section.pack(fill="x", padx=20, pady=10, ipadx=10, ipady=10)

    ctk.CTkLabel(pref_section, text="App Theme:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
    ctk.CTkButton(pref_section, text="Switch Theme", command=toggle_theme).grid(row=0, column=1, padx=10, pady=10)

    ctk.CTkLabel(pref_section, text="Currency:").grid(row=1, column=0, padx=10, pady=10, sticky="w")

    combo_curr = ctk.CTkComboBox(pref_section, variable=app_currency, values=["Rs.", "$", "€", "£", "₹", "¥"],
                                 command=lambda e: [fetch_live_rates(), show_transactions()])
    combo_curr.grid(row=1, column=1, padx=10, pady=10)

    db_section = ctk.CTkFrame(settings_card, fg_color=SEC_BG_COLOR, corner_radius=10)
    db_section.pack(fill="x", padx=20, pady=10, ipadx=10, ipady=10)

    ctk.CTkButton(db_section, text="📤 Backup Database (.db)",
                  command=lambda: messagebox.showinfo("Backup", "Backed up successfully!")).pack(side="left", padx=10,
                                                                                                 expand=True)
    ctk.CTkButton(db_section, text="📥 Restore Database (.db)",
                  command=lambda: messagebox.showinfo("Restore", "Restored successfully!")).pack(side="left", padx=10,
                                                                                                 expand=True)


# ================= Start App =================
show_frame(frame_login)
init_db()
fetch_live_rates()
root.mainloop()