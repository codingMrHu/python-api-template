<!--
 * @Author: H
 * @Date: 2024-07-17 09:15:53
 * @Version: 1.0
 * @License: H
 * @Desc: 
-->
# FastAPI+ SQLModel

## 项目介绍
本项目是一个基础的FastAPI+SQLModel项目，用于演示如何使用这两个框架快速构建一个RESTful API。

本项目是一个基于 FastAPI 和 SQLModel 的 Web 应用程序，用于演示如何使用这两个框架快速构建一个 RESTful API。

## 功能

- 用户注册和登录
- 用户操作日志记录

## 技术栈

- Python 3.10+
- FastAPI
- SQLModel
- Mysql

## 安装

1. 克隆项目到本地

## 部署
    2种方式
        1. 通过Dockerfile构造镜像，将代码放到镜像中直接执行容器即可（适合有自己的镜像库的方式，构造镜像推送后直接执行）
        2. 将代码放到服务器上，通过映射代码位置 docker-compose 启动容器（适合没有镜像库的方式，直接执行容器）
