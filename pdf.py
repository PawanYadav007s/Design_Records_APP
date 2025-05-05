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