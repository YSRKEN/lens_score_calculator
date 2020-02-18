import sqlite3
from contextlib import closing

from flask import Flask, jsonify
from flask_cors import CORS

DB_PATH = 'lens_data.db'

app = Flask(__name__)
CORS(app)


@app.route('/')
def hello_world():
    return "Hello World!"


@app.route('/api/lenses')
def get_lens_list():
    """レンズの一覧を返す

    Returns
    -------
        {'id': integer, 'name': string, 'device': string}[]
    """
    lens_list = []
    with closing(sqlite3.connect(DB_PATH)) as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT id, name, device FROM lens_name ORDER BY id')
        for record in cursor.fetchall():
            lens_list.append({
                'id': record[0],
                'name': record[1],
                'device': record[2]
            })
        return jsonify(lens_list)


@app.route('/api/lenses/<lens_id>/<data_type>/<f_value_type>')
def get_lens_score(lens_id: str, data_type: str, f_value_type: str):
    """指定した条件で、レンズの焦点距離毎のスコアを返す

    Parameters
    ----------
    lens_id
        レンズID
    data_type
        "center"なら中央、"edge"なら周辺のスコア
    f_value_type
        負数なら最大値、0なら絞り解放、それ以外ならその値のもののみとする

    Returns
    -------
        {'focal': integer, 'score': integer}[]
    """

    f_value_type_float = float(f_value_type)
    if f_value_type_float > 0.0:
        # 指定した値をF値と見立て、その値のものから抽出する
        score_list = []
        with closing(sqlite3.connect(DB_PATH)) as connection:
            cursor = connection.cursor()
            cursor.execute(f'SELECT focal_length, MAX({data_type}_score) AS score FROM lens_score WHERE'
                           f' lens_id={lens_id} AND f_value = {f_value_type} GROUP BY focal_length')
            for record in cursor.fetchall():
                score_list.append({
                    'focal': record[0],
                    'score': record[1]
                })
        return jsonify(score_list)
    elif f_value_type_float == 0.0:
        # 絞り解放のものを抽出する
        score_list = []
        with closing(sqlite3.connect(DB_PATH)) as connection:
            cursor = connection.cursor()
            cursor.execute(f'SELECT focal_length, MIN(f_value), {data_type}_score AS score FROM lens_score WHERE'
                           f' lens_id={lens_id} GROUP BY focal_length')
            for record in cursor.fetchall():
                score_list.append({
                    'focal': record[0],
                    'score': record[2]
                })
        return jsonify(score_list)
    else:
        # 最大値のみ抽出する
        score_list = []
        with closing(sqlite3.connect(DB_PATH)) as connection:
            cursor = connection.cursor()
            cursor.execute(f'SELECT focal_length, MAX({data_type}_score) AS score FROM lens_score WHERE'
                           f' lens_id={lens_id} GROUP BY focal_length')
            for record in cursor.fetchall():
                score_list.append({
                    'focal': record[0],
                    'score': record[1]
                })
        return jsonify(score_list)


if __name__ == '__main__':
    app.run(debug=True)
