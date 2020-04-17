import codecs
import json
import re
import sqlite3
from contextlib import closing
from pprint import pprint
from typing import List, Dict, Union

from flask import Flask, jsonify, request, render_template, send_from_directory
from flask_cors import CORS
from requests_html import HTMLSession, HTML, Element

DB_PATH = 'lens_data.db'

app = Flask(__name__)
CORS(app)
session = HTMLSession()


@app.route('/')
def index():
    return render_template('index.html')


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
                           f' lens_id={lens_id} AND f_value <= {f_value_type} GROUP BY focal_length')
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


def get_pre_scores_impl(lens_id: str):
    page = session.get(f'https://www.opticallimits.com/m43/{lens_id}?start=1')
    html: HTML = page.html

    title = html.find('td.contentheading', first=True).text\
        .replace(' - Review / Lens Test Report - Analysis', '')\
        .replace(' - Review / Test Report - Analysis', '')\
        .replace(' - Review / Lens Test - Analysis', '')\
        .replace(' Review / Test Report - Analysis', '')\
        .replace(' - Analysis', '')\
        .replace(' - Review / Test - Analysis', '')\
        .replace(' - Review / Test', '')

    m = re.search(r'loadCharts\((\d+)\);', page.text)
    if m is None:
        return {'result': 'ok', 'type': 'image', 'title': title, 'data': []}
    lens_id_inner = m.group(1)
    page2 = session.post(f'https://www.opticallimits.com/js/php/get_data.php', data={
        'lens_id': lens_id_inner
    })
    resp: Dict[str, any] = json.loads(page2.text.encode().decode('utf-8-sig'))
    response_json = ({'result': 'ok', 'type': 'text', 'title': title, 'data': []})
    for focal_length, data in resp.items():
        data: Dict[str, List[any]] = data
        if 'mtf_val_extreme' in data:
            center_data: List[int] = data['mtf_val_center']
            edge_data: List[int] = data['mtf_val_extreme']
        else:
            center_data: List[int] = data['mtf_val_center']
            edge_data: List[int] = data['mtf_val_border']
        f_value_list: List[str] = [re.sub('-.*', '', x.replace('F/', '').replace('f/', '').replace('f', '')) for x in data['mtf_cat']]
        for f_value, center_score, edge_score in zip(f_value_list, center_data, edge_data):
            response_json['data'].append({
                'focal': focal_length,
                'f': f_value,
                'center': center_score,
                'edge': edge_score
            })
    return response_json


@app.route('/api/lenses/<lens_id>/pre')
def get_pre_scores(lens_id: str):

    page = session.get(f'https://www.opticallimits.com/m43/{lens_id}?start=1')
    if not page.ok:
        return jsonify({'result': 'ng'})
    html: HTML = page.html

    title = html.find('td.contentheading', first=True).text\
        .replace(' - Review / Lens Test Report - Analysis', '')\
        .replace(' - Review / Test Report - Analysis', '')

    img_list: List[Element] = html.find('img')
    for img_tag in img_list:
        url = 'https://www.opticallimits.com' + img_tag.attrs['src']
        if 'mtf.png' in url:
            return jsonify({'result': 'ok', 'type': 'image', 'title': title, 'data': url})

    response_json = get_pre_scores_impl(lens_id)

    return jsonify(response_json)


@app.route('/api/lenses/<lens_id>', methods=['POST'])
def post_lens_score(lens_id: str):
    lens_data = get_pre_scores_impl(lens_id)
    lens_id_int = int(lens_id)
    lens_name = lens_data['title']
    post_data = request.json
    lens_device = post_data['device']

    if 'data' in post_data:
        record_data = post_data['data']
    else:
        record_data = [{
            'focal': float(x['focal']),
            'f': float(x['f']),
            'center': x['center'],
            'edge': x['edge'],
        } for x in lens_data['data']]

    print(lens_data)
    print(post_data)
    with closing(sqlite3.connect(DB_PATH)) as connection:
        cursor = connection.cursor()
        sql = 'insert into lens_name (id, name, device) values (?,?,?)'
        lens_name = (lens_id_int, lens_name, lens_device)
        cursor.execute(sql, lens_name)
        for record in record_data:
            record: Dict[str, Union[str, any]] = record
            sql = 'insert into lens_score (lens_id, focal_length, f_value, center_score, edge_score) values (?,?,?,?,?)'
            lens_name = (lens_id_int, record['focal'], record['f'], record['center'], record['edge'])
            cursor.execute(sql, lens_name)
        connection.commit()
    return jsonify({})


@app.route("/<static_file>")
def manifest(static_file: str):
    return send_from_directory('./root', static_file)


if __name__ == '__main__':
    app.run(debug=True)
