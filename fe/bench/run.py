import os
import sys
sys.path.append("D:\\wuwen\\ECNU\\大二下\\数据库\\大作业\\book_store")
# os.environ['PATH']=os.environ.get("PATH","")+os.pathsep+"D:\\wuwen\\ECNU\\大二下\\数据库\\大作业\\book_store"
import logging
from fe.bench.workload import Workload
from fe.bench.session import Session

import threading
from be import serve
from be.model.store import init_completed_event
from urllib.parse import urljoin
from fe import conf
import requests
thread:threading.Thread = None

logging.basicConfig(filename='bench.log',level=logging.INFO)

def run_bench():
    wl = Workload()
    wl.gen_database()

    sessions = []
    for i in range(0, wl.session):
        ss = Session(wl)
        sessions.append(ss)

    for ss in sessions:
        ss.start()

    for ss in sessions:
        ss.join()


if __name__ == "__main__":
    # global thread
    thread = threading.Thread(target=serve.be_run)
    thread.start()
    init_completed_event.wait()
    logging.info("bench start")
    run_bench()
    url=urljoin(conf.URL,"shutdown")
    requests.get(url)
    thread.join()


