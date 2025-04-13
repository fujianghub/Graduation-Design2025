from netmiko import ConnectHandler
from netmiko.exceptions import (
    NetmikoAuthenticationException,
    NetmikoTimeoutException,
)
from paramiko.ssh_exception import SSHException
import os
from datetime import datetime
import time

data_list = [
    {"HQ_FWB": {"ip": "192.168.4.22", "port": 22, "username": "HQFeng", "password": "Huawei@123"}},
    {"HQ_FWA": {"ip": "192.168.4.11", "port": 22, "username": "HQFeng", "password": "Huawei@123"}},
    {"HQ_DHCP_Server": {"ip": "192.168.33.1", "port": 22, "username": "HQFeng", "password": "Huawei@123"}},
    {"HQ_SW12": {"ip": "192.168.12.1", "port": 22, "username": "HQFeng", "password": "Huawei@123"}},
    {"HQ_SW4": {"ip": "192.168.4.4", "port": 22, "username": "HQFeng", "password": "Huawei@123"}},
    {"HQ_SW3": {"ip": "192.168.4.3", "port": 22, "username": "HQFeng", "password": "Huawei@123"}},
    {"HQ_SW2": {"ip": "192.168.4.253", "port": 22, "username": "HQFeng", "password": "Huawei@123"}},
    {"HQ_SW1": {"ip": "192.168.4.252", "port": 22, "username": "HQFeng", "password": "Huawei@123"}}
]

backup_dir = "Configure"
os.makedirs(backup_dir, exist_ok=True)
os.makedirs("Download_Bak_Log", exist_ok=True)  # 新增日志目录


def get_current_time():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def backup_device(device_name, conn_info, retry=3):
    for attempt in range(1, retry + 1):
        try:
            connection_params = {
                'device_type': 'huawei',
                'host': conn_info['ip'],
                'port': conn_info.get('port', 22),
                'username': conn_info['username'],
                'password': conn_info['password'],
                'timeout': 45,
                'session_log': os.path.join("Download_Bak_Log", f'{device_name}_session.log'),  # 修改日志路径
                'auth_timeout': 30,
                'banner_timeout': 30,
                'ssh_config_file': './ssh_config',
            }

            with ConnectHandler(**connection_params) as conn:
                conn.write_channel(" \n")
                time.sleep(1)
                conn.send_command('screen-length 0 temporary', read_timeout=10)
                config = conn.send_command('display current-configuration', read_timeout=120)

                filename = f"{device_name}-{conn_info['ip']}-{get_current_time()}.cfg"
                with open(os.path.join(backup_dir, filename), 'w', encoding='utf-8') as f:
                    f.write(f"# Backup Time: {get_current_time()}\n")
                    f.write(f"# Device: {device_name}\n")
                    f.write(f"# IP: {conn_info['ip']}\n\n")
                    f.write(config)

                print(f"✅[SUCCESS] {device_name} 配置已保存至 {os.path.join(backup_dir, filename)}")
                return True

        except (NetmikoTimeoutException, SSHException, ConnectionResetError) as e:
            if attempt < retry:
                time.sleep(attempt * 5)
                continue
            print(f"❌[Fail] {device_name}-{conn_info['ip']} 请检查网络和SSH相关配置！")  # 统一错误提示
            return False
        except NetmikoAuthenticationException as e:
            print(f"❌[Fail] {device_name}-{conn_info['ip']} 请检查网络和SSH相关配置！")  # 统一错误提示
            return False
        except Exception as e:
            print(f"❌[Fail] {device_name}-{conn_info['ip']} 请检查网络和SSH相关配置！")  # 统一错误提示
            return False


# 创建SSH配置文件
if not os.path.exists('ssh_config'):
    with open('ssh_config', 'w') as f:
        f.write("Host *\n")
        f.write("  KexAlgorithms diffie-hellman-group-exchange-sha1\n")
        f.write("  Ciphers aes128-cbc,aes192-cbc,aes256-cbc\n")
        f.write("  MACs hmac-sha1\n")

# 执行备份
for device in data_list:
    for device_name, conn_info in device.items():
        print(f"▶️开始备份 {device_name}-{conn_info['ip']}......")  # 修正IP显示问题
        backup_device(device_name, conn_info)