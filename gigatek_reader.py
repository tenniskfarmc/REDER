import serial
import serial.tools.list_ports
import datetime
import csv
import os

# ==========================================
#   קורא צ'יפים GIGATEK - UR110U-30
# ==========================================

def list_ports():
    ports = serial.tools.list_ports.comports()
    if not ports:
        print("❌ לא נמצאו פורטים פעילים.")
        return []
    print("\n📡 פורטים זמינים:")
    for i, p in enumerate(ports):
        print(f"  [{i}] {p.device} — {p.description}")
    return ports

def choose_port(ports):
    if not ports:
        return None
    print()
    choice = input("בחר מספר פורט (ברירת מחדל: COM5): ").strip()
    if choice == "":
        return "COM5"
    try:
        idx = int(choice)
        return ports[idx].device
    except:
        return choice  # אם הקלידו שם ישירות כמו COM5

def save_to_csv(records, filename="gigatek_log.csv"):
    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["קוד", "זמן", "מספר סריקה"])
        writer.writerows(records)
    print(f"\n💾 נשמר ל-{filename}")

def main():
    print("=" * 45)
    print("   קורא צ'יפים GIGATEK — UR110U-30")
    print("=" * 45)

    ports = list_ports()
    port = choose_port(ports)

    if not port:
        print("❌ לא נבחר פורט. יוצא.")
        return

    baud = 9600  # ברירת מחדל לרוב קוראי HID/Serial

    print(f"\n🔌 מנסה להתחבר ל-{port} בקצב {baud}...")

    try:
        ser = serial.Serial(port, baud, timeout=1)
        print(f"✅ מחובר ל-{port}")
        print("\n📋 ממתין לסריקות... (הקש Ctrl+C לסיום)\n")
        print("-" * 40)

        records = []
        scan_count = 0

        while True:
            try:
                line = ser.readline().decode("utf-8", errors="ignore").strip()
                if line:
                    scan_count += 1
                    now = datetime.datetime.now().strftime("%H:%M:%S")
                    records.append([line, now, scan_count])
                    print(f"[{scan_count}] {now}  ➜  {line}")

            except KeyboardInterrupt:
                break

    except serial.SerialException as e:
        print(f"\n❌ שגיאה בחיבור ל-{port}:")
        print(f"   {e}")
        print("\n💡 טיפים:")
        print("   - וודא שהקורא מחובר ל-USB")
        print("   - בדוק ב-Device Manager איזה COM מוקצה")
        print("   - נסה להריץ כמנהל (Run as Administrator)")
        input("\nלחץ Enter לסיום...")
        return

    finally:
        try:
            ser.close()
        except:
            pass

    print("\n" + "=" * 40)
    print(f"סיכום: {scan_count} סריקות בסה\"כ")

    if records:
        save = input("\nלשמור ל-CSV? (y/n): ").strip().lower()
        if save == "y":
            save_to_csv(records)

    input("\nלחץ Enter לסיום...")

if __name__ == "__main__":
    main()
