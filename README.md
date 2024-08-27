# loopStoreManagement


## Overview

This project is designed to calculate and report the uptime and downtime of stores based on their operational hours and store status data. The calculations are performed for different time intervals, including the last hour, last day, and last week. The generated report is saved as a CSV file and stored in a MongoDB database.

## Features

- **Uptime/Downtime Calculation**: Calculates the uptime and downtime of stores for specific time intervals.
- **Customizable Timezones**: Supports different timezones for stores, ensuring accurate calculations based on local business hours.
- **Optimized with MongoDB Indexes**: MongoDB indexes are used on collections to optimize query performance, especially for large datasets.
- **Multithreading**: The report generation process can be optimized using multithreading for faster execution.

## Project Structure

- **`app.py`**: Flask application that provides endpoints to trigger report generation and retrieve report status.
- **`reportGenerator.py`**: Contains the `ReportGenerator` class responsible for generating the uptime/downtime report.
- **`uptimeCalculator.py`**: Contains classes and methods to calculate uptime and downtime based on store status and business hours.
- **`database.py`**: Handles the MongoDB database connection and initialization.

## How Uptime/Downtime is Calculated

### Key Concepts

- **Business Hours**: The hours during which a store is expected to be operational. These are stored in the `businessHours` collection.
- **Store Status**: The status of the store (`active` or `inactive`) at different timestamps, stored in the `storeStatus` collection.
- **Timezone**: Each store operates in a specific timezone, which is taken into account when calculating uptime/downtime.

### Calculation Process

1. **Fetching Latest Timestamp**:
   - The latest status timestamp is fetched from the `storeStatus` collection. This is used to determine the current time for calculations.

2. **Parsing Business Hours**:
   - Business hours for each store are retrieved from the `businessHours` collection. If no specific hours are found, the store is assumed to operate 24/7.

3. **Handling Timezones**:
   - The store's timezone is retrieved from the `timezones` collection. All business hours are converted to UTC for consistency in calculations.

4. **Calculating Uptime/Downtime**:
   - For each day in the specified interval, the code checks whether the store was within business hours and then evaluates the store's status (`active` or `inactive`).
   - The duration of each status is calculated and aggregated to determine the total uptime and downtime.

5. **Handling Edge Cases**:
   - The code handles cases where there are no business hours configured for a store or when there are gaps in the status data.

### Code Example

```python
# Example of calculating uptime/downtime for a store within a specific time range
start_time = datetime.now() - timedelta(days=1)
end_time = datetime.now()

uptime, downtime = calculate_uptime_downtime(store_id="store_123", start_time=start_time, end_time=end_time)

print(f"Uptime: {uptime} hours, Downtime: {downtime} hours")
