from datetime import datetime, timedelta
from pytz import timezone
import pytz
from database import db

class TimestampParser:
    @staticmethod
    def parse(timestamp_str):
        try:
            return datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S.%f UTC').replace(tzinfo=pytz.utc)
        except ValueError:
            return datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S UTC').replace(tzinfo=pytz.utc)

class UptimeDowntimeCalculator:
    def __init__(self, db, store_id, start_time, end_time):
        self.db = db
        self.store_id = store_id
        self.start_time = start_time
        self.end_time = end_time
        self.uptime = 0
        self.downtime = 0

    def get_timezone(self):
        timezone_data = self.db.timezones.find_one({"store_id": self.store_id}) or {"timezone_str": "America/Chicago"}
        return timezone(timezone_data['timezone_str'])

    def get_business_hours(self):
        business_hours = list(self.db.businessHours.find({"store_id": self.store_id}))
        if not business_hours:
            business_hours = [{"day": i, "start_time_local": "00:00:00", "end_time_local": "23:59:59"} for i in range(7)]
        return business_hours

    def calculate(self):
        local_tz = self.get_timezone()
        business_hours = self.get_business_hours()
        duration_in_hours = (self.end_time - self.start_time).total_seconds() / 3600
        use_minutes = duration_in_hours <= 1

        current_time = self.start_time
        while current_time < self.end_time:
            current_day = current_time.weekday()
            hours_for_day = [bh for bh in business_hours if bh['day'] == current_day]

            if not hours_for_day:
                current_time += timedelta(days=1)
                continue

            for hours in hours_for_day:
                start_local = local_tz.localize(
                    datetime.combine(current_time.date(), datetime.strptime(hours['start_time_local'], '%H:%M:%S').time()))
                end_local = local_tz.localize(
                    datetime.combine(current_time.date(), datetime.strptime(hours['end_time_local'], '%H:%M:%S').time()))

                start_utc = start_local.astimezone(pytz.utc)
                end_utc = end_local.astimezone(pytz.utc)

                interval_start = max(start_utc, self.start_time)
                interval_end = min(end_utc, self.end_time)

                if interval_start >= interval_end:
                    continue

                statuses = list(self.db.storeStatus.find({
                    "store_id": self.store_id,
                    "timestamp_utc": {"$gte": interval_start.strftime('%Y-%m-%d %H:%M:%S.%f UTC'),
                                      "$lt": interval_end.strftime('%Y-%m-%d %H:%M:%S.%f UTC')}
                }).sort("timestamp_utc"))

                if not statuses:
                    continue

                for i in range(len(statuses) - 1):
                    status_start = TimestampParser.parse(statuses[i]['timestamp_utc'])
                    status_end = TimestampParser.parse(statuses[i + 1]['timestamp_utc'])

                    duration = (status_end - status_start).total_seconds() / (60 if use_minutes else 3600)

                    if statuses[i]['status'] == 'active':
                        self.uptime += duration
                    else:
                        self.downtime += duration

                last_status_time = TimestampParser.parse(statuses[-1]['timestamp_utc'])
                final_duration = (interval_end - last_status_time).total_seconds() / (60 if use_minutes else 3600)

                if statuses[-1]['status'] == 'active':
                    self.uptime += final_duration
                else:
                    self.downtime += final_duration

            current_time += timedelta(days=1)

        return self.uptime, self.downtime

def parse_timestamp(timestamp_str):
    return TimestampParser.parse(timestamp_str)

def calculate_uptime_downtime(store_id, start_time, end_time):
    calculator = UptimeDowntimeCalculator(db, store_id, start_time, end_time)
    return calculator.calculate()
