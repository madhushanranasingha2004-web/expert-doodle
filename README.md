# 💰 Premium Finance Tracker

  <img width="200" height="200" alt="money" src="https://github.com/user-attachments/assets/e5661a53-9cec-482a-83bc-462879044eb0" />

A modern, high-performance Desktop Personal Finance Management Application built with **Python**, **CustomTkinter**, and **SQLite3**. Track cash flow, manage multiple accounts, automate subscriptions, and analyze budgets dynamically.

---

## 🚀 Core Features
* **Multi-Account Tracking:** Manage Cash, Bank, and Credit Card balances in real-time.
* **50/30/20 Budgeting:** Interactive Matplotlib charts comparing spending against financial rules.
* **Automated Bill Manager:** Smart reminders for recurring bills (subscriptions) with auto-logging.
* **Live Currency Exchange:** Live rates integration ($ , €, £, ₹, ¥, Rs.) via online API.
* **Smart Insights:** Algorithmic recommendation engine triggering expense warnings and tips.
* **Data Portability:** Quick CSV Import/Export for statements and transaction logs.

---

## 📸 Application Interface & UI Frames
*(Place your screen captures under each respective section below)*

### 🔐 1. Authentication Suite
* **Login Frame:** Secure access portal with credential verification, "Remember Me", and password toggle.
  <img width="1920" height="1020" alt="2026-07-07 (10)" src="https://github.com/user-attachments/assets/11bcf5d3-66b8-44e0-95e1-e9fe9cbf0094" />

* **Registration Frame:** Premium onboarding layout featuring a looping background video via OpenCV.
  <img width="1920" height="1020" alt="2026-07-07 (9)" src="https://github.com/user-attachments/assets/1d3456f3-1a46-4cf4-842c-df090082182c" />

* **Password Reset Frame:** Minimalist and secure account credential recovery pipeline.
  <img width="1920" height="1020" alt="2026-07-07 (7)" src="https://github.com/user-attachments/assets/e44acc30-d59e-435b-9b71-57462faa7d9e" />


### 📊 2. Dashboards & Analytics
* **Main Dashboard:** Live balance widgets, advanced CRUD transaction log, and a color-coded data grid.
  <img width="1920" height="1020" alt="2026-07-07 (11)" src="https://github.com/user-attachments/assets/20bdf768-4254-4778-8bc1-3e7ee6ab1e06" />

* **Monthly Summary:** Interactive Pie Charts for spending categories paired with localized trend alerts.
  <img width="1920" height="1020" alt="2026-07-07 (12)" src="https://github.com/user-attachments/assets/ea17b15c-e86c-422a-9e48-bd2d14e732b7" />

* **50/30/20 Analyzer:** Dynamic vertical bar charts separating Needs, Wants, and Savings.
  <img width="1920" height="1020" alt="2026-07-07 (13)" src="https://github.com/user-attachments/assets/221e81d3-3a05-4355-af32-2c975b1736a6" />


### ⚙️ 3. Automation & Controls
* **Recurring Bills Frame:** Control center for managing fixed utilities and recurring subscription templates.
  <img width="1920" height="1020" alt="2026-07-07 (14)" src="https://github.com/user-attachments/assets/517c1ede-995b-40e9-8245-b4bcc9ca3873" />

* **Settings Panel:** Seamless Light/Dark mode toggling, currency configuration, and manual database backup.
  <img width="1920" height="1020" alt="2026-07-07 (15)" src="https://github.com/user-attachments/assets/8b8c06a1-9d25-485f-a07a-e3dee7d33c30" />


---

## 🛠️ Tech Stack & Architecture

* **UI Framework:** `CustomTkinter` (Modern UI), `pywinstyles` (Native Windows styling).
* **Data & Charts:** `Matplotlib`, `NumPy` (Responsive dark-themed graphs).
* **Media Handling:** `OpenCV (cv2)`, `Pillow (PIL)` (Smooth video-based login backdrop).
* **Backend Storage:** `SQLite3` with an **Auto-Migration Engine** for schema updates and multi-user data isolation.

### Relational Database Schemas:
* **`users`:** `id` (PK) | `username` (Unique) | `password`
* **`transactions`:** `id` (PK) | `date` | `type` | `category` | `amount` | `note` | `account` | `user_id` (FK)
* **`recurring_bills`:** `id` (PK) | `name` | `amount` | `category` | `account` | `due_date` | `user_id` (FK)

---

## 🔧 Installation & Setup

```bash
# Clone the repository
git clone [https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git](https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git)
cd YOUR_REPO_NAME

# Install required packages (if applicable)
pip install customtkinter matplotlib pywinstyles opencv-python pillow

# Run the application
python main.py
