import csv
import os

# Define the field names
task_fields = ['task_id', 'chat_id', 'task_name', 'task_assignee', 'task_deadlines', 'task_remarks', 'status']
event_fields = ['event_id', 'event_name', 'event_start', 'event_end', 'event_remarks']

# Define data to be added or updated

csv_filepath_task = 'data/tasks.csv'
csv_filepath_event = 'data/events.csv'

mode = 'w'

# Open the CSV file
with open(csv_filepath_task, mode, newline='') as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=task_fields)

    # If writing a new file, write the header
    if mode == 'w':
        writer.writeheader()

with open(csv_filepath_event, mode, newline='') as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=event_fields)

    # If writing a new file, write the header
    if mode == 'w':
        writer.writeheader()

print("CSV file updated.")