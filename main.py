import sqlite3
from contextlib import closing

import pandas
from matplotlib import pyplot
from pandas import DataFrame

from database import Database


def test1():
    # OpticalLimits基準→2000がBetter、2500がGood、3000が限界っぽい
    # ePhotozine基準→154がFair、230がGood、306がExcellent

    mode = 'OpticalLimits'
    if mode == 'OpticalLimits':
        db_name = 'lens_data1.db'
        db_label = 'OpticalLimits'
        lens_id_list = (1, 2, 3, 4, 5)
        focal_list = (14, 25, 40, 60, 100, 140)
        f_value = -1
        graph_size = (800, 600)
        y_limit = 4000
    else:
        db_name = 'lens_data2.db'
        db_label = 'ePhotozine'
        lens_id_list = (1, 2, 3, 4)
        focal_list = (14, 25, 40, 60, 100, 140)
        f_value = -1
        graph_size = (800, 600)
        y_limit = 500

    print(f'データベース名：{db_name}')
    db = Database(db_name)
    print('レンズ一覧：')
    lens_list = db.get_lens_list()
    for lens_id in lens_id_list:
        print(f'・ID={lens_id} {lens_list[lens_id - 1]}')

    lens_count = len(lens_id_list)
    bar_plot_width = 1.0 / (lens_count + 1)
    for mode in ['center', 'edge']:
        print(f'{mode}を描画……')
        pyplot.figure(figsize=[graph_size[0] / 100.0, graph_size[1] / 100.0])
        pyplot.ylim([0, y_limit])
        for i, lens_id in enumerate(lens_id_list):
            x_list = [x + bar_plot_width * i for x in range(0, len(focal_list))]
            if mode == 'center':
                y_list = [db.get_center_score(lens_id, y, f_value) for y in focal_list]
            else:
                y_list = [db.get_edge_score(lens_id, y, f_value) for y in focal_list]
            data_label = lens_list[lens_id - 1]
            print(x_list)
            print(y_list)
            pyplot.bar(x_list, y_list, width=bar_plot_width, label=data_label, align='center')

        pyplot.legend(loc=2)
        pyplot.xticks(list(range(0, len(focal_list))), focal_list)
        if f_value < 0:
            title = f'{mode}-F0-{db_label}'
        else:
            title = f'{mode}-F{f_value}-{db_label}'
        pyplot.title(title)
        pyplot.savefig(f'output/{title}.png')
        pyplot.close()


def test2():
    mode = 'OpticalLimits'
    if mode == 'OpticalLimits':
        db_name = 'lens_data1.db'
        db_label = 'OpticalLimits'
        lens_id_list = (1, 2, 4, 3, 5)
        lens_color = ('red', 'brown', 'blue', 'lime', 'cyan')
        focal_range = (14, 140)
        f_value = -1
        graph_size = (800, 600)
        y_limit = 4000
    else:
        db_name = 'lens_data2.db'
        db_label = 'ePhotozine'
        lens_id_list = (1, 4, 2, 3)
        lens_color = ('magenta', 'red', 'brown', 'blue')
        focal_range = (14, 140)
        f_value = -1
        graph_size = (800, 600)
        y_limit = 500
    print(f'データベース名：{db_name}')
    db = Database(db_name)
    print('レンズ一覧：')
    lens_list = db.get_lens_list()
    for lens_id in lens_id_list:
        print(f'・ID={lens_id} {lens_list[lens_id - 1]}')

    lens_count = len(lens_id_list)
    for mode in ['center', 'edge']:
        print(f'{mode}を描画……')
        pyplot.figure(figsize=[graph_size[0] / 100.0, graph_size[1] / 100.0])
        pyplot.xlim([focal_range[0], focal_range[1]])
        pyplot.ylim([0, y_limit])
        for i, lens_id in enumerate(lens_id_list):
            def func(focal):
                if mode == 'center':
                    return db.get_center_score(lens_id, focal, f_value)
                else:
                    return db.get_edge_score(lens_id, focal, f_value)
            x_list = list(range(focal_range[0], focal_range[1] + 1))
            y_list = [func(x) for x in x_list]
            data_label = lens_list[lens_id - 1]
            pyplot.plot(x_list, y_list, label=data_label, c=lens_color[i])
            for f in db.get_just_focal_list(lens_id):
                pyplot.plot(f, func(f), marker='o', c=lens_color[i])
        pyplot.legend(loc=2)
        pyplot.xscale('log')
        if f_value < 0:
            title = f'{mode}-F0-{db_label}'
        else:
            title = f'{mode}-F{f_value}-{db_label}'
        pyplot.title(title)
        pyplot.savefig(f'output/{title}-2.png')
        pyplot.close()


def test3():
    # 各種設定
    mode = 'ePhotozine'
    if mode == 'OpticalLimits':
        db_name = 'lens_data1.db'
        db_label = 'OpticalLimits'
        focal_length_range = list(range(10, 140+1, 10))
        lens_color = {1: 'red', 2: 'brown', 3: 'blue', 4: 'lime', 5: 'cyan'}
        ylim = [0, 4000]
    else:
        db_name = 'lens_data2.db'
        db_label = 'ePhotozine'
        focal_length_range = list(range(10, 140 + 1, 10))
        lens_color = {1: 'red', 2: 'brown', 3: 'blue', 4: 'lime', 5: 'cyan'}
        ylim = [0, 600]

    # 生データを読み込む
    with closing(sqlite3.connect(db_name)) as conn:
        lens_name_df = pandas.read_sql('SELECT id, name FROM lens_name ORDER BY id', con=conn)
        lens_score_df = pandas.read_sql('SELECT lens_id, focal_length, f_value, center_score, edge_score'
                                        ' FROM lens_score', con=conn)

    # 各レンズにおける絞り開放のスコアを取得してmergeする
    merged_center_df = DataFrame()
    merged_edge_df = DataFrame()
    for lens_id, lens_name in zip(lens_name_df['id'], lens_name_df['name']):
        # 指定したレンズIDにおける焦点距離一覧を取得
        temp_df_1 = lens_score_df.query(f'lens_id=={lens_id}')
        focal_length_list = sorted(list(set(temp_df_1['focal_length'])))

        # 各焦点距離における絞り開放のスコアを取得
        center_score_list = []
        edge_score_list = []
        for focal_length in focal_length_list:
            # 指定した焦点距離におけるスコアを取得
            temp_df_2 = temp_df_1.query(f'focal_length=={focal_length}').sort_values('f_value')
            center_score = temp_df_2['center_score'].values[0]
            edge_score = temp_df_2['edge_score'].values[0]

            # リストに追加
            center_score_list.append({'focal_length': focal_length, f'{lens_id}': center_score})
            edge_score_list.append({'focal_length': focal_length, f'{lens_id}': edge_score})

        # DataFrame化して結合
        center_score_df = DataFrame.from_records(center_score_list)
        edge_score_df = DataFrame.from_records(edge_score_list)
        if len(merged_center_df) == 0:
            merged_center_df = center_score_df
        else:
            merged_center_df = merged_center_df.merge(right=center_score_df, on='focal_length', how='outer', sort=True)
        if len(merged_edge_df) == 0:
            merged_edge_df = edge_score_df
        else:
            merged_edge_df = merged_edge_df.merge(right=edge_score_df, on='focal_length', how='outer', sort=True)

    # 補間のため、別途作成した焦点距離一覧についてmergeする
    temp_df_3 = DataFrame()
    temp_df_3['focal_length'] = focal_length_range
    merged_center_df2 = merged_center_df.merge(temp_df_3, 'outer', 'focal_length').sort_values('focal_length')
    merged_edge_df2 = merged_edge_df.merge(temp_df_3, 'outer', 'focal_length').sort_values('focal_length')

    # 補間する。ただし、補間方向は「内挿」のみとする
    merged_center_df2.set_index('focal_length', inplace=True)
    merged_edge_df2.set_index('focal_length', inplace=True)
    merged_center_df2.interpolate(method='spline', order=2, limit_area='inside', inplace=True)
    merged_edge_df2.interpolate(method='spline', order=2, limit_area='inside', inplace=True)
    merged_center_df2.dropna(how='all', inplace=True)
    merged_edge_df2.dropna(how='all', inplace=True)

    # トリミングズームを再現するため、焦点距離が大きい方向に外挿する
    for lens_id in lens_name_df['id']:
        # 指定したレンズIDにおける最大焦点距離と、それに対応するスコアを確認する
        max_focal_length = max(merged_center_df[['focal_length', f'{lens_id}']].dropna()['focal_length'])
        center_score = merged_center_df.query(f'focal_length=={max_focal_length}')[f'{lens_id}'].values[0]
        edge_score = merged_edge_df.query(f'focal_length=={max_focal_length}')[f'{lens_id}'].values[0]

        # トリミングズームを再現しながら外挿する
        for focal_length in merged_center_df2.index:
            if focal_length > max_focal_length:
                merged_center_df2.loc[focal_length, f'{lens_id}'] = 1.0 * center_score * max_focal_length / focal_length
        for focal_length in merged_edge_df2.index:
            if focal_length > max_focal_length:
                merged_edge_df2.loc[focal_length, f'{lens_id}'] = 1.0 * edge_score * max_focal_length / focal_length

    # 可視化
    pyplot.figure(figsize=[8.0, 6.0])
    pyplot.ylim(ylim)
    pyplot.grid(which='major', color='black', linestyle='dashed')
    for lens_id, lens_name in zip(lens_name_df['id'], lens_name_df['name']):
        pyplot.plot(merged_center_df2.index, merged_center_df2[f'{lens_id}'], label=lens_name,
                    c=lens_color[lens_id])
        temp_df_4 = merged_center_df[['focal_length', f'{lens_id}']].dropna()
        for x, y in zip(temp_df_4['focal_length'], temp_df_4[f'{lens_id}']):
            pyplot.plot(x, y, marker='o', c=lens_color[lens_id])
    pyplot.legend(loc=2)
    pyplot.title(f'center-{db_label}')
    pyplot.savefig(f'output/center-{db_label}.png')
    pyplot.close()

    pyplot.figure(figsize=[8.0, 6.0])
    pyplot.ylim(ylim)
    pyplot.grid(which='major', color='black', linestyle='dashed')
    for lens_id, lens_name in zip(lens_name_df['id'], lens_name_df['name']):
        pyplot.plot(merged_edge_df2.index, merged_edge_df2[f'{lens_id}'], label=lens_name,
                    c=lens_color[lens_id])
        temp_df_4 = merged_edge_df[['focal_length', f'{lens_id}']].dropna()
        for x, y in zip(temp_df_4['focal_length'], temp_df_4[f'{lens_id}']):
            pyplot.plot(x, y, marker='o', c=lens_color[lens_id])
    pyplot.legend(loc=2)
    pyplot.title(f'edge-{db_label}')
    pyplot.savefig(f'output/edge-{db_label}.png')
    pyplot.close()


if __name__ == '__main__':
    # test1()
    # test2()
    test3()
