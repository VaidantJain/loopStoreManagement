from flask import Flask, jsonify, request
from pymongo import MongoClient
import uuid
from database import db
from reportGenerator import generate_report

app = Flask(__name__)

class ReportService:
    def __init__(self, db):
        self.db = db

    def trigger_report(self):
        report_id = str(uuid.uuid4())
        self.db.reports.insert_one({"report_id": report_id, "status": "Running"})
        generate_report(report_id)
        return report_id

    def get_report(self, report_id):
        report = self.db.reports.find_one({"report_id": report_id})
        if report['status'] == 'Running':
            return {"status": "Running"}
        return {"status": "Complete", "data": report['data']}


report_service = ReportService(db)

@app.route('/trigger_report', methods=['POST'])
def trigger_report():
    report_id = report_service.trigger_report()
    return jsonify({"report_id": report_id})

@app.route('/get_report', methods=['GET'])
def get_report():
    report_id = request.args.get('report_id')
    report = report_service.get_report(report_id)
    return jsonify(report)

if __name__ == '__main__':
    app.run(debug=True)
