from flask import Flask, render_template, jsonify
import pandas as pd
import json

app = Flask(__name__)
app.config.from_object('config.Config')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_api_key', methods=['GET'])
def get_api_key():
    # API 키를 JSON 형태로 반환합니다.
    api_key = app.config['API_KEY']
    return jsonify({'api_key': api_key})

if __name__ == '__main__':
    app.run(debug=True)
