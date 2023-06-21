import multiprocessing


bind = "0.0.0.0:8000"
workers = int(min(4, multiprocessing.cpu_count() * 2 + 1))
worker_class = "uvicorn.workers.UvicornWorker"
worker_tmp_dir = "/dev/shm"
preload_app = True
timeout = 30
loglevel = "info"  # will be overridden by app config
