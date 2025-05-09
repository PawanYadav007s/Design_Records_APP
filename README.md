🛠️ Design Record Management System
This is a lightweight Flask-based offline web application for managing design records linked to purchase orders (POs). It allows admins to add PO entries and designers to fill in design record forms against them. The application supports viewing, searching, exporting, and generating reports.

📦 Features
Add PO records (Admin)

Assign and complete design records (Designers)

Filter and view all completed records

Search by PO number, project, client, or designer

Export all data to Excel (.xlsx)

Simple and responsive UI

🏗️ Tech Stack
Backend: Python 3.x, Flask

Database: SQLite (SQLAlchemy ORM)

Frontend: HTML, CSS (Bootstrap optionally)

Export: pandas

📁 Project Structure
csharp
Copy
Edit
project/
│
├── templates/               # HTML templates
│   ├── base.html
│   ├── dashboard.html
│   ├── add_po.html
│   ├── add_form.html
│   ├── view_all.html
│   └── search.html
│
├── models.py                # SQLAlchemy models
├── app.py                   # Main application file
├── requirements.txt         # Dependencies
├── records_export.xlsx      # (Generated on export)
└── .gitignore
🚀 Getting Started
1. Clone the repository:
bash
Copy
Edit
git clone https://github.com/yourusername/design-record-system.git
cd design-record-system
2. Set up a virtual environment (optional but recommended):
bash
Copy
Edit
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
3. Install dependencies:
bash
Copy
Edit
pip install -r requirements.txt
4. Run the application:
bash
Copy
Edit
python app.py
Visit http://127.0.0.1:5000 in your browser.

📑 Requirements
Python 3.7+

Flask

SQLAlchemy

pandas

Install via:

bash
Copy
Edit
pip install flask sqlalchemy pandas
📤 Exporting Data
Use the Export to Excel option on the dashboard to generate records_export.xlsx.

📄 License
MIT License – Free to use and modify.