import dearpygui.dearpygui as dpg
import psutil
import wmi
import platform
import locale
import pythoncom
import subprocess
import socket

# Dil seçenekleri
languages = {
    "Türkçe": "tr_TR",
    "English": "en_US",
    "Français": "fr_FR",
    "Italiano": "it_IT"
}

# Mevcut dil
current_language = "en_US"

# IP adresini listeleyen fonksiyon
def list_ip_address():
    ip_address = socket.gethostbyname(socket.gethostname())
    dpg.set_value("ip_info", f"IP Address: {ip_address}")

# Wi-Fi şifrelerini listeleyen fonksiyon
def get_wifi_passwords():
    profiles_data = subprocess.check_output(['netsh', 'wlan', 'show', 'profiles']).decode('utf-8').split('\n')
    profiles = [i.split(":")[1][1:-1] for i in profiles_data if "All User Profile" in i]

    wifi_info = ""
    for profile in profiles:
        profile_info = subprocess.check_output(['netsh', 'wlan', 'show', 'profile', profile, 'key=clear']).decode('utf-8').split('\n')
        password_line = [b for b in profile_info if "Key Content" in b]
        try:
            password = password_line[0].split(":")[1][1:-1]
        except IndexError:
            password = "No password found"
        wifi_info += f"SSID: {profile}, Password: {password}\n"
    
    return wifi_info

def list_wifi_passwords():
    wifi_info = get_wifi_passwords()
    dpg.set_value("wifi_info", wifi_info)

# Cihaz bilgilerini listeleyen fonksiyon
def list_devices():
    pythoncom.CoInitialize()
    dpg.set_value("device_info", "")
    c = wmi.WMI()
    devices = "Connected Disks:\n"
    for disk in c.Win32_LogicalDisk():
        devices += f"  Device: {disk.DeviceID}, Mount Point: {disk.Caption}, File System: {disk.FileSystem}\n"
    
    devices += "\nUSB Devices:\n"
    for usb in c.Win32_USBControllerDevice():
        usb_device = usb.Dependent
        devices += f"  Device: {usb_device.DeviceID}, Manufacturer: {usb_device.Manufacturer}, Description: {usb_device.Description}\n"
    
    devices += "\nNetwork Interfaces:\n"
    addrs = psutil.net_if_addrs()
    for interface, address_list in addrs.items():
        devices += f"  Interface: {interface}\n"
        for addr in address_list:
            devices += f"    Family: {addr.family}, Address: {addr.address}, Netmask: {addr.netmask}, Broadcast: {addr.broadcast}\n"

    dpg.set_value("device_info", devices)

# Sistem bilgilerini listeleyen fonksiyon
def system_info():
    pythoncom.CoInitialize()
    dpg.set_value("system_info", "")
    sys_info = f"Operating System: {platform.system()} {platform.release()}\n"
    sys_info += f"Processor: {platform.processor()}\n"
    sys_info += f"RAM: {round(psutil.virtual_memory().total / (1024**3))} GB\n"
    
    c = wmi.WMI()
    for item in c.Win32_ComputerSystem():
        sys_info += f"Motherboard Model: {item.Model}\n"
        sys_info += f"System Manufacturer: {item.Manufacturer}\n"

    for disk in c.Win32_DiskDrive():
        sys_info += f"HDD/SSD Model: {disk.Model}, Capacity: {round(int(disk.Size) / (1024**3))} GB\n"

    for item in c.Win32_VideoController():
        sys_info += f"Graphics Card: {item.Name}\n"

    for item in c.Win32_NetworkAdapter():
        if item.NetEnabled:
            sys_info += f"Network Adapter: {item.Name}\n"

    for item in c.Win32_SoundDevice():
        sys_info += f"Sound Card: {item.Name}\n"

    dpg.set_value("system_info", sys_info)

# Dil değiştirme fonksiyonu
def change_language(sender, app_data):
    global current_language
    current_language = languages[app_data]
    locale.setlocale(locale.LC_ALL, current_language)
    update_ui_language()

# UI dilini güncelleme fonksiyonu
def update_ui_language():
    dpg.set_item_label("btn_devices", translate("Devices"))
    dpg.set_item_label("btn_system", translate("System Info"))
    dpg.set_item_label("btn_help", translate("Help"))
    dpg.set_item_label("btn_help_info", translate("©MaskTheGreat 2024 All Rights Reserved"))

# Yardım fonksiyonu
def help_info():
    dpg.set_value("help_info", "©MaskTheGreat 2024 All Rights Reserved")

# Çeviri fonksiyonu
def translate(text):
    translations = {
        "Devices": "Aygitlar",
        "System Info": "Sistem Bilgisi",
        "Help": "Yardim",
        "©MaskTheGreat 2024 All Rights Reserved": "©MaskTheGreat 2024 All Rights Reserved"
    }
    return translations.get(text, text)

# Dear PyGui arayüzünü oluşturma
dpg.create_context()
with dpg.theme() as global_theme:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 10)
        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5)
        dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (0, 128, 255))  # Rahatlatıcı mavi arka plan rengi
        dpg.add_theme_color(dpg.mvThemeCol_Border, (200, 200, 200))
        dpg.add_theme_color(dpg.mvThemeCol_Button, (50, 50, 50))
        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (70, 70, 70))
        dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (90, 90, 90))
        dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive, (50, 50, 50))

with dpg.window(label="NexDevice", width=800, height=600):
    dpg.bind_theme(global_theme)
    with dpg.tab_bar():
        with dpg.tab(label="Aygitlar"):
            dpg.add_button(label="Cihazlari Listele", callback=list_devices, tag="btn_devices", width=200, height=40)
            dpg.add_separator()
            dpg.add_text("", tag="device_info")
        with dpg.tab(label="Sistem Bilgisi"):
            dpg.add_button(label="Sistem Bilgilerini Göster", callback=system_info, tag="btn_system", width=200, height=40)
            dpg.add_separator()
            dpg.add_text("", tag="system_info")
        with dpg.tab(label="IP Adresi"):
            dpg.add_button(label="IP Adresini Göster", callback=list_ip_address, width=200, height=40)
            dpg.add_separator()
            dpg.add_text("", tag="ip_info")
        with dpg.tab(label="Wi-Fi Şifreleri"):
            dpg.add_button(label="Wi-Fi Şifrelerini Göster", callback=list_wifi_passwords, width=200, height=40)
            dpg.add_separator()
            dpg.add_text("", tag="wifi_info")
        with dpg.tab(label="Yardim"):
            dpg.add_combo(list(languages.keys()), label="Dil Seçenekleri", callback=change_language, width=200)
            dpg.add_separator()
            dpg.add_button(label="Yardim", callback=help_info, width=200, height=40)
            dpg.add_separator()
            dpg.add_text("", tag="help_info")

dpg.create_viewport(title='NexDevice', width=800, height=600)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
