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
    r = HTTPResponse(status=200, body=body)
    r.set_header('Content-Type', 'application/json')
    return r


def get_number_index_from_dataframe(data):
    return np.logical_or(data.dtypes == "float", data.dtypes == "int")


def request_list_to_np_array(data):
    return np.array(list(map(int, data.split(","))))


def get_file_name_from_id(file_id):
    return storage.fetch_file(file_id)['name']


def get_hist_from_npdata(number_index, data):
    hist_data = []
    for i, val in enumerate(number_index):
        if val:
            d = data[:, i][~np.isnan(data[:, i])]
            hist_data.append(d.tolist())
        else:
            hist_data.append([])
    return hist_data


@route('/', method='GET')
def index():
    return static_file('index.html', root='.')


@route('/static/js/<file_name>')
def static_js(file_name):
    return static_file(file_name, root='static/js/')


@route('/static/css/<file_name>')
def static_css(file_name):
    return static_file(file_name, root='static/css/', mimetype='text/css')


@route('/static/fonts/<file_name>')
def static_fonts(file_name):
    return static_file(file_name, root='static/fonts/')


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
        file_name = get_file_name_from_id(file_id)
        file_data = pd.read_csv(os.path.join(DATA_DIR, file_name), encoding=ENCODING)

        data_header = file_data.columns

        number_index = get_number_index_from_dataframe(file_data)
        text_data = file_data.loc[:, ~number_index]
        number_data = np.array(file_data)
        number_data[:, ~number_index] = np.zeros(text_data.shape)
        number_data = number_data.astype('float')

        hist_data = get_hist_from_npdata(number_index, number_data)

        nan_index = file_data.isnull()
        nan_count = nan_index.sum().astype(np.float)
        nan_ratio = (nan_count / file_data.shape[0]).astype(np.float)
        interpolate_list = np.zeros(nan_index.shape[1])

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
            'hist_data': hist_data,
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


@route('/api/files/<file_id:int>/export', method='POST')
def export_file(file_id):
    try:
        out_file_name = request.params.out_file_name
        if not re.match(r'[a-zA-Z0-9]*.csv', out_file_name):
            out_file_name += '.csv'
        # timeseries flag
        timeseries = int(request.params.timeseries)
        # use data column index
        select_index = request_list_to_np_array(request.params.select_index)
        # interpolate methods
        interpolate_list = request_list_to_np_array(request.params.interpolate_list)
        # row range
        row_range = request_list_to_np_array(request.params.row_range)

        # load src file data
        file_name = get_file_name_from_id(file_id)
        file_data = pd.read_csv(os.path.join(DATA_DIR, file_name))

        # selected data
        select_file_data = file_data.iloc[:, select_index]

        # number data index of selected data
        number_index = get_number_index_from_dataframe(select_file_data)
        number_columns = np.array(select_file_data.columns)[number_index]
        number_data = select_file_data.loc[:, number_index]

        # timeseries interpolation
        if timeseries == 1:
            # interpolate number data
            output_data = np.zeros((file_data.shape[0], len(number_index[number_index])))

            for (index, item) in enumerate(INTERPOLATE_ITEMS):
                loc = interpolate_list[select_index][number_index] == index

                if index == 0:
                    d = number_data.loc[:, loc]
                else:
                    d = interpolate(np.array(number_data.loc[:, loc]), mode=INTERPOLATE_ITEMS[index])
                output_data[:, loc] += d
        else:
            output_data = number_data

        # add text data
        text_columns = np.array(select_file_data.columns)[~number_index]
        columns = np.concatenate([number_columns, text_columns])
        output_data = np.concatenate([output_data, select_file_data.loc[:, ~number_index]], axis=1)

        df = pd.DataFrame(output_data[row_range[0]:row_range[1]+1], columns=columns)
        output_file = os.path.join(DATA_DIR, out_file_name)
        df.to_csv(output_file, index=None)
        # wait watchdog regist file data in db
        time.sleep(0.5)
    except Exception as e:
        body = json.dumps({"error_msg": e.args[0]})
        ret = create_response(body)
        return ret


@route('/api/files/<file_id:int>/columns/interpolate', method='GET')
def interpolate_columns(file_id):
    try:
        file_name = get_file_name_from_id(file_id)
        file_data = pd.read_csv(os.path.join(DATA_DIR, file_name), encoding=ENCODING)
        interpolate_method = int(request.query['interpolate_method'])

        number_index = get_number_index_from_dataframe(file_data)
        number_data = np.array(file_data.loc[:, number_index])

        nan_index = file_data.isnull()

        interpolated_data = np.zeros(file_data.shape)
        if interpolate_method > 0:
            interpolated_data[:, number_index] += interpolate(number_data, mode=INTERPOLATE_ITEMS[interpolate_method])
        else:
            interpolated_data[:, number_index] += number_data

        hist_data = get_hist_from_npdata(number_index, interpolated_data)

        body = json.dumps({
            'interpolated_data': hist_data,
            'nan_index': nan_index.T.tolist(),
        })
    except Exception as e:
        body = json.dumps({"error_msg": e.args[0]})
    ret = create_response(body)
    return ret


@route('/api/files/<file_id:int>/columns/<column_index:int>/interpolate',
       method='GET')
def interpolate_column(file_id, column_index):
    try:
        file_name = get_file_name_from_id(file_id)
        file_data = pd.read_csv(os.path.join(DATA_DIR, file_name), encoding=ENCODING)
        interpolate_method = int(request.query['interpolate_method'])

        data = np.array(file_data.iloc[:, column_index])
        nan_index = np.array(file_data.isnull())
        nan_index = nan_index[:, column_index].reshape(-1)

        if interpolate_method > 0:
            interpolated_data = interpolate(data, mode=INTERPOLATE_ITEMS[interpolate_method])
        else:
            interpolated_data = data[~nan_index]

        body = json.dumps({
            'interpolated_data': interpolated_data.tolist(),
            'nan_index': nan_index.tolist(),
        })
    except Exception as e:
        body = json.dumps({"error_msg": e.args[0]})
    ret = create_response(body)
    return ret


class DataFileEventHandler(PatternMatchingEventHandler):
    def on_created(self, event):
        file_name = event.src_path.split('/')[-1]
        storage.register_file(file_name)

    def on_deleted(self, event):
        file_name = event.src_path.split('/')[-1]
        storage.remove_file(file_name)


def init_db():
    files = os.listdir(DATA_DIR)
    files_in_db = storage.fetch_files()
    name_list = []
    for i in files_in_db:
        name_list.append(files_in_db[i]['name'])

    for f in files:
        if not storage.exist_file(f):
            storage.register_file(f)

    # check remove file
    diff_files = list(set(name_list) - set(files))
    for f in diff_files:
        storage.remove_file(f)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='desc')
    parser.add_argument('--host', default='0.0.0.0', help='Server address')
    parser.add_argument('--port', default='8090', help='Server port')
    args = parser.parse_args()

    if not os.path.isdir(DATA_DIR):
        os.makedirs(DATA_DIR)
    init_db()

    handler = DataFileEventHandler(patterns=['*.csv'])
    observer = Observer()
    observer.schedule(handler, DATA_DIR, recursive=False)
    observer.start()
    run(host=args.host, port=args.port)
    observer.stop()
    observer.join()
