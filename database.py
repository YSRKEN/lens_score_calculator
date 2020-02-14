import sqlite3
from contextlib import closing
from typing import List, Optional

import numpy
import pandas
from pandas import DataFrame


class Database:
    def __init__(self, db_path: str):
        with closing(sqlite3.connect(db_path)) as conn:
            self.lens_name_df = pandas.read_sql('SELECT * FROM lens_name ORDER BY id', con=conn)
            self.lens_score_df = pandas.read_sql('SELECT * FROM lens_score', con=conn)

    def get_lens_list(self) -> List[str]:
        return list(self.lens_name_df['name'].values)

    @staticmethod
    def predict(x: float, x_list: numpy.ndarray, y_list: numpy.ndarray) -> float:
        # ヒットしたものについては、そのままの値を返す
        df = DataFrame()
        df['x'] = x_list
        df['y'] = y_list
        temp = df.query(f'x=={x}')
        if len(temp) >= 1:
            return temp['y'].values[0]

        # 補間した値を返す
        temp = df.to_dict(orient='records')
        temp.append({'x': x, 'y': None})
        df = DataFrame.from_records(temp).sort_values('x').set_index('x')
        if len(df) > 4:
            df.interpolate(method='spline', limit_direction='both', order=3, inplace=True)
        elif len(df) > 3:
            df.interpolate(method='spline', limit_direction='both', order=2, inplace=True)
        else:
            df.interpolate(method='index', inplace=True)
        temp = df.query(f'x=={x}')
        return temp['y'].values[0]

    @staticmethod
    def get_score_by_f_value(f_value: float, f_value_list: numpy.ndarray, score_list: numpy.ndarray) -> float:
        # F値が負数の時は、絞り開放だと判断する
        if f_value < 0:
            return Database.get_score_by_f_value(min(f_value_list), f_value_list, score_list)
        # 複数のスコアからの補間で判断する
        return Database.predict(f_value, f_value_list, score_list)

    def get_center_score(self, lens_id: int, focal_length: int, f_value: float) -> float:
        print(f'【get_center_score{(lens_id, focal_length, f_value)}】')
        # DBに存在しないレンズについては計算不可とする
        filtered_df = self.lens_score_df.query(f'lens_id=={lens_id}')
        if len(filtered_df) == 0:
            return 0.0
        # 焦点距離が短すぎるものについては計算不可とする
        if focal_length < min(filtered_df['focal_length']):
            return 0.0
        # 焦点距離が長すぎるものについてはトリミングズームしたとする
        max_focal = max(filtered_df['focal_length'])
        if focal_length > max_focal:
            return self.get_center_score(lens_id, max_focal, f_value) * max_focal / focal_length
        # 複数のスコアからの補間で判断する
        x_list = []
        y_list = []
        for x in set(filtered_df['focal_length'].values):
            temp = filtered_df.query(f'focal_length=={x}')
            score = Database.get_score_by_f_value(f_value, temp['f_value'].values, temp['center_score'].values)
            if score > 0.0:
                x_list.append(x)
                y_list.append(score)
        if len(x_list) == 0:
            return 0.0
        return Database.predict(focal_length, numpy.array(x_list), numpy.array(y_list))
