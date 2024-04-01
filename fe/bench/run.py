import os
import sys
sys.path.append("D:\\wuwen\\ECNU\\大二下\\数据库\\大作业\\book_store")
# os.environ['PATH']=os.environ.get("PATH","")+os.pathsep+"D:\\wuwen\\ECNU\\大二下\\数据库\\大作业\\book_store"
import logging
from fe.bench.workload import Workload
from fe.bench.session import Session


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
    logging.basicConfig(filename='test.log',filemode='w',level=logging.INFO)
    logging.info("bench start")
    run_bench()
