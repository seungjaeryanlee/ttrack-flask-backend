from flask import Flask
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
