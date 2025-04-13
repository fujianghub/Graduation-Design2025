from netmiko import ConnectHandler
from netmiko.exceptions import (
    NetmikoAuthenticationException,
    NetmikoTimeoutException,
)
from paramiko.ssh_exception import SSHException
import os
import time

# 设备列表
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

# 初始化日志目录
LOG_DIR = "Configure_Bak_Log"
os.makedirs(LOG_DIR, exist_ok=True)


def read_config_file(file_path):
    with open(file_path, 'r') as f:
        return [line.strip() for line in f if line.strip()]


def save_config(conn, device_name):
    try:
        conn.exit_config_mode()
        output = conn.send_command("save", expect_string=r"[Y/N]", read_timeout=30)
        output += conn.send_command("Y", expect_string=r">", read_timeout=60)
        print(f"✅[{device_name}] 配置保存成功")
        return True
    except Exception as e:
        print(f"❌[{device_name}] 保存失败: {str(e)}")
        return False


def configure_device(device_name, conn_info, config_commands):
    try:
        connection_params = {
            'device_type': 'huawei',
            'host': conn_info['ip'],
            'port': conn_info.get('port', 22),
            'username': conn_info['username'],
            'password': conn_info['password'],
            'timeout': 30,
            'session_log': os.path.join(LOG_DIR, f"{device_name}_session.log"),  # 关键修改点
            'fast_cli': False
        }

        with ConnectHandler(**connection_params) as conn:
            conn.enable()
            output = conn.send_config_set(config_commands)

            if save_config(conn, device_name):
                with open(os.path.join(LOG_DIR, "success.log"), "a") as f:
                    f.write(f"{time.ctime()} | {device_name} ({conn_info['ip']})\n")
                return True

    except (NetmikoTimeoutException, NetmikoAuthenticationException, SSHException) as e:
        error_msg = f"连接失败: {type(e).__name__}"
    except Exception as e:
        error_msg = f"未知错误: {str(e)}"

    with open(os.path.join(LOG_DIR, "failed.log"), "a") as f:
        f.write(f"{time.ctime()} | {device_name} ({conn_info['ip']}) | {error_msg}\n")
    print(f"❌ [{device_name}] {error_msg}")
    return False


if __name__ == "__main__":
    config_commands = ["system-view"] + read_config_file("conf.txt")

    print("\n" + "-" * 25 + " 🔄批量配置 " + "-" * 25)

    success = 0
    for device in data_list:
        for name, info in device.items():
            print(f"▶️ 正在配置 {name} ({info['ip']})...")
            if configure_device(name, info, config_commands):
                success += 1

    print("\n" + "-" * 25 + " 🔄结果统计 " + "-" * 25)
    print(f"✅ 成功: {success}\n❌ 失败: {len(data_list) - success}")
    print(f"详细日志位置: {os.path.abspath(LOG_DIR)}")
    print("-" * 60)