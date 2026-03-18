import serial
import serial.tools.list_ports
import threading
import json
import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

scans = []
scan_count = 0
last_code = ""
ser = None

def list_ports():
    return [{"device": p.device, "desc": p.description} for p in serial.tools.list_ports.comports()]

def read_serial(port, baud=9600):
    global ser, last_code, scan_count
    try:
        ser = serial.Serial(port, baud, timeout=1)
        print(f"✅ מחובר ל-{port}")
        while True:
            line = ser.readline().decode("utf-8", errors="ignore").strip()
            if line:
                scan_count += 1
                now = datetime.datetime.now().strftime("%H:%M:%S")
                entry = {"code": line, "time": now, "n": scan_count}
                scans.insert(0, entry)
                last_code = line
                print(f"[{scan_count}] {now} → {line}")
    except Exception as e:
        print(f"❌ שגיאה: {e}")

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a): pass

    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(open("index.html", "rb").read())

        elif self.path == "/ports":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(list_ports()).encode())

        elif self.path == "/scans":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"scans": scans, "total": scan_count}).encode())

    def do_POST(self):
        if self.path == "/connect":
            length = int(self.headers["Content-Length"])
            body = json.loads(self.rfile.read(length))
            port = body.get("port", "COM5")
            t = threading.Thread(target=read_serial, args=(port,), daemon=True)
            t.start()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"ok": True}).encode())

if __name__ == "__main__":
    print("🚀 שרת רץ על http://localhost:8765")
    print("   פתח את הדפדפן ועבור לכתובת הזו")
    HTTPServer(("localhost", 8765), Handler).serve_forever()
