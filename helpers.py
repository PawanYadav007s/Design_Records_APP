import pandas as pd
from models import db, DesignRecord, PORecord
import json
import os
import sys

def get_base_path():
    """Returns the base path depending on if app is frozen (compiled) or not."""
    return os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(__file__))

def load_settings():
    """Loads or creates default settings.json file for paths used in app."""
    base_path = get_base_path()
    settings_path = os.path.join(base_path, 'settings.json')
    default_settings = {
        "db_path": os.path.join(base_path, "design.db"),
        "excel_save_path": os.path.join(base_path, "ExcelBackup")
    }

    # Create settings file if it doesn't exist
    if not os.path.exists(settings_path):
        os.makedirs(default_settings["excel_save_path"], exist_ok=True)
        with open(settings_path, "w") as f:
            json.dump(default_settings, f, indent=4)

    with open(settings_path, "r") as f:
        settings = json.load(f)

    # Ensure Excel path exists
    os.makedirs(settings["excel_save_path"], exist_ok=True)
    return settings

def export_all_data_to_excel():
    """Exports all design records to an Excel file for backup."""
    try:
        settings = load_settings()
        filepath = os.path.join(settings['excel_save_path'], 'design_records.xlsx')

        records = DesignRecord.query.all()
        data = []
        for record in records:
            po = PORecord.query.get(record.po_id)
            if not po:
                continue
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

        pd.DataFrame(data).to_excel(filepath, index=False)
    except Exception as e:
        print(f"[ERROR] Failed to export Excel: {e}")
