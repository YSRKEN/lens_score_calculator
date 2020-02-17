from matplotlib import pyplot

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


if __name__ == '__main__':
    # test1()
    test2()
