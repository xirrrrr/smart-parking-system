# parking_system.py
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, Optional

from structures import WaitingQueue, StackParkingLane, QueueParkingLot, CarInLot
from records import RecordLinkedList, Record
from pricing import calc_fee


class SimClock:
    """為了測試可重現：可以手動前進時間"""
    def __init__(self, start: Optional[datetime] = None) -> None:
        self._now = start or datetime.now()

    def now(self) -> datetime:
        return self._now

    def advance_minutes(self, minutes: int) -> None:
        self._now += timedelta(minutes=minutes)


class SmartParkingSystem:
    """
    需求對應：
    - Queue：排隊等待進場
    - Stack：單行巷式停車
    - Hash Table：車牌是否在場 / 快速查詢
    - Linked List：停車紀錄
    """
    def __init__(self, capacity: int = 5, mode: str = "STACK", rate_per_hour: int = 40) -> None:
        self.capacity = capacity
        self.mode = mode.upper()  # "STACK" or "QUEUE"
        self.rate_per_hour = rate_per_hour

        self.waiting = WaitingQueue()
        self.records = RecordLinkedList()

        self.in_lot: Dict[str, CarInLot] = {}  # Hash Table：plate -> CarInLot

        self.stack_lane = StackParkingLane(capacity)
        self.queue_lot = QueueParkingLot(capacity)

        self.clock = SimClock(datetime(2025, 12, 19, 9, 0, 0))  # 固定起始時間方便 demo

    def set_mode(self, mode: str) -> None:
        mode = mode.upper()
        if mode not in ("STACK", "QUEUE"):
            raise ValueError("mode must be STACK or QUEUE")
        if self.in_lot:
            raise RuntimeError("停車場內有車時不可切換模式")
        self.mode = mode

    def arrive(self, plate: str) -> str:
        """車輛抵達：如果滿了 → 進等待隊列；否則直接進場"""
        plate = plate.strip().upper()
        if not plate:
            return "車牌不可為空"

        if plate in self.in_lot or plate in self.waiting.to_list():
            return f"[拒絕] 車牌 {plate} 已在場或已在等待隊列"

        if self._lot_is_full():
            self.waiting.enqueue(plate)
            return f"[排隊] 停車場已滿，{plate} 進入等待隊列（目前等待 {len(self.waiting)} 台）"

        return self._enter_lot(plate)

    def process_next_waiting(self) -> str:
        """從等待隊列放行一台進場（若有空位）"""
        if self._lot_is_full():
            return "[無法放行] 停車場仍是滿的"
        plate = self.waiting.dequeue()
        if not plate:
            return "[無車可放行] 等待隊列為空"
        return self._enter_lot(plate)

    def _enter_lot(self, plate: str) -> str:
        """真正執行進場（依模式放到 Stack 或 Queue）"""
        now = self.clock.now()

        if self.mode == "STACK":
            ok = self.stack_lane.park(plate)
        else:
            ok = self.queue_lot.park(plate)

        if not ok:
            # 理論上不會發生（外層已判斷滿），保險起見
            self.waiting.enqueue(plate)
            return f"[排隊] 進場失敗，{plate} 改排隊"

        self.in_lot[plate] = CarInLot(plate=plate, entry_time=now, mode=self.mode)
        return f"[進場] {plate} 於 {now.strftime('%H:%M')} 進入停車場（模式={self.mode}）"

    def exit(self, plate: str) -> str:
        """出場：計算停車時間與費用，寫入 Linked List 紀錄"""
        plate = plate.strip().upper()
        if plate not in self.in_lot:
            return f"[查無此車] {plate} 不在場內"

        car = self.in_lot[plate]
        now = self.clock.now()

        moves = 0
        if car.mode == "STACK":
            ok, moves = self.stack_lane.remove(plate)
            if not ok:
                return f"[錯誤] 系統狀態異常：找不到 {plate}"
        else:
            # Queue 模式：只允許隊首出場（FIFO），示範 Queue 的特性
            front = self.queue_lot.exit_front()
            if front != plate:
                # 把拿出來的車放回去（避免資料錯亂）
                if front is not None:
                    self.queue_lot.park(front)
                return f"[Queue限制] Queue 模式只能讓隊首出場，目前隊首不是 {plate}"

        minutes = int((now - car.entry_time).total_seconds() // 60)
        fee = calc_fee(minutes, rate_per_hour=self.rate_per_hour)

        self.records.add_front(
            Record(
                plate=plate,
                entry_time=car.entry_time,
                exit_time=now,
                minutes=minutes,
                fee=fee,
                mode=car.mode,
                moves=moves
            )
        )
        del self.in_lot[plate]

        # 出場後若有空位，嘗試放行一台等待車
        auto = ""
        if len(self.waiting) > 0 and not self._lot_is_full():
            auto = "\n" + self.process_next_waiting()

        return (
            f"[出場] {plate} 於 {now.strftime('%H:%M')} 離場｜停車 {minutes} 分鐘｜費用 {fee} 元"
            + (f"｜挪車 {moves} 次" if car.mode == "STACK" else "")
            + auto
        )

    def is_in_lot(self, plate: str) -> bool:
        """Hash Table O(1) 查詢"""
        return plate.strip().upper() in self.in_lot

    def status(self) -> str:
        """顯示停車場狀態（空位、停車順序、等待隊列）"""
        if self.mode == "STACK":
            order = self.stack_lane.snapshot()
            empty = self.stack_lane.empty_spots()
        else:
            order = self.queue_lot.snapshot()
            empty = self.queue_lot.empty_spots()

        return (
            f"=== 狀態（模式={self.mode}）===\n"
            f"目前在場：{len(order)} 台｜空位：{empty}\n"
            f"停車順序：{order}\n"
            f"等待隊列：{self.waiting.to_list()}\n"
        )

    def show_recent_records(self, limit: int = 10) -> str:
        recs = self.records.to_list(limit=limit)
        if not recs:
            return "(尚無停車紀錄)"
        lines = ["=== 最近停車紀錄 ==="]
        for r in recs:
            lines.append(
                f"{r.plate} | {r.mode} | {r.entry_time.strftime('%H:%M')}→{r.exit_time.strftime('%H:%M')} "
                f"| {r.minutes} 分 | {r.fee} 元 | moves={r.moves}"
            )
        return "\n".join(lines)

    def _lot_is_full(self) -> bool:
        if self.mode == "STACK":
            return self.stack_lane.is_full()
        return self.queue_lot.is_full()
