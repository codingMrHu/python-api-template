# -*- coding:utf-8 -*-
# @Author: H
# @Date: 2024-07-18 15:38:02
# @Version: 1.0
# @License: H
# @Desc: 

class ListNode:
    def __init__(self, value=0, next=None):
        self.value = value
        self.next = next

def reverse_list(head: ListNode) -> ListNode:
    prev = None
    current = head
    while current:
        next_node = current.next  # 保存下一个节点
        current.next = prev       # 反转当前节点的指针
        prev = current            # 移动前驱指针到当前节点
        current = next_node       # 移动当前节点到下一个节点
    return prev

# 定义测试链表
node3 = ListNode(3)
# node2 = ListNode(2, node3)
# node1 = ListNode(1, node2)

# 原链表：1 -> 2 -> 3
head = node3

# 调用反转函数
reversed_head = reverse_list(head)

# 打印反转后的链表
current = reversed_head
while current:
    print(current.value, end=" -> ")
    current = current.next
# 输出: 3 -> 2 -> 1 ->