# structures.py
# 負責提供停車場會用到的資料結構封裝：
# - Queue：排隊等待進場（collections.deque）
# - Stack：單行巷式停車（先進後出）
# - Hash Table：車牌快速查詢（dict）

from __future__ import annotations
from dataclasses import dataclass
from collections import deque
from typing import Deque, Dict, List, Optional
from datetime import datetime


@dataclass
class CarInLot:
    """紀錄目前在場車輛資訊（給 Hash Table 用）"""
    plate: str
    entry_time: datetime
    mode: str  # "STACK" or "QUEUE"


class WaitingQueue:
    """Queue：排隊等待進場"""
    def __init__(self) -> None:
        self._q: Deque[str] = deque()

    def enqueue(self, plate: str) -> None:
        self._q.append(plate)

    def dequeue(self) -> Optional[str]:
        if not self._q:
            return None
        return self._q.popleft()

    def peek(self) -> Optional[str]:
        return self._q[0] if self._q else None

    def __len__(self) -> int:
        return len(self._q)

    def to_list(self) -> List[str]:
        return list(self._q)


class StackParkingLane:
    """
    Stack：單行巷式停車（LIFO）
    - 進場：push 到 stack 尾端
    - 出場：如果要移出中間車，需用暫存 stack 模擬挪車再復位
    """
    def __init__(self, capacity: int) -> None:
        self.capacity = capacity
        self._stack: List[str] = []

    def is_full(self) -> bool:
        return len(self._stack) >= self.capacity

    def is_empty(self) -> bool:
        return len(self._stack) == 0

    def park(self, plate: str) -> bool:
        if self.is_full():
            return False
        self._stack.append(plate)
        return True

    def remove(self, plate: str) -> tuple[bool, int]:
        """
        移出指定車牌
        回傳 (是否成功, 挪車次數)
        挪車次數 = 暫時移走幾台車
        """
        if plate not in self._stack:
            return (False, 0)

        temp: List[str] = []
        moves = 0

        # 把上面的車先挪走
        while self._stack and self._stack[-1] != plate:
            temp.append(self._stack.pop())
            moves += 1

        # 移走目標車
        if self._stack and self._stack[-1] == plate:
            self._stack.pop()

        # 把挪走的車放回去
        while temp:
            self._stack.append(temp.pop())

        return (True, moves)

    def snapshot(self) -> List[str]:
        """回傳目前停車順序（底 -> 頂）"""
        return list(self._stack)

    def empty_spots(self) -> int:
        return self.capacity - len(self._stack)


class QueueParkingLot:
    """
    Queue 模式停車（非單行巷式，示範用）
    - 停車順序：FIFO（例如：出場只允許從隊首）
    """
    def __init__(self, capacity: int) -> None:
        self.capacity = capacity
        self._q: Deque[str] = deque()

    def is_full(self) -> bool:
        return len(self._q) >= self.capacity

    def park(self, plate: str) -> bool:
        if self.is_full():
            return False
        self._q.append(plate)
        return True

    def exit_front(self) -> Optional[str]:
        if not self._q:
            return None
        return self._q.popleft()

    def snapshot(self) -> List[str]:
        return list(self._q)

    def empty_spots(self) -> int:
        return self.capacity - len(self._q)
