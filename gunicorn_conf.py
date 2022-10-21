bind = "0.0.0.0:8000"
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
worker_tmp_dir = "/dev/shm"
loglevel = "info"  # will be overridden by app config
