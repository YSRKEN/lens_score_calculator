from matplotlib import pyplot

from database import Database

if __name__ == '__main__':
    db_name = 'lens_data1.db'
    db_label = 'OpticalLimits'
    lens_id_list = (1, 2, 3, 5)
    focal_list = (14, 25, 40, 60, 100, 140)
    f_value = -1
    graph_size = (800, 600)
    y_limit = 4000

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
                y_list = [db.get_center_score(lens_id, y, -1) for y in focal_list]
            else:
                y_list = [db.get_edge_score(lens_id, y, -1) for y in focal_list]
            data_label = lens_list[lens_id - 1]
            print(x_list)
            print(y_list)
            pyplot.bar(x_list, y_list, width=bar_plot_width, label=data_label, align='center')

        pyplot.legend(loc=2)
        pyplot.xticks(list(range(0, len(focal_list))), focal_list)
        pyplot.title(f'{mode} ({db_label})')
        pyplot.savefig(f'output/{mode}-{db_label}.png')
        pyplot.close()
