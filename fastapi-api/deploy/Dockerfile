FROM contos7/py312-api:base
  
USER root

# 添加代码自动解压缩
ADD ./api.tar.gz /root

RUN /root/miniconda3/bin/pip install -r /root/api/deploy/requirements.txt -i http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com
RUN mkdir -p /root/api/logs

EXPOSE 7860

# 设置启动命令
CMD ["/root/miniconda3/bin/supervisord",  "-c" ,"/root/api/deploy/supervisord.conf"]