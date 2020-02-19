import codecs
import json
import re
import sqlite3
from contextlib import closing
from pprint import pprint
from typing import List, Dict

from flask import Flask, jsonify
from flask_cors import CORS
from requests_html import HTMLSession, HTML, Element

DB_PATH = 'lens_data.db'

app = Flask(__name__)
CORS(app)
session = HTMLSession()


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


@app.route('/api/lenses/<lens_id>/pre')
def get_pre_scores(lens_id: str):

    page = session.get(f'https://www.opticallimits.com/m43/{lens_id}?start=1')
    if not page.ok:
        return jsonify({'result': 'ng'})
    with open('temp.html', 'w', encoding='utf-8') as f:
        f.write(page.text)
    html: HTML = page.html

    img_list: List[Element] = html.find('img')
    for img_tag in img_list:
        url = 'https://www.opticallimits.com' + img_tag.attrs['src']
        if 'mtf.png' in url:
            return jsonify({'result': 'ok', 'type': 'image', 'data': url})

    m = re.search(r'loadCharts\((\d+)\);', page.text)
    lens_id_inner = m.group(1)
    page2 = session.post(f'https://www.opticallimits.com/js/php/get_data.php', data={
        'lens_id': lens_id_inner
    })
    if not page2.ok:
        return jsonify({'result': 'ng'})
    resp: Dict[str, any] = json.loads(page2.text.encode().decode('utf-8-sig'))
    responst_json = ({'result': 'ok', 'type': 'text', 'data': []})
    for focal_length, data in resp.items():
        data: Dict[str, List[any]] = data
        if 'mtf_val_extreme' in data:
            center_data: List[int] = data['mtf_val_center']
            edge_data: List[int] = data['mtf_val_extreme']
        else:
            center_data: List[int] = data['mtf_val_center']
            edge_data: List[int] = data['mtf_val_border']
        f_value_list: List[str] = [x.replace('F/', '') for x in data['ca_cat']]
        for f_value, center_score, edge_score in zip(f_value_list, center_data, edge_data):
            responst_json['data'].append({
                'focal': focal_length,
                'f': f_value,
                'center': center_score,
                'edge': edge_score
            })

    return jsonify(responst_json)


if __name__ == '__main__':
    app.run(debug=True)
