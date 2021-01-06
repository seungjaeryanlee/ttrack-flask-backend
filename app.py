import os
from pathlib import Path

from flask import Flask, request
from flask_cors import CORS

import parser



app = Flask(__name__)
# TODO: Probably not needed when actually deployed?
CORS(app) 


@app.route('/api/all/<date>')
def get_all_data(date):
    year, month, day = date.split("-")
    filepath = f"ttrack-database/log/{year}/{month}/{year}-{month}-{day}.txt"
    raw_lines = parser.get_raw_lines(filepath)
    duration_and_lines = parser.get_duration_and_lines(raw_lines)
    info_dict = parser.get_info_dict(duration_and_lines)

    return info_dict


@app.route('/api/log/<date>')
def get_log(date):
    year, month, day = date.split("-")
    filepath = f"ttrack-database/log/{year}/{month}/{year}-{month}-{day}.txt"
    if Path(filepath).is_file():
        raw_lines = parser.get_raw_lines(filepath)
        return { "log": "\n".join(raw_lines) }
    else:
        return { "log" : "" }


@app.route('/api/log/save', methods=['PUT'])
def save_log():
    date = request.json["date"]
    log = request.json["log"]

    year, month, day = date.split("-")
    file_directory = f"ttrack-database/log/{year}/{month}"
    filepath = f"{file_directory}/{year}-{month}-{day}.txt"

    os.makedirs(file_directory, exist_ok=True)
    with open(filepath, "w") as f:
        f.write(log + "\n")

    return { "status": "success" }


@app.route('/api/rules/all')
def get_all_rules():
    task_to_label = {}
    for label, db_filename in parser.LABEL_TO_DB_FILES.items():
        with open('ttrack-database/parser_rules/{}'.format(db_filename), 'r') as f:
            for line in f.readlines():
                task = line.strip()
                if not task or task[0] == '#':
                    continue
                task_to_label[task] = label

    return task_to_label


@app.route('/api/rules/add', methods=['POST'])
def add_rule():
    task = request.json["task"]
    label = request.json["task_label"]
    db_filename = parser.LABEL_TO_DB_FILES[label]

    with open('ttrack-database/parser_rules/{}'.format(db_filename), 'a') as f:
        f.write(f"{task}\n")

    return { "status": "success" }
