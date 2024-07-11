import multiprocessing
import os


bind = "0.0.0.0:8000"
preload_app = True
timeout = 480  # this has to be quite long as the workers also generate export data etc.

workers = int(min(4, multiprocessing.cpu_count() * 2 + 1))
worker_class = "uvicorn.workers.UvicornWorker"
worker_tmp_dir = "/dev/shm"

loglevel = os.getenv("TEKST_LOG_LEVEL", "WARNING").upper()
accesslog = "-"
