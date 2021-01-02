from flask import Flask

import parser


app = Flask(__name__)


@app.route('/api/all/<date>')
def get_all_data(date):
    year, month, day = date.split("-")
    filepath = f"../../self-management/data/raw/{year}/{month}/{year}-{month}-{day}.txt"
    raw_lines = parser.get_raw_lines(filepath)
    duration_and_lines = parser.get_duration_and_lines(raw_lines)
    info_dict = parser.get_info_dict(duration_and_lines)

    return info_dict
