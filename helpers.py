import pandas as pd
from models import db, DesignRecord, PORecord
from flask import current_app
import json
import os

def export_all_data_to_excel():
    with open('settings.json') as f:
        settings = json.load(f)

    folder_path = settings['excel_save_path']
    os.makedirs(folder_path, exist_ok=True)
    filepath = os.path.join(folder_path, 'design_records.xlsx')

    records = DesignRecord.query.all()
    data = []

    for record in records:
        po = PORecord.query.get(record.po_id)
        data.append({
            'PO Number': po.po_number,
            'Quotation Number': po.quotation_number,
            'PO Date': po.po_date,
            'Client Name': po.client_company_name,
            'Project Name': po.project_name,
            'Designer Name': record.designer_name,
            'Design Location': record.design_location,
            'Reference Design Location': record.reference_design_location,
            'Design Release Date': record.design_release_date,
        })

    df = pd.DataFrame(data)
    df.to_excel(filepath, index=False)
