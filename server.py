"""data preprocess."""
import os
import argparse
import json
import re
import time
import numpy as np
import pandas as pd
from bottle import run, route, request, static_file, HTTPResponse
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
from renom.utility import interpolate
from const import DATA_DIR, INTERPOLATE_ITEMS
from settings import ENCODING
from storage import storage


def create_response(body):
    # httpのjsonレスポンスを作成する
    r = HTTPResponse(status=200, body=body)
    r.set_header('Content-Type', 'application/json')
    return r


def get_number_index_from_dataframe(data):
    # pandasデータフレームの数値データの列のインデックスを取得する
    return np.logical_or(data.dtypes == "float", data.dtypes == "int")


def request_list_to_np_array(data):
    # リクエストで受け取った文字列を配列に展開する
    return np.array(list(map(int, data.split(","))))


def get_file_name_from_id(file_id):
    # ファイルIDからファイル名を取得する
    return storage.fetch_file(file_id)['name']


def get_hist_from_npdata(number_index, data):
    # ヒストグラム用にNone値を削除した配列の配列を作成する
    hist_data = []
    for i, val in enumerate(number_index):
        if val:
            # 数値データのindexにはNone値を削除した配列を入れる
            d = data[:, i][~np.isnan(data[:, i])]
            hist_data.append(d.tolist())
        else:
            # 文字列データのindexには空の配列を入れる
            hist_data.append([])
    return hist_data


def get_time_from_npdata(number_index, data):
    # 数値データのインデックスの欠損部分をわかる形で取得する
    time_data = []
    for i, val in enumerate(number_index):
        if val:
            # 欠損部分は''で埋める
            d = ['' if np.isnan(d) else str(d) for d in data[:, i]]
            time_data.append(d)
        else:
            # テキストデータのインデックスには空の配列を入れる
            time_data.append([])
    return time_data


# 補間領域を取得
def get_interpolate_index(nan_index):
    interpolate_index = []

    # 欠損領域を取得する
    # 横方向で1カラム分取れるように転置する
    nan_index_t = np.array(nan_index.T)

    # 欠損領域をbooleanで取得する
    # 補間結果描画時に欠損領域の前後の時間も必要なので、前後にずらした行列の論理ORを取得する
    zeros = np.zeros([nan_index_t.shape[0], 1])
    a = np.concatenate([nan_index_t[:, 1:], zeros], axis=1) == 1
    b = np.concatenate([zeros, nan_index_t[:, :-1]], axis=1) == 1
    c = np.logical_or(nan_index_t, a)
    bool_interpolate_area = np.logical_or(b, c)

    # 欠損領域のインデックスを取得する
    indexes = np.where(bool_interpolate_area == 1)
    interpolate_index = [[] for i in range(nan_index_t.shape[0])]

    # 欠損部分のインデックスの配列を作成する
    s = []
    for i, v in enumerate(np.diff(indexes[1], n=1)):
        if v == 1:
            s.append(str(indexes[1][i]))
        else:
            s.append(str(indexes[1][i]))
            interpolate_index[indexes[0][i]].append(s)
            s = []

    if len(indexes[1]) > 0:
        s.append(str(indexes[1][-1]))
        interpolate_index[indexes[0][-1]].append(s)

    return interpolate_index


@route('/', method='GET')
def index():
    return static_file('index.html', root='js')


@route('/static/js/<file_name>')
def static_js(file_name):
    return static_file(file_name, root='js/static/js/')


@route('/static/css/<file_name>')
def static_css(file_name):
    return static_file(file_name, root='js/static/css/', mimetype='text/css')


@route('/static/fonts/<file_name>')
def static_fonts(file_name):
    return static_file(file_name, root='js/static/fonts/')


@route("/api/files", method="GET")
def load_files():
    try:
        files = storage.fetch_files()
        body = json.dumps({"files": files})
    except Exception as e:
        body = json.dumps({"error_msg": e.args[0]})
    r = create_response(body)
    return r


@route('/api/files/<file_id:int>', method='GET')
def load_file(file_id):
    try:
        # ファイルIDからファイル名を取得
        file_name = get_file_name_from_id(file_id)

        # ファイルを設定したエンコードで読み込む
        file_data = pd.read_csv(os.path.join(DATA_DIR, file_name), encoding=ENCODING)

        # ヘッダー
        data_header = file_data.columns

        # 数値データのカラムのインデックスを取得する
        number_index = get_number_index_from_dataframe(file_data)

        # 文字列データを取得
        text_data = file_data.loc[:, ~number_index]

        # 数値データを取得
        # 配列の大きさが変更されないように文字列データの部分は0で埋めておく
        number_data = np.array(file_data)
        number_data[:, ~number_index] = np.zeros(text_data.shape)
        number_data = number_data.astype('float')

        # ヒストグラム表示用のデータを作成
        hist_data = get_hist_from_npdata(number_index, number_data)

        # 時系列表示用のデータを作成
        time_data = get_time_from_npdata(number_index, number_data)

        # 欠損のインデックスを取得
        nan_index = file_data.isnull()

        # 補間領域のインデックスを取得
        interpolate_index = get_interpolate_index(nan_index)

        # 欠損の数と率を取得
        nan_count = nan_index.sum().astype(np.float)
        nan_ratio = (nan_count / file_data.shape[0]).astype(np.float)
        interpolate_list = np.zeros(nan_index.shape[1])

        # 統計量を取得
        data_mean = np.nanmean(number_data, axis=0)
        data_var = np.nanvar(number_data, axis=0)
        data_std = np.nanstd(number_data, axis=0)
        data_min = np.nanmin(number_data, axis=0)
        data_25percentile = np.nanpercentile(number_data, 25, axis=0)
        data_50percentile = np.nanpercentile(number_data, 50, axis=0)
        data_75percentile = np.nanpercentile(number_data, 75, axis=0)
        data_max = np.nanmax(number_data, axis=0)

        body = json.dumps({
            'row': file_data.shape[0],
            'columns': file_data.shape[1],
            'data_header': data_header.tolist(),
            'number_index': number_index.tolist(),
            'interpolate_index': interpolate_index,
            'hist_data': hist_data,
            'time_data': time_data,
            'data_mean': data_mean.tolist(),
            'data_var': data_var.tolist(),
            'data_std': data_std.tolist(),
            'data_min': data_min.tolist(),
            'data_25percentile': data_25percentile.tolist(),
            'data_50percentile': data_50percentile.tolist(),
            'data_75percentile': data_75percentile.tolist(),
            'data_max': data_max.tolist(),
            'nan_index': np.array(nan_index).T.tolist(),
            'nan_count': nan_count.tolist(),
            'nan_ratio': nan_ratio.tolist(),
            'interpolate_list': interpolate_list.tolist(),
        })
    except Exception as e:
        body = json.dumps({"error_msg": e.args[0]})
    r = create_response(body)
    return r


@route('/api/files/<file_id:int>/download', method='GET')
def download_file(file_id):
    try:
        file_name = get_file_name_from_id(file_id)
        # クライアントにファイルをダウンロードさせる
        return static_file(file_name, root=DATA_DIR, download=True)
    except Exception as e:
        body = json.dumps({"error_msg": e.args[0]})
        r = create_response(body)
        return r


@route('/api/files/<file_id:int>/export', method='POST')
def export_file(file_id):
    try:
        # ユーザが入力したファイル名を取得
        # .csvで終わっていなければ.csvを付ける
        out_file_name = request.params.out_file_name
        if not re.match(r'[a-zA-Z0-9]*.csv', out_file_name):
            out_file_name += '.csv'

        # 時系列表示をしているかどうか
        timeseries = int(request.params.timeseries)

        # 選択された列のインデックスのリストを取得
        select_index = request_list_to_np_array(request.params.select_index)

        # 補間方法の選択した項目のリストを取得
        interpolate_list = request_list_to_np_array(request.params.interpolate_list)

        # 選択した行のインデックスを取得
        row_range = request_list_to_np_array(request.params.row_range)

        # 選択したファイルを読み込み
        file_name = get_file_name_from_id(file_id)
        file_data = pd.read_csv(os.path.join(DATA_DIR, file_name))

        # 選択したデータを抽出
        select_file_data = file_data.iloc[:, select_index]

        # 選択したデータから数値データを抽出
        number_index = get_number_index_from_dataframe(select_file_data)
        number_columns = np.array(select_file_data.columns)[number_index]
        number_data = select_file_data.loc[:, number_index]

        # 補間を行う
        if timeseries == 1:
            # 時系列データの補間
            # 補間データを格納する行列を初期化
            output_data = np.zeros((file_data.shape[0], len(number_index[number_index])))

            # 補間手法でループ
            for (index, item) in enumerate(INTERPOLATE_ITEMS):
                loc = interpolate_list[select_index][number_index] == index

                if index == 0:
                    # 補間しないとき
                    d = number_data.loc[:, loc]
                else:
                    # 手法に応じて補間
                    d = interpolate(np.array(number_data.loc[:, loc]), mode=INTERPOLATE_ITEMS[index])

                # 補間結果を反映する
                output_data[:, loc] += d
        else:
            # 時系列じゃないときはなにもしない
            output_data = number_data

        # 文字列データを取得
        text_columns = np.array(select_file_data.columns)[~number_index]

        # 数値データと文字列データを連結
        columns = np.concatenate([number_columns, text_columns])
        output_data = np.concatenate([output_data, select_file_data.loc[:, ~number_index]], axis=1)

        # データフレームを作成して出力
        df = pd.DataFrame(output_data[row_range[0]:row_range[1]+1], columns=columns)
        output_file = os.path.join(DATA_DIR, out_file_name)
        df.to_csv(output_file, index=None)

        # watchdogが作成したデータをDBに反映するのを待つ
        time.sleep(0.5)
    except Exception as e:
        body = json.dumps({"error_msg": e.args[0]})
        ret = create_response(body)
        return ret


@route('/api/files/<file_id:int>/columns/<column_index:int>/interpolate',
       method='GET')
def interpolate_column(file_id, column_index):
    try:
        # カラム単位で補間する
        file_name = get_file_name_from_id(file_id)
        file_data = pd.read_csv(os.path.join(DATA_DIR, file_name), encoding=ENCODING)
        interpolate_method = int(request.query['interpolate_method'])

        data = np.array(file_data.iloc[:, column_index])
        nan_index = np.array(file_data.isnull())
        nan_index = nan_index[:, column_index].reshape(-1)

        # 補間後のヒストグラムと時系列データを作成
        if interpolate_method > 0:
            hist_data = interpolate(data, mode=INTERPOLATE_ITEMS[interpolate_method])
            time_data = hist_data
        else:
            hist_data = data[~nan_index]
            time_data = data

        time_data = ['' if np.isnan(d) else str(d) for d in time_data]

        body = json.dumps({
            'hist_data': hist_data.tolist(),
            'time_data': time_data,
        })
    except Exception as e:
        body = json.dumps({"error_msg": e.args[0]})
    ret = create_response(body)
    return ret


class DataFileEventHandler(PatternMatchingEventHandler):
    def on_created(self, event):
        # ファイルが作成されたら
        file_name = event.src_path.split('/')[-1]
        storage.register_file(file_name)

    def on_deleted(self, event):
        # ファイルが削除されたら
        file_name = event.src_path.split('/')[-1]
        storage.remove_file(file_name)


def init_db():
    files = os.listdir(DATA_DIR)
    files_in_db = storage.fetch_files()

    # DB内のファイルの名前のリスト
    name_list = []
    for i in files_in_db:
        name_list.append(files_in_db[i]['name'])

    # DBに登録されていないファイルがあれば登録
    for f in files:
        if not storage.exist_file(f):
            storage.register_file(f)

    # dataディレクトリから削除されたファイルがあればDBに反映
    diff_files = list(set(name_list) - set(files))
    for f in diff_files:
        storage.remove_file(f)


if __name__ == '__main__':
    # 引数でホストとポートを変更できる
    parser = argparse.ArgumentParser(description='desc')
    parser.add_argument('--host', default='0.0.0.0', help='Server address')
    parser.add_argument('--port', default='8090', help='Server port')
    args = parser.parse_args()

    # dataディレクトリの中身をDBに反映
    if not os.path.isdir(DATA_DIR):
        os.makedirs(DATA_DIR)
    init_db()

    # dataディレクトリの中をwatchして変更があったらDBを更新
    handler = DataFileEventHandler(patterns=['*.csv'])
    observer = Observer()
    observer.schedule(handler, DATA_DIR, recursive=False)
    observer.start()

    run(host=args.host, port=args.port, reloader=True)
    observer.stop()
    observer.join()
