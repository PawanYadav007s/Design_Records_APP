import sys
import json
import os
from flask import Flask, render_template, request, redirect, url_for, send_file
from models import db, PORecord, DesignRecord
from datetime import datetime
import pandas as pd
from helpers import export_all_data_to_excel  # if you’ve modularized it

from sqlalchemy.exc import IntegrityError
from flask import flash  # Add flash for user feedback



# from reportlab.lib.pagesizes import letter
# from reportlab.pdfgen import canvas


app = Flask(__name__)
# Determine correct base path
if getattr(sys, 'frozen', False):
    # Running as bundled executable
    base_path = sys._MEIPASS
else:
    # Running in normal script
    base_path = os.path.dirname(os.path.abspath(__file__))


# # --- Use shared folder location ---
# shared_folder = r"Z:\SharedDataFolder"  # Replace with actual shared path
# db_path = os.path.join(shared_folder, 'design.db')
db_path = os.path.join(base_path, 'design.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'Pawanyadav211191@!@#'
db.init_app(app)


# Enable WAL mode (best for multi-user access)
with app.app_context():
    from sqlalchemy import text
    db.session.execute(text('PRAGMA journal_mode=WAL;'))
    db.session.commit()



# Initialize the database and create tables if not exist
def create_tables():
    with app.app_context():
        db.create_all()
        export_all_data_to_excel()  # ✅ Only call this after tables exist

create_tables()



# Load configuration from settings.json


def load_settings():
    if getattr(sys, 'frozen', False):
        # Running from .exe, use the directory of the .exe file
        base_path = os.path.dirname(sys.executable)
    else:
        # Running from script
        base_path = os.path.dirname(os.path.abspath(__file__))

    settings_path = os.path.join(base_path, 'settings.json')

    # Default settings
    default_settings = {
        "excel_save_path": os.path.join(base_path, "ExcelBackup")
    }

    # Create settings.json if not exist
    if not os.path.exists(settings_path):
        os.makedirs(default_settings["excel_save_path"], exist_ok=True)
        with open(settings_path, "w") as f:
            json.dump(default_settings, f, indent=4)

    # Load and return
    with open(settings_path, "r") as f:
        return json.load(f)



settings = load_settings()


# Ensure database creation
create_tables()

@app.route('/')
def dashboard():
    pending_pos = PORecord.query.filter_by(design_status='pending').count()
    return render_template('dashboard.html', pending_pos=pending_pos)

@app.route('/add_po', methods=['GET', 'POST'])
def add_po():
    if request.method == 'POST':
        po_number = request.form['po_number']
        quotation_number = request.form['quotation_number']
        po_date = datetime.strptime(request.form['po_date'], '%Y-%m-%d').date()
        client_company_name = request.form['client_company_name']
        project_name = request.form['project_name']

        new_po = PORecord(
            po_number=po_number,
            quotation_number=quotation_number,
            po_date=po_date,
            client_company_name=client_company_name,
            project_name=project_name
        )

        try:
            db.session.add(new_po)
            db.session.commit()
            flash('PO Record added successfully!', 'success')
            return redirect(url_for('dashboard'))
        except IntegrityError:
            db.session.rollback()
            flash('PO Number already exists. Please use a unique PO Number.', 'danger')
            return redirect(url_for('add_po'))
        finally:
            db.session.close()
    return render_template('add_po.html')
@app.route('/add_form', methods=['GET', 'POST'])
def add_form():
    if request.method == 'POST':
        # Collect form data
        po_number = request.form['po_number']
        designer_name = request.form['designer_name']
        reference_design_location = request.form['reference_design_location']
        design_location = request.form['design_location']
        design_release_date = datetime.strptime(request.form['design_release_date'], '%Y-%m-%d').date()

        po_record = PORecord.query.filter_by(po_number=po_number).first()

        new_design = DesignRecord(
            designer_name=designer_name,
            reference_design_location=reference_design_location,
            design_location=design_location,
            design_release_date=design_release_date,
            po_record=po_record
        )

        db.session.add(new_design)
        po_record.design_status = 'completed'
        db.session.commit()

        # ✅ Export Excel after commit
        export_all_data_to_excel()

        return redirect(url_for('dashboard'))

    po_numbers = PORecord.query.filter_by(design_status='pending').all()
    return render_template('add_form.html', po_numbers=po_numbers)



@app.route('/view_all')
def view_all():
    records = db.session.query(DesignRecord, PORecord).join(PORecord).order_by(DesignRecord.id.desc()).all()
    return render_template('view_all.html', records=records)

@app.route('/search')
def search():
    query = request.args.get('query')
    records = []
    if query:
        records = db.session.query(DesignRecord, PORecord).join(PORecord).filter(
            (PORecord.po_number.ilike(f'%{query}%')) |
            (PORecord.project_name.ilike(f'%{query}%')) |
            (PORecord.client_company_name.ilike(f'%{query}%')) |
            (DesignRecord.designer_name.ilike(f'%{query}%'))
        ).all()
    return render_template('search.html', records=records, query=query)


@app.route('/edit/<int:record_id>', methods=['GET', 'POST'])
def edit_record(record_id):
    record = DesignRecord.query.get_or_404(record_id)
    if request.method == 'POST':
        record.designer_name = request.form['designer_name']
        record.reference_design_location = request.form['reference_design_location']
        record.design_location = request.form['design_location']
        record.design_release_date = datetime.strptime(request.form['design_release_date'], '%Y-%m-%d').date()
        db.session.commit()
        export_all_data_to_excel()

        return redirect(url_for('view_all'))
    return render_template('edit_record.html', record=record)

@app.route('/delete/<int:record_id>', methods=['GET'])
def delete_record(record_id):
    record = DesignRecord.query.get_or_404(record_id)
    db.session.delete(record)
    db.session.commit()
    export_all_data_to_excel()
    return redirect(url_for('view_all'))


@app.route('/export_excel')
def export_excel():
    try:
        # Fetch records from the database
        records = db.session.query(DesignRecord, PORecord).join(PORecord).all()
        data = []
        for record, po in records:
            data.append([
                len(data) + 1,
                po.po_number,
                po.po_date,
                po.project_name,
                po.client_company_name,
                record.designer_name,
                record.reference_design_location,
                record.design_location,
                record.design_release_date
            ])
        
        # Create DataFrame
        df = pd.DataFrame(data, columns=[
            'Sr.No', 'PO Number', 'PO Date', 'Project Name', 'Customer Name',
            'Designer Name', 'Reference Design', 'Design Location', 'Design Release Date'
        ])

        # Set save path
        directory = os.path.join(os.path.expanduser("~"), "Downloads")
        os.makedirs(directory, exist_ok=True)
        filename = f"design_records_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        filepath = os.path.join(directory, filename)

        # Save to file
        df.to_excel(filepath, index=False)

        # Try to serve file to browser (works in web browser, may fail in PyWebView)
        return send_file(filepath, as_attachment=True)

    except Exception as e:
        # Handle error and show message
        flash(f"Error exporting Excel file: {str(e)}")
        return redirect(url_for('dashboard'))




if __name__ == '__main__':
    create_tables()  # Ensure tables are created before running the app
    app.run(debug=True)
