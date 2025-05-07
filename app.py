import os
from flask import Flask, render_template, request, redirect, url_for, send_file, flash
from models import db, PORecord, DesignRecord,Designer
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from helpers import export_all_data_to_excel, load_settings, get_base_path
import pandas as pd

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'Pawanyadav211191@!@#'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Set database path directly from base path
from helpers import get_base_path

db_path = os.path.join(get_base_path(), "design.db")
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
db.init_app(app)

# Enable WAL mode
with app.app_context():
    from sqlalchemy import text
    db.session.execute(text('PRAGMA journal_mode=WAL;'))
    db.session.commit()

def create_tables():
    """Creates DB tables and exports Excel snapshot on first run."""
    with app.app_context():
        db.create_all()
        export_all_data_to_excel()

# ✅ Call this to ensure DB + tables are created
create_tables()

# Routes follow


@app.route('/')
def dashboard():
    """Dashboard summary showing pending POs."""
    pending_pos = PORecord.query.filter_by(design_status='pending').count()
    return render_template('dashboard.html', pending_pos=pending_pos)

@app.route('/add_po', methods=['GET', 'POST'])
def add_po():
    """Route to add a new Purchase Order."""
    if request.method == 'POST':
        try:
            new_po = PORecord(
                po_number=request.form['po_number'],
                quotation_number=request.form['quotation_number'],
                po_date=datetime.strptime(request.form['po_date'], '%Y-%m-%d').date(),
                client_company_name=request.form['client_company_name'],
                project_name=request.form['project_name']
            )
            db.session.add(new_po)
            db.session.commit()
            flash('PO Record added successfully!', 'success')
        except IntegrityError:
            db.session.rollback()
            flash('PO Number already exists.', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
        finally:
            db.session.close()
        return redirect(url_for('dashboard'))
    return render_template('add_po.html')

@app.route('/add_form', methods=['GET', 'POST'])
def add_form():
    """Route for designers to fill form based on available POs and select designer from dropdown."""
    if request.method == 'POST':
        try:
            po_number = request.form['po_number']
            po_record = PORecord.query.filter_by(po_number=po_number).first()

            new_design = DesignRecord(
                designer_name=request.form['designer_name'],
                reference_design_location=request.form['reference_design_location'],
                design_location=request.form['design_location'],
                design_release_date=datetime.strptime(request.form['design_release_date'], '%Y-%m-%d').date(),
                po_record=po_record
            )
            db.session.add(new_design)
            po_record.design_status = 'completed'
            db.session.commit()
            export_all_data_to_excel()
        except Exception as e:
            db.session.rollback()
            flash(f"Error submitting form: {e}", 'danger')
        return redirect(url_for('dashboard'))

    po_numbers = PORecord.query.filter_by(design_status='pending').all()
    designers = Designer.query.order_by(Designer.name).all()
    return render_template('add_form.html', po_numbers=po_numbers, designers=designers)



@app.route('/designers', methods=['GET', 'POST'])
def manage_designers():
    if request.method == 'POST':
        name = request.form['designer_name'].strip()
        if name:
            existing = Designer.query.filter_by(name=name).first()
            if not existing:
                db.session.add(Designer(name=name))
                db.session.commit()
            else:
                flash("Designer already exists.", "warning")
        return redirect(url_for('manage_designers'))

    designers = Designer.query.order_by(Designer.name).all()
    return render_template('manage_designers.html', designers=designers)

@app.route('/delete_designer/<int:designer_id>', methods=['POST'])
def delete_designer(designer_id):
    designer = Designer.query.get_or_404(designer_id)
    db.session.delete(designer)
    db.session.commit()
    return redirect(url_for('manage_designers'))

@app.route('/edit_designer/<int:designer_id>', methods=['POST'])
def edit_designer(designer_id):
    designer = Designer.query.get_or_404(designer_id)
    new_name = request.form['new_name'].strip()
    if new_name:
        designer.name = new_name
        db.session.commit()
    return redirect(url_for('manage_designers'))




@app.route('/view_all')
def view_all():
    """Displays all design records."""
    records = db.session.query(DesignRecord, PORecord).join(PORecord).order_by(DesignRecord.id.desc()).all()
    return render_template('view_all.html', records=records)

@app.route('/search')
def search():
    """Search design records by multiple fields."""
    query = request.args.get('query', '')
    records = db.session.query(DesignRecord, PORecord).join(PORecord).filter(
        (PORecord.po_number.ilike(f'%{query}%')) |
        (PORecord.project_name.ilike(f'%{query}%')) |
        (PORecord.client_company_name.ilike(f'%{query}%')) |
        (DesignRecord.designer_name.ilike(f'%{query}%'))
    ).all() if query else []
    return render_template('search.html', records=records, query=query)

@app.route('/edit/<int:record_id>', methods=['GET', 'POST'])
def edit_record(record_id):
    """Edit a design record."""
    record = DesignRecord.query.get_or_404(record_id)
    if request.method == 'POST':
        try:
            record.designer_name = request.form['designer_name']
            record.reference_design_location = request.form['reference_design_location']
            record.design_location = request.form['design_location']
            record.design_release_date = datetime.strptime(request.form['design_release_date'], '%Y-%m-%d').date()
            db.session.commit()
            export_all_data_to_excel()
            flash('Record updated.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating record: {e}", 'danger')
        return redirect(url_for('view_all'))
    return render_template('edit_record.html', record=record)

@app.route('/delete/<int:record_id>')
def delete_record(record_id):
    """Delete a design record."""
    try:
        record = DesignRecord.query.get_or_404(record_id)
        db.session.delete(record)
        db.session.commit()
        export_all_data_to_excel()
        flash('Record deleted.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting record: {e}", 'danger')
    return redirect(url_for('view_all'))

@app.route('/export_excel')
def export_excel():
    """Download all design records as an Excel file."""
    try:
        records = db.session.query(DesignRecord, PORecord).join(PORecord).all()
        data = [[
            i+1,
            po.po_number,
            po.po_date,
            po.project_name,
            po.client_company_name,
            dr.designer_name,
            dr.reference_design_location,
            dr.design_location,
            dr.design_release_date
        ] for i, (dr, po) in enumerate(records)]

        df = pd.DataFrame(data, columns=[
            'Sr.No', 'PO Number', 'PO Date', 'Project Name', 'Customer Name',
            'Designer Name', 'Reference Design', 'Design Location', 'Design Release Date'
        ])

        filename = f"design_records_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        download_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        filepath = os.path.join(download_dir, filename)
        df.to_excel(filepath, index=False)

        return send_file(filepath, as_attachment=True)
    except Exception as e:
        flash(f"Error exporting Excel file: {str(e)}", 'danger')
        return redirect(url_for('dashboard'))

if __name__ == '__main__':
    create_tables()
    app.run(debug=True)
