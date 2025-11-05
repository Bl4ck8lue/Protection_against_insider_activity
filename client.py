# client.py
import socket
import platform
import json
import wmi
import psutil
import winapps

def build_payload():
    model_cpu = platform.processor()
    computer = wmi.WMI()
    try:
        gpu = computer.Win32_VideoController()[0].Name
    except Exception:
        gpu = "Unknown GPU"
    try:
        ram = float(computer.Win32_OperatingSystem()[0].TotalVisibleMemorySize) / 1048576
    except Exception:
        ram = 0.0

    disk_partitions = psutil.disk_partitions()

    apps = []
    for app in winapps.list_installed():
        apps.append(app.name)

    j = {
        "CPU": model_cpu,
        "GPU": gpu,
        "Size RAM (GB)": ram,
        "Disk count": len(disk_partitions),
        "Programs": apps
    }
    return json.dumps(j, ensure_ascii=False)

def main(server_host='127.0.0.1', server_port=50000):
    payload = build_payload().encode('utf-8')
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((server_host, server_port))
        client.sendall(payload)
        resp = client.recv(1024)
        print("Server replied:", resp.decode('utf-8', errors='replace'))
    except Exception as e:
        print("Client error:", e)
    finally:
        client.close()

if __name__ == '__main__':
    # замените на IP сервера при необходимости
    main('127.0.0.1', 50000)
