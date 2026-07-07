# expert-doodle
A premium desktop Expense &amp; Income Tracker built with Python &amp; CustomTkinter. Features live currency rates, multi-account management, smart financial insights, 50/30/20 budget analysis, and automated recurring bills.

# 💰 Premium Finance Tracker

<img width="350" height="350" alt="money" src="https://github.com/user-attachments/assets/e5661a53-9cec-482a-83bc-462879044eb0" />

A sleek, feature-rich, and high-performance Desktop Personal Finance Management Application. Built with **Python**, **CustomTkinter**, and **SQLite3**, this application empowers users to manage their cash flow, track multiple accounts, analyze budgets via standard financial rules, and automate subscription tracking with a modern, production-grade User Interface.

---

## 🎨 UI/UX Architecture (The UI Side)

The visual interface is crafted to deliver a premium, fluid, and modern desktop experience, moving away from legacy Tkinter styles.

*   **CustomTkinter & Theme Engine:** Powered by `customtkinter` with full Dark and Light mode support. Dynamic color mapping ensures high contrast and accessibility.
*   **Cinematic Login/Registration Experience:** Integrated with **OpenCV (cv2)** and **Pillow (PIL)** to render a smooth, looping video background on the registration screen for a modern onboarding flow.
*   **Advanced Styling Integration:** Utilizes `pywinstyles` to inject native Windows styling tweaks, custom header integrations, and border smoothing.
*   **Dynamic Data Visualization:** Implements **Matplotlib** with custom dark-background configurations matching the application's core aesthetic, providing real-time responsive graphs.
*   **Clean Data Hierarchy:** Treeview elements customized via `tkinter.ttk` styles with color-coded transaction rows (differentiating income and expenses instantly).

---

## 🗄️ Database Architecture (The Backend & Storage)

The application relies on a local, lightweight, yet robust relational database model managed via **SQLite3**.

### Table Schemas:
1.  **`users`:** Manages secure authentication control.
    *   Fields: `id` (PK), `username` (Unique), `password`.
2.  **`transactions`:** Records every financial flow mapped to specific users and financial buckets.
    *   Fields: `id` (PK), `date`, `type` (Income/Expense), `category`, `amount`, `note`, `account` (Cash/Bank/Card), `user_id` (FK).
3.  **`recurring_bills`:** Houses automation templates for subscriptions.
    *   Fields: `id` (PK), `name`, `amount`, `category`, `account`, `due_date`, `user_id` (FK).
    *   <img width="1920" height="1020" alt="2026-07-07 (14)" src="https://github.com/user-attachments/assets/77d5eb72-db69-4049-baf0-098036aaf6d8" />


### Key Backend Mechanisms:
*   **Auto-Migration Engine:** Built-in schema verification that automatically alters older database versions without losing user data (e.g., automated execution of `ALTER TABLE` for backwards compatibility).
*   **Data Isolation:** Multi-user support with strict Foreign Key constraints ensuring users only visualize and modify their own financial logs.

---

## 🚀 Core Features & Advanced Capabilities

### 1. Multi-Account Balance Tracking
Dynamically distributes and calculates balances across three primary financial channels:
*   💵 Cash Wallet
*   🏦 Bank Account
*   💳 Credit Card
Any transaction added instantly updates the respective account's liquid capital display.

### 2. Live Currency Exchange Integration
Integrated with an online Exchange Rate API (`https://open.er-api.com`). Automatically converts and displays all data, accounts, and reports across global currencies ($ , €, £, ₹, ¥, Rs.) on the fly with a fallback to cached local rates during network timeouts.

### 3. Rule-Based Smart Financial Insights
An algorithmic recommendation engine that evaluates current monthly spending against previous periods:
*   Detects spikes in specific categories and triggers localized warnings.
*   Congratulates users on effective budgeting when expenses drop.

### 4. 50/30/20 Budgeting Analytics
Uses standard microeconomic principles to divide user income into **Needs (50%)**, **Wants (30%)**, and **Savings (20%)**. Matplotlib dynamically renders a comparison bar chart contrasting recommended financial distribution versus actual real-time spending.

### 5. Automated Subscription & Bill Manager
A background daemon triggers on user login to scan the database for due templates (e.g., Netflix, Internet bills):
*   Prompts user with a smart reminder modal.
*   Auto-logs transactions upon approval and mathematically increments the next billing date by exactly 1 calendar month.

### 6. Data Portability (Import/Export)
*   **Export:** Instantly flushes filtered transaction selections into standard UTF-8 encoded CSV sheets.
*   **Import:** Parses raw external bank transaction statements directly into the system database.

---

## 🛠️ Tech Stack & Dependencies

*   **Language:** Python 3.x
*   **GUI Framework:** CustomTkinter, Tkinter (Ttk)
*   **Database Engine:** SQLite3
*   **Data Analytics/Charts:** Matplotlib, NumPy
*   **Video & Image Processing:** OpenCV-Python (cv2), Pillow (PIL)
*   **Styling Tweaks:** pywinstyles, ctypes
*   **Networking/API:** urllib, json

---

## 🔧 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git](https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git)
   cd YOUR_REPO_NAME
