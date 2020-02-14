"""
def get_score_by_f(f_value: float, table: DataFrame) -> Optional[Tuple[float, float]]:
    # print(f'【get_score_by_f({f_value})】')
    # f値が負数のものについては、絞り開放での値だと判断する
    min_f = min(table['f_value'])
    if f_value < 0:
        return get_score_by_f(min_f, table)

    # f値が負数ではなく、かつ小さすぎるものについては計算不可とする
    if f_value < min_f:
        return None

    # ジャストなf値が存在する場合には、そのf値で判断する
    f_list = list(set(table['f_value']))
    if f_value in f_list:
        filtered_table = table.query(f'f_value=={f_value}')[['center_score', 'edge_score']]
        return filtered_table['center_score'].values[0], filtered_table['edge_score'].values[0]

    # 複数のスコアからの補間で判断する
    filtered_list = table[['f_value', 'center_score', 'edge_score']].to_dict(orient='records')
    filtered_list.append({'f_value': f_value, 'center_score': None, 'edge_score': None})
    filtered_table = DataFrame.from_records(filtered_list)
    filtered_table.sort_values('f_value', inplace=True)
    filtered_table.set_index('f_value', inplace=True)
    if len(filtered_table) > 4:
        filtered_table.interpolate(method='spline', order=3, inplace=True)
    else:
        filtered_table.interpolate(method='spline', order=2, inplace=True)
    filtered_table2 = filtered_table.query(f'f_value=={f_value}')[['center_score', 'edge_score']]
    return filtered_table2['center_score'].values[0], filtered_table2['edge_score'].values[0]


def get_score(lens_id: int, focal_length: int, f_value: float) -> Optional[Tuple[float, float]]:
    # print(f'【get_score{(lens_id, focal_length, f_value)}】')
    # DBに存在しないレンズについては計算不可とする
    filtered_df = lens_score_df.query(f'lens_id=={lens_id}')
    if len(filtered_df) == 0:
        return None

    # 焦点距離が短すぎるものについては計算不可とする
    min_focal = min(filtered_df['focal_length'])
    if focal_length < min_focal:
        return None

    # 焦点距離が長すぎるものについてはトリミングズームしたとする
    max_focal = max(filtered_df['focal_length'])
    if focal_length > max_focal:
        temp = get_score(lens_id, max_focal, f_value)
        if temp is None:
            return None
        ratio = 1.0 * max_focal / focal_length
        return temp[0] * ratio, temp[1] * ratio

    # ジャストな焦点距離が存在する場合には、その焦点距離で判断する
    focal_list = list(set(filtered_df['focal_length']))
    if focal_length in focal_list:
        filtered_df2 = filtered_df.query(f'focal_length=={focal_length}')
        return get_score_by_f(f_value, filtered_df2)

    # 複数のスコアからの補間で判断する
    score_list = [{'focal_length': focal_length, 'center_score': None, 'edge_score': None}]
    for fl in focal_list:
        score = get_score(lens_id, fl, f_value)
        if score is not None:
            score_list.append({
                'focal_length': fl,
                'center_score': score[0],
                'edge_score': score[1]
            })
    score_df = DataFrame.from_records(score_list)
    score_df.sort_values('focal_length', inplace=True)
    score_df.set_index('focal_length', inplace=True)
    if len(score_df) > 4:
        score_df.interpolate(method='spline', order=3, inplace=True)
    elif len(score_df) > 3:
        score_df.interpolate(method='spline', order=2, inplace=True)
    else:
        score_df.interpolate(method='index', inplace=True)
    filtered_score_df = score_df.query(f'focal_length=={focal_length}')[['center_score', 'edge_score']]
    return filtered_score_df['center_score'].values[0], filtered_score_df['edge_score'].values[0]


def main():
    lens_id_list = [1, 2, 3, 4, 5]
    focal_list = [14, 25, 40, 60, 100, 140]
    f_value = -1

    plot_width_per = 0.15
    figsize = [8, 6]
    ylim = 4000

    result_list = []
    for fl in focal_list:
        record = {'focal_length': fl}
        for lens_id in lens_id_list:
            record[f'center-{lens_id}'] = get_score(lens_id, fl, f_value)[0]
        for lens_id in lens_id_list:
            record[f'edge-{lens_id}'] = get_score(lens_id, fl, f_value)[1]
        result_list.append(record)
    result_df = DataFrame.from_records(result_list)
    pandas.options.display.width = 250
    pandas.options.display.max_columns = None
    print(result_df)

    pyplot.figure(figsize=figsize)
    pyplot.ylim([0, ylim])
    x_label = result_df['focal_length'].T
    for lens_id in lens_id_list:
        x_pos = [x + plot_width_per * (lens_id - 1) for x in list(range(0, len(result_df)))]
        data_label = get_lens_name(lens_id)
        pyplot.bar(x_pos, result_df[f'center-{lens_id}'], width=plot_width_per, label=data_label, align="center")

    pyplot.legend(loc=2)
    pyplot.xticks(list(range(0, len(result_df))), x_label)
    pyplot.title('center (OpticalLimits)')
    pyplot.savefig('output/center.png')
    pyplot.close()

    pyplot.figure(figsize=figsize)
    pyplot.ylim([0, ylim])
    x_label = result_df['focal_length'].T
    for lens_id in lens_id_list:
        x_pos = [x + plot_width_per * (lens_id - 1) for x in list(range(0, len(result_df)))]
        data_label = get_lens_name(lens_id)
        pyplot.bar(x_pos, result_df[f'edge-{lens_id}'], width=plot_width_per, label=data_label, align="center")

    pyplot.legend(loc=2)
    pyplot.xticks(list(range(0, len(result_df))), x_label)
    pyplot.title('edge (OpticalLimits)')
    pyplot.savefig('output/edge.png')
"""
from pprint import pprint

from database import Database

if __name__ == '__main__':
    db1 = Database('lens_data1.db')
    pprint(db1.get_lens_list())
    pprint(db1.get_center_score(1, 14, -1))
    pprint(db1.get_center_score(1, 50, -1))
    pprint(db1.get_center_score(1, 100, -1))
    # main()
