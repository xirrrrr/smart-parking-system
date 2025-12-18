# main.py
# 主程式：提供簡單 CLI 選單（可報告用）
from parking_system import SmartParkingSystem

def print_menu() -> None:
    print("\n===== Smart Parking System =====")
    print("1) 車輛抵達(進場/排隊)")
    print("2) 放行下一台等待車進場")
    print("3) 車輛出場")
    print("4) 查詢車牌是否在場")
    print("5) 顯示停車場狀態")
    print("6) 顯示最近停車紀錄")
    print("7) 時間前進(分鐘)（測試用）")
    print("8) 離開")

def main() -> None:
    system = SmartParkingSystem(capacity=3, mode="STACK", rate_per_hour=40)

    while True:
        print_menu()
        choice = input("選擇功能: ").strip()

        if choice == "1":
            plate = input("輸入車牌: ")
            print(system.arrive(plate))

        elif choice == "2":
            print(system.process_next_waiting())

        elif choice == "3":
            plate = input("輸入要出場的車牌: ")
            print(system.exit(plate))

        elif choice == "4":
            plate = input("輸入車牌: ")
            print("[在場]" if system.is_in_lot(plate) else "[不在場]")

        elif choice == "5":
            print(system.status())

        elif choice == "6":
            print(system.show_recent_records(limit=10))

        elif choice == "7":
            mins = int(input("前進幾分鐘: "))
            system.clock.advance_minutes(mins)
            print(f"[時間] 已前進 {mins} 分鐘，目前時間 {system.clock.now().strftime('%H:%M')}")

        elif choice == "8":
            print("Bye!")
            break

        else:
            print("無效選項，請重新選擇。")

if __name__ == "__main__":
    main()
