import pandas as pd
from pymongo import MongoClient
from datetime import datetime, timedelta
import pytz
from concurrent.futures import ThreadPoolExecutor
from utils import calculate_uptime_downtime, parse_timestamp
from database import db

class ReportGenerator:
    def __init__(self, db, report_id):
        self.db = db
        self.report_id = report_id

    def fetch_latest_timestamp(self):
        max_timestamp = self.db.storeStatus.find_one(sort=[("timestamp_utc", -1)])['timestamp_utc']
        return datetime.strptime(max_timestamp, '%Y-%m-%d %H:%M:%S.%f UTC').replace(tzinfo=pytz.utc)

    def prepare_report_data(self, current_time):
        report_data = []
        store_ids = self.db.storeStatus.distinct('store_id')

        for store_id in store_ids:
            uptime_last_hour, downtime_last_hour = calculate_uptime_downtime(
                store_id, current_time - timedelta(hours=1), current_time
            )
            uptime_last_day, downtime_last_day = calculate_uptime_downtime(
                store_id, current_time - timedelta(days=1), current_time
            )
            uptime_last_week, downtime_last_week = calculate_uptime_downtime(
                store_id, current_time - timedelta(weeks=1), current_time
            )

            report_data.append({
                "store_id": store_id,
                "uptime_last_hour": uptime_last_hour,
                "downtime_last_hour": downtime_last_hour,
                "uptime_last_day": uptime_last_day,
                "downtime_last_day": downtime_last_day,
                "uptime_last_week": uptime_last_week,
                "downtime_last_week": downtime_last_week
            })

        return report_data

    def save_report_to_csv(self, report_data):
        df = pd.DataFrame(report_data)
        report_file = f'templates/report_{self.report_id}.csv'
        df.to_csv(report_file, index=False)

    def save_report_to_db(self, report_data):
        self.db.reports.update_one(
            {"report_id": self.report_id}, {"$set": {"status": "Complete", "data": report_data}}
        )

    def generate(self):
        current_time = self.fetch_latest_timestamp()
        report_data = self.prepare_report_data(current_time)
        self.save_report_to_csv(report_data)
        self.save_report_to_db(report_data)

def generate_report(report_id):
    generator = ReportGenerator(db, report_id)
    print(f"GENERATING REPORT...")
    generator.generate()
