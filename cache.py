import winreg
import os
import glob
import subprocess
import pickle
import tkinter as tk
from tkinter import filedialog

# Создание главного окна
windows = tk.Tk()

# Настройка окна
windows.title("BOra")  # Заголовок окна
windows.geometry("1100x200")  # Размер окна (ширина x высота)

# Создание таблицы
table = tk.Frame(windows)
table.pack(padx=10, pady=10)

# Расстояние между колонками
table.columnconfigure(0, pad=10)
table.columnconfigure(1, pad=10)
table.columnconfigure(2, pad=10)
table.columnconfigure(3, pad=10)
table.columnconfigure(4, pad=10)

# Создание заголовка
tk.Label(table, text="Browser Name").grid(row=0, column=0)
tk.Label(table, text="Status Browser").grid(row=0, column=1)
tk.Label(table, text="Status Cache").grid(row=0, column=2)
tk.Label(table, text="Locate Cache").grid(row=0, column=3)

# Создание пути к кэш файлам Firefox
    # Запрашиваем список профилей в директории: "Profiles"
profile_path = os.path.join(os.path.expanduser("~"), "AppData\\Local\\Mozilla\\Firefox\\Profiles")
profile_pattern = os.path.join(profile_path, "*.default-release")

    # Получаем список названий профилей в директории: "Profiles"
profile_list = glob.glob(profile_pattern)

# Стандартное расположение браузеров в реестре
BROWSER_KEYS = {
    "Chrome": "SOFTWARE\\Google\\Chrome\\BLBeacon",
    "Firefox": "SOFTWARE\\Mozilla\\Mozilla Firefox",
    "Edge": "SOFTWARE\\Microsoft\\Edge\\BLBeacon",
    "Opera": "SOFTWARE\\Opera Software",
    "Yandex": "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\App Paths\\browser.exe"
}

# Стандартное расположение Кэш файлов браузеров
CACHE_LOCATION = {
    "Chrome": os.path.expanduser("~") + "\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Cache\\Cache_Data",
    "Firefox": profile_list[0] + "\\cache2\\entries",
    "Edge": os.path.expanduser("~") + "\\AppData\\Local\\Microsoft\\Edge\\User Data\\Default\\Cache\\Cache_Data",
    "Opera": os.path.expanduser("~") + "\\AppData\\Opera Software\\Opera Stable\\Cache",
    "Yandex": os.path.expanduser("~") + "\\AppData\\Yandex\\YandexBrowser\\User Data\\Default\\Cache"
}

# Проверяем реестр на наличие установленных браузеров
installed_browser = []
not_installed = []

for browser, value in BROWSER_KEYS.items():
    try:
        winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, value)
        installed_browser.append(browser)
    except FileNotFoundError:
        pass
    
    try:
        winreg.OpenKey(winreg.HKEY_CURRENT_USER, value)
        if browser not in installed_browser:
            installed_browser.append(browser)
    except FileNotFoundError:
            not_installed.append(browser)

# Вывод установленных и не установленных браузеров
r = 1
for browser in installed_browser:    
    label = tk.Label(table, text=browser).grid(row=r, column=0, sticky='w')
    label = tk.Label(table, text="✓").grid(row=r, column=1)
    r += 1

for browser in not_installed:
    label = tk.Label(table, text=browser).grid(row=r, column=0, sticky='w')
    lable = tk.Label(table, text="✗").grid(row=r, column=1)
    r += 1

# Проверка пути Кэша браузеров
r = 1
for browser, value in CACHE_LOCATION.items():
    if os.path.exists(value):
        label = tk.Label(table, text="✓").grid(row=r, column=2) # Status Cache
        label = tk.Text(table, height=1, width=80, wrap='none') # Locate Cache
        label.insert("1.0", value)
        label.config(state="disabled")
        label.grid(row=r, column=3, sticky='w')
        r += 1
    else:
        label = tk.Label(table, text="✗").grid(row=r, column=2)
        label = tk.Text(table, height=1, width=80, wrap='none')
        label.insert("1.0", value)
        label.config(state="disabled")
        label.grid(row=r, column=3, sticky='w')
        r += 1

# Перенос кэша

# Кнопки переноса кэша
# Как должен переноситься кэш
#   Даное 2 папки:
#   Старая: C:\Users\Admin\AppData\Local\Microsoft\Edge\User Data\Default\Cache\Cache_Data
#   Новая: C:\Users\Admin\Desktop\ВРК\Сache_Edge
#   1) Получаем путь к новой папке
#   2) Из старой папки переносятся файлы в новую, 
#   3) Удаляется директория "Cache_Date" и все ее содержимое. 
#   4) Вместо старой папки создаем ссылочую папку: mklink /D "C:\Users\Admin\AppData\Local\Microsoft\Edge\User Data\Default\Cache\Cache_Data" "C:\Users\Admin\Desktop\ВРК\Сache_Edge"
#   5) Если все успешно созданно, то записываем путь к новой директории

# Создание кнопок переноса кэша
for row in range(1, 6):
    button = tk.Button(table, text="Locate", command=lambda row=row: button_path(row))
    button.grid(row=row, column=4)

    # Получение New_Dir
def button_path(row):
    path = (filedialog.askdirectory())
    if path:
        New_Dir = path
        New_Dir = path.replace('/', "\\")        
        creat_link(New_Dir, row)
        
    #Создание ссылки
def creat_link(New_Dir, row):
    # Узнаем название папки в Cache, чтобы в будущем создать ссылку с ее именем
    Old_Dir = table.grid_slaves(row=row, column=3)[0].get("1.0", "end-1c") # Получаем путь к стандартному расположение кэша
    last_element = os.path.basename(Old_Dir)  # Создаем Новый путь с "Cache_Edge" на конце
    New_Dir = os.path.join(New_Dir, last_element)
    

      # Настроить копирование 
    result = subprocess.run(["xcopy", "/I", "/E", Old_Dir, New_Dir], shell=True)
    if result.returncode == 0:
        result_1 = subprocess.run(["rmdir", "/s", "/q", Old_Dir], shell=True) # Удаляем папку с кэшем     P.S. Нужно добавить проверку на удаление. Если не удаляется, то нужно проверить процесс открытия браузера
        if result_1.returncode == 0:
            result_2 = subprocess.run(["mklink", "/D", Old_Dir, New_Dir], shell=True)  # Создаем ссылку
            if result_2.returncode == 0:
                label = tk.Text(table, height=1, width=80, wrap='none')
                label.insert("1.0", New_Dir)
                label.config(state="disabled")
                label.grid(row=row, column=3, sticky='w')
                print("Перенос выполнен успешно")
            else:
                print("Перенос завершился с ошибкой")
        else:
            print("Браузер открыт")
    else:
        print("Ошибка копирования")

# Удаление ссылки

# Возвращение кэша по стандартому пути
#   Даное 2 папки:
#   Старая: C:\Users\Admin\AppData\Local\Microsoft\Edge\User Data\Default\Cache\Cache_Data
#   Новая: C:\Users\Admin\Desktop\ВРК\Сache_Edge\Cache_Data
#   1) Удаляем ссылку (Старую)
#   2) Переносим файлы из Новой в Старую 
#   3) Удаляем директорию с Новой папкой

#Создание кнопки удаления кэша
for row in range(1, 6):
    button = tk.Button(table, text="Reset", command=lambda row=row: delite_link(row))
    button.grid(row=row, column=5)

def delite_link(row):
    all_values = list(CACHE_LOCATION.values())
    Old_Dir = all_values[row-1]
    New_Dir = table.grid_slaves(row=row, column=3)[0].get("1.0", "end-1c") # Получаем новый путь (берем из таблици, т.к. подразумевается, что в окне уже измененый путь)
    result = subprocess.run (["rmdir", "/s", "/q", Old_Dir], shell=True)
    if result.returncode == 0:
        result_2 = subprocess.run(["xcopy", "/I", "/E", New_Dir, Old_Dir], shell=True)
        if result_2.returncode == 0:
            result_3 = subprocess.run (["rmdir", "/s", "/q", New_Dir], shell=True)
            if result_3.returncode == 0:
                label = tk.Text(table, height=1, width=80, wrap='none')
                label.insert("1.0", Old_Dir)
                label.config(state="disabled")
                label.grid(row=row, column=3, sticky='w')
            else:
                print("Удаление новой папки не выполнено")                    
        else:
            print("Копирование не выполнено")
    else:
        print("Удаление символической ссылки не выполнено")



# Функция сохранения 
def close():
    data = []
    for row in range(1, 6):
        data.append(table.grid_slaves(row=row, column=3)[0].get("1.0", "end-1c"))
    with open('data.pkl', 'wb') as file:  # Сохраняем данные в файл
        pickle.dump(data, file)
        windows.destroy()

# ОТслеживание события закрытия окна
windows.protocol("WM_DELETE_WINDOW", close)

#Функция загрузки
def load_data():
    try:
        with open('data.pkl', 'rb') as file:
            data = pickle.load(file)
            
            for row in range(0, 5):
                label = tk.Text(table, height=1, width=80, wrap='none')
                label.insert("1.0", data[row])
                label.config(state="disabled")
                label.grid(row=row+1, column=3, sticky='w')

            # Пример: вывод загруженных данных на экран
            print(data[3])
    except FileNotFoundError:
        None

# Загрузка данных при открытии программы
load_data()

# Отображение кнопки
table.pack()

# Отображение окна
windows.mainloop()

