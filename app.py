import json
import os
from flask import Flask, render_template, request, redirect, url_for, send_file
from models import db, PORecord, DesignRecord
from datetime import datetime
import pandas as pd
 


# from reportlab.lib.pagesizes import letter
# from reportlab.pdfgen import canvas


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///design.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Load configuration from settings.json
def load_settings():
    with open('settings.json', 'r') as f:
        return json.load(f)

settings = load_settings()

# Initialize the database and create tables if not exist
def create_tables():
    with app.app_context():
        db.create_all()

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

        new_po = PORecord(po_number=po_number, quotation_number=quotation_number, po_date=po_date,
                          client_company_name=client_company_name, project_name=project_name)

        db.session.add(new_po)
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('add_po.html')

@app.route('/add_form', methods=['GET', 'POST'])
def add_form():
    if request.method == 'POST':
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

@app.route('/export_excel')
def export_excel():
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
    
    df = pd.DataFrame(data, columns=['Sr.No', 'PO Number', 'PO Date', 'Project Name', 'Customer Name',
                                     'Designer Name', 'Reference Design', 'Design Location', 'Design Release Date'])

    # Use the path from settings.json
    filepath = settings["excel_save_path"]

    # Ensure the directory exists
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    df.to_excel(filepath, index=False)
    return send_file(filepath, as_attachment=True)


# @app.route('/download_pdf', methods=['GET'])
# def download_pdf():
#     search_term = request.args.get('query')
#     records = []

#     if search_term:
#         records = db.session.query(DesignRecord, PORecord).join(PORecord).filter(
#             (PORecord.po_number.like(f'%{search_term}%')) |
#             (PORecord.project_name.like(f'%{search_term}%')) |
#             (PORecord.client_company_name.like(f'%{search_term}%')) |
#             (DesignRecord.designer_name.like(f'%{search_term}%'))
#         ).all()

#     # Generate the PDF using ReportLab
#     pdf_filename = f"search_results_{search_term}.pdf"
#     pdf_filepath = os.path.join('temp', pdf_filename)
#     c = canvas.Canvas(pdf_filepath, pagesize=letter)
#     width, height = letter

#     c.setFont("Helvetica", 12)
#     c.drawString(100, height - 40, f"Search Term: {search_term}")
#     c.drawString(100, height - 60, "ID | PO Number | Designer Name | Description | Completion Date")

#     y_position = height - 80
#     for record, po in records:
#         c.drawString(100, y_position, f"{record.id} | {po.po_number} | {record.designer_name} | {record.design_description} | {record.completion_date}")
#         y_position -= 20

#     c.save()

#     return send_file(pdf_filepath, as_attachment=True, download_name=pdf_filename)

if __name__ == '__main__':
    create_tables()  # Ensure tables are created before running the app
    app.run(debug=True)
