# -*- coding:utf-8 -*-
# @Author: H
# @Date: 2024-12-11 16:37:37
# @Version: 1.0
# @License: H
# @Desc: 

import asyncio
import httpx

"""异步并发请求多个API, 其中一个完成则返回结果（不等待全部响应完成）"""

class Task:
    def __init__(self, name, method, url, headers, data):
        self.name = name
        self.method = method
        self.url = url
        self.headers = headers
        self.data = data

    async def execute(self):
        print(f"{self.name} started")
        async with httpx.AsyncClient() as client:
            response = await client.request(self.method, self.url, headers=self.headers, data=self.data, timeout=20)
        print(f"{self.name} completed")
        return str(response.text)

async def run_tasks_concurrently(tasks):
    # 使用 asyncio.as_completed() 返回已完成的任务
    for completed_task in asyncio.as_completed([task.execute() for task in tasks]):
        result = await completed_task
        print(f"Result: {result}")
        break

if __name__ == "__main__":
    tasks = [
        Task("Task 1", 'GET', 'http://localhost:5000', {'Content-Type': 'application/json'}, '{"name": "John", "age": 30}'),
        Task("Task 2", 'GET', 'http://localhost:5000', {'Content-Type': 'application/json'}, '{"name": "Jane"}'),
        Task("Task 3", 'GET', 'http://localhost:5000', {'Content-Type': 'application/json'}, '{"xx": "mm"}')
    ]
    asyncio.run(run_tasks_concurrently(tasks))
