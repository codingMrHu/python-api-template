# -*- coding:utf-8 -*-
# @Author: H
# @Date: 2024-07-17 09:27:35
# @Version: 1.0
# @License: H
# @Desc:
import os
import re
from typing import Dict, List, Optional, Type, Union, get_type_hints

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class LoggerConf(BaseModel):
    level: str = "DEBUG"
    format: str = "<level>[{level.name} process-{process.id}-{thread.id} {name}:{line}]</level> - <level>trace={extra[trace_id]} {message}</level>"  # noqa
    handlers: List[Dict] = []

    @classmethod
    def parse_logger_sink(cls, sink: str) -> str:
        match = re.search(r"\{(.+?)\}", sink)
        if not match:
            return sink
        env_keys = {}
        for one in match.groups():
            env_keys[one] = os.getenv(one, "")
        return sink.format(**env_keys)


class COSConfig(BaseModel):
    """腾讯云COS配置"""

    secret_id: str
    secret_key: str
    region: str
    bucket: str
    domain: Optional[str] = None


class DatabaseConfig(BaseModel):
    """数据库配置"""

    url: str


class JWTConfig(BaseModel):
    """JWT配置"""

    secret: str
    expires: int


class Settings(BaseSettings):
    # 基础配置
    environment: Union[dict, str] = "local"
    base_dir: str = os.path.dirname(os.path.abspath(__file__))
    logger_conf: LoggerConf = LoggerConf()

    # 数据库配置
    database: Optional[DatabaseConfig] = None

    # JWT配置
    jwt: Optional[JWTConfig] = None

    # 腾讯云COS配置
    cos: Optional[COSConfig] = None

    class Config:
        extra = "allow"  # 允许动态添加额外字段

    def update_settings(self, **kwargs):
        """更新设置，保持向后兼容"""
        for key, value in kwargs.items():
            setattr(self, key, value)


def load_settings_from_yaml(env: str) -> Settings:
    """从YAML文件加载配置"""
    if env != "prod":
        config_path = os.path.join(Settings().base_dir, ".config.yaml")
    else:
        config_path = os.path.join(Settings().base_dir, ".config_prod.yaml")

    with open(config_path, "r", encoding="utf-8") as f:
        settings_dict = yaml.safe_load(f)

    settings_dict["environment"] = env

    # 创建配置对象
    settings = Settings()

    # 动态解析结构化配置
    # 获取Settings类的类型注解
    type_hints = get_type_hints(Settings)

    for key, value in settings_dict.items():
        if key in type_hints:
            config_type = type_hints[key]

            # 跳过基础类型和特殊处理
            if key in ["environment", "base_dir", "logger_conf"]:
                continue

            # 如果是Optional[SomeConfig]类型，提取实际的配置类
            if hasattr(config_type, "__origin__") and config_type.__origin__ is Union:
                # 从Union类型中提取非None的类型
                actual_type = None
                for arg in config_type.__args__:
                    if arg is not type(None) and issubclass(arg, BaseModel):
                        actual_type = arg
                        break
                if actual_type and isinstance(value, dict):
                    try:
                        setattr(settings, key, actual_type(**value))
                    except Exception as e:
                        print(f"Failed to parse {key} config: {e}")
            elif isinstance(value, dict) and issubclass(config_type, BaseModel):
                try:
                    setattr(settings, key, config_type(**value))
                except Exception as e:
                    print(f"Failed to parse {key} config: {e}")

    # 特殊处理logger配置
    if "logger" in settings_dict:
        settings.logger_conf = LoggerConf(**settings_dict["logger"])

    # 只更新非结构化配置，避免覆盖已正确设置的配置对象
    for key, value in settings_dict.items():
        if key not in type_hints or key in ["environment", "base_dir", "logger_conf"]:
            setattr(settings, key, value)

    return settings


ENV = os.getenv("ENV", "local")
print("env-------", ENV)
settings = load_settings_from_yaml(ENV)
