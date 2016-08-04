# -*- coding: utf-8 -*-

import os
import socket
import Queue
import httplib2
import threading

from src.conf import IMG_DIR, DOWNLOAD_WORKER_NUM

SHARE_QUEUE = Queue.Queue()


class DownloadThread(threading.Thread):
    def __init__(self, func):
        super(DownloadThread, self).__init__()
        self.func = func

    def run(self):
        self.func()


def download_worker():
    global SHARE_QUEUE
    while not SHARE_QUEUE.empty():
        item = SHARE_QUEUE.get()
        sn = item["sn"]
        img_url = item["img_url"]
        filepath = item["filepath"]

        h = httplib2.Http()
        try:
            resp, content = h.request(img_url)
        except socket.error:
            print("SKIP: SN " + sn + " NETWORK PROBLEM")
            continue
        if resp["status"] == "200":
            with open(filepath, "wb") as f:
                f.write(content)
            print("OK: SN " + sn)
        else:
            print("SKIP: SN " + sn + " CANNOT ACCESS THE IMAGE")


def init_downloader():
    if not os.path.exists(IMG_DIR):
        os.makedirs(IMG_DIR)


def add_task(sn, img_url, filepath):
    """
    向下载队列中增加任务
    :param img_url: 图片 URL
    :param filepath: 保存路径
    """
    global SHARE_QUEUE
    SHARE_QUEUE.put({
        "sn": sn,
        "img_url": img_url,
        "filepath": filepath,
    })


def generate_filepath(sn, mime):
    """
    生成图片文件名
    :param sn: SN
    :param mime: MIME
    :return: 图片文件名
    """
    filename = sn + "."
    if mime == "image/png":
        filename += ".png"
    elif mime == "image/jpeg" or mime == "image/jpg":
        filename += ".jpg"
    elif mime == "image/gif":
        filename += ".gif"
    else:
        filename += "png"
    return os.path.join(IMG_DIR, filename)