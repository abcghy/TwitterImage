import sqlite3
from main import crawler_username_list
import time
import requests
from concurrent.futures import ThreadPoolExecutor, wait
import os

proxy = 'http://127.0.0.1:7890'

proxies = {
        'http': proxy,
        'https': proxy
        }


class DownloadObj:
    directory: str
    file_name: str
    photos: str

    def __init__(self, directory, file_name, photos):
        self.directory = directory
        self.file_name = file_name
        self.photos = photos


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def real_download_picture(download_obj: DownloadObj):
    print('开始下载', download_obj.file_name)
    # 看文件夹是否存在
    directory = os.path.join('photos', download_obj.directory)
    if not os.path.exists(directory):
        os.makedirs(directory)
    relative_file = os.path.join(directory, download_obj.file_name)

    r = requests.get(download_obj.photos, proxies=proxies)
    if r.status_code == 200:
        with open(relative_file, 'wb') as f:
            f.write(r.content)
        print('下载结束')
    else:
        print('下载失败')


def get_suffix(url):
    return os.path.splitext(url)[-1]


def manage_by_row(row):
    if row['video'] == 1:
        return None
    name = row['name']
    date = row['date']
    time = row['time']
    photos = str(row['photos']).split(',')
    return [DownloadObj(name, str(date) + '|' + str(time) + '|' + str(index) + get_suffix(photo), photo + ':orig') for index, photo in enumerate(photos)]


def fetch_tweet_by(username):
    db_name = username + '.db'
    conn = sqlite3.connect(db_name)
    conn.row_factory = dict_factory

    print('connected', db_name)

    c = conn.cursor()

    cursor = c.execute('SELECT * FROM tweets')

    download_files = []
    for row in cursor:
        file_obj = manage_by_row(row)
        if file_obj:
            download_files.extend(file_obj)

    print('Success', db_name)

    c.close()
    conn.close()
    return download_files


if __name__ == '__main__':
    download_files = []
    for username in crawler_username_list:
        download_files.extend(fetch_tweet_by(username))
    # 前面获取了所有的下载任务，下面开始下载
    print('*' * 20)
    print('开始下载')
    start = time.time()

    executor = ThreadPoolExecutor(max_workers=10)
    future_tasks = [executor.submit(
        real_download_picture, download_obj) for download_obj in download_files]

    wait(future_tasks)

    end = time.time()
    print('总耗时: %s' % (end - start))
    print('*' * 20)
