import socket, platform, wmi, json, winapps

client = socket.socket()  # создаем сокет клиента
hostname = socket.gethostname()  # получаем хост сервера
port = 123  # устанавливаем порт сервера
client.connect((hostname, port))  # подключаемся к серверу

# Hardware
model_cpu = platform.processor()
computer = wmi.WMI()
model_GPU = computer.Win32_VideoController()[0].Name
ram = float(computer.Win32_OperatingSystem()[0].TotalVisibleMemorySize) / 1048576

# Program
apps = []
for app in winapps.list_installed():
    apps.append(app)
    #print(app)
for i in apps:
    print(i)

# All info
j_string = {"CPU: ": model_cpu,
            "GPU: ": model_GPU,
            "Size RAM: ": ram,
            "Disk count: ": 0,
            "Installed programs": apps}
message_send = json.dumps(j_string)
client.sendall(message_send.encode('utf-8'))

data = client.recv(1024)  # получаем данные с сервера
print("Server sent: ", data.decode())  # выводим данные на консоль
client.close()  # закрываем подключение