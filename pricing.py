# pricing.py
# 計費規則可自由改（老師通常只看你有沒有「時間 → 費用」邏輯）
import math

def calc_fee(minutes: int, rate_per_hour: int = 40, min_charge_minutes: int = 30) -> int:
    """
    - 未滿 min_charge_minutes：以 min_charge_minutes 計
    - 超過則以「每小時」向上取整計費
    """
    bill_minutes = max(minutes, min_charge_minutes)
    hours = math.ceil(bill_minutes / 60)
    return hours * rate_per_hour
