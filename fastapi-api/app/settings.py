# -*- coding:utf-8 -*-
# @Author: H
# @Date: 2024-07-17 09:27:35
# @Version: 1.0
# @License: H
# @Desc: 
import os
import re
from typing import Dict, List, Optional, Union

import yaml
from loguru import logger
from pydantic import BaseModel, Field,BaseSettings
# from pydantic_settings import BaseSettings
from sqlmodel import select

class LoggerConf(BaseModel):
    level: str = 'DEBUG'
    format: str = '<level>[{level.name} process-{process.id}-{thread.id} {name}:{line}]</level> - <level>trace={extra[trace_id]} {message}</level>'  # noqa
    handlers: List[Dict] = []

    @classmethod
    def parse_logger_sink(cls, sink: str) -> str:
        match = re.search(r'\{(.+?)\}', sink)
        if not match:
            return sink
        env_keys = {}
        for one in match.groups():
            env_keys[one] = os.getenv(one, '')
        return sink.format(**env_keys)


    
class Settings(BaseSettings):
    environment: Union[dict, str] = 'local'
    base_dir : str = os.path.dirname(os.path.abspath(__file__))
    logger_conf: LoggerConf = LoggerConf()

    class Config:
        extra = 'allow'  # 允许动态添加额外字段
        
    def update_settings(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

def load_settings_from_yaml(env: str) -> Settings:
    if env!='prod':
        config_path = os.path.join(Settings().base_dir, '.config.yaml')
    else:
        config_path = os.path.join(Settings().base_dir, '.config_prod.yaml')

    with open(config_path, 'r', encoding='utf-8') as f:
        settings_dict = yaml.safe_load(f)

    settings_dict['environment'] = env
    settings = Settings()
    settings.update_settings(**settings_dict)
    return settings

ENV = os.getenv('ENV', 'local')
print('env-------',ENV)
settings = load_settings_from_yaml(ENV)
