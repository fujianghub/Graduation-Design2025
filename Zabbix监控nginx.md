## 💡Zabbix监控nginx

#### ✅安装和配置nginx

```bash
yum install -y nginx
vim /etc/nginx/nginx.conf
#添加下面三行，Zabbix默认监控/basic_status,此处为/status，需要和zabbix的模板定义的路径要保持一致 
        location = /basic_status {
                stub_status;
        }
systemctl enable --now nginx
```
![image](https://github.com/user-attachments/assets/2689f466-1d04-49b7-82d8-dfa3e002bb04)

![image](https://github.com/user-attachments/assets/a2bb2d18-ddd9-460b-8b65-3ffcd1c1ad0e)

**web访问测试：**
![image](https://github.com/user-attachments/assets/ca1f4b17-b5c3-4c81-8e42-e4cc814388d7)


#### ✅Zabbix添加nginx模板

![image](https://github.com/user-attachments/assets/3a77d4e1-718f-4c4d-9cfa-ad500dd19c89)
#### ✅可以单独针对某个设备定义宏
![image](https://github.com/user-attachments/assets/49c521e3-8b7c-436c-8ce6-fd1c640408c7)
