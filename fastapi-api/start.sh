/root/miniconda3/bin/uvicorn main:app --host 0.0.0.0 --port 7860 --workers 4

# 生产启动方式 gunicorn+uvicorn 
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app:app --bind 0.0.0.0:7860