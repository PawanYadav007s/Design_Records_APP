import pandas as pd
from models import db, DesignRecord, PORecord
from flask import current_app
import json
import os
import sys





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


def export_all_data_to_excel():
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
