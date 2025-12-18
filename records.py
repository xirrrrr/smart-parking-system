# records.py
# Linked List：用來保存停車紀錄（進出場、費用、停車分鐘、挪車次數...）
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List


@dataclass
class Record:
    plate: str
    entry_time: datetime
    exit_time: datetime
    minutes: int
    fee: int
    mode: str
    moves: int  # Stack 模式出車時，挪車次數（Queue 模式為 0）


@dataclass
class Node:
    data: Record
    next: Optional["Node"] = None


class RecordLinkedList:
    """單向 Linked List（新紀錄插到表頭，O(1)）"""
    def __init__(self) -> None:
        self.head: Optional[Node] = None
        self.size = 0

    def add_front(self, record: Record) -> None:
        self.head = Node(record, self.head)
        self.size += 1

    def to_list(self, limit: int = 20) -> List[Record]:
        """匯出最近幾筆紀錄（預設 20 筆）"""
        out: List[Record] = []
        cur = self.head
        while cur and len(out) < limit:
            out.append(cur.data)
            cur = cur.next
        return out
