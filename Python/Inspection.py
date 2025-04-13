from netmiko import ConnectHandler
from netmiko.exceptions import (
    NetmikoAuthenticationException,
    NetmikoTimeoutException,
)
from paramiko.ssh_exception import SSHException
import os
import time
from datetime import datetime

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

# 目录配置
LOG_DIR = "Inspection_Bak_Log"
OUTPUT_DIR = "Inspection_Display"
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


def read_inspection_commands(file_path):
    """读取巡检命令文件"""
    with open(file_path, 'r') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]


def inspect_device(device_name, conn_info, commands):
    """执行单设备巡检"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"{device_name}-{conn_info['ip']}-{timestamp}-inspection.txt"
    output_path = os.path.join(OUTPUT_DIR, output_file)
    log_file = os.path.join(LOG_DIR, f"{device_name}-{timestamp}.log")

    try:
        conn_params = {
            'device_type': 'huawei',
            'host': conn_info['ip'],
            'port': conn_info.get('port', 22),
            'username': conn_info['username'],
            'password': conn_info['password'],
            'timeout': 30,
            'session_log': log_file,
            'global_delay_factor': 2,
            'fast_cli': False
        }

        with ConnectHandler(**conn_params) as conn:
            conn.enable()
            # 关闭分页显示
            conn.send_command('screen-length 0 temporary', read_timeout=10)

            # 写入文件头信息
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"设备名称: {device_name}\n")
                f.write(f"设备IP: {conn_info['ip']}\n")
                f.write(f"巡检时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 60 + "\n\n")

            # 执行所有巡检命令
            for cmd in commands:
                try:
                    start_time = time.time()
                    output = conn.send_command(cmd, read_timeout=60)
                    exec_time = round(time.time() - start_time, 2)

                    # 追加写入结果
                    with open(output_path, 'a', encoding='utf-8') as f:
                        f.write(f"✅[命令执行成功] {cmd} (耗时{exec_time}s)\n")
                        f.write("-" * 60 + "\n")
                        f.write(output + "\n\n")

                except Exception as e:
                    with open(output_path, 'a', encoding='utf-8') as f:
                        f.write(f"❌[命令执行失败] {cmd} - {str(e)}\n\n")
                    continue

            print(f"✅ [{device_name}] 巡检完成: {output_file}")
            return True

    except (NetmikoTimeoutException, NetmikoAuthenticationException, SSHException) as e:
        error_type = type(e).__name__
        error_msg = f"❌ [{device_name}] 连接失败 - {error_type}"
    except Exception as e:
        error_msg = f"❌ [{device_name}] 未知错误 - {str(e)}"

    # 记录失败信息到文件
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"巡检失败: {error_msg}")
    print(error_msg)
    return False


if __name__ == "__main__":
    # 读取巡检命令
    inspection_commands = read_inspection_commands("inspection.txt")

    print("\n" + "-" * 25 + " 🔄批量巡检开始 " + "-" * 25)

    total = len(data_list)
    success = 0

    for device in data_list:
        for dev_name, conn_info in device.items():
            print(f"▶️ 正在巡检 {dev_name} ({conn_info['ip']})...")
            if inspect_device(dev_name, conn_info, inspection_commands):
                success += 1
            time.sleep(2)  # 设备间间隔

    print("\n" + "-" * 25 + " 🔄巡检结果统计 " + "-" * 25)
    print(f"✅成功设备: {success}\t❌失败设备: {total - success}")
    print(f"日志目录: {os.path.abspath(LOG_DIR)}")
    print(f"结果目录: {os.path.abspath(OUTPUT_DIR)}")