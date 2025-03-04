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

![image-20250304094325422](C:\Users\冯富江\AppData\Roaming\Typora\typora-user-images\image-20250304094325422.png)

![image-20250304091122386](C:\Users\冯富江\AppData\Roaming\Typora\typora-user-images\image-20250304091122386.png)

**web访问测试：**

![image-20250304094726307](C:\Users\冯富江\AppData\Roaming\Typora\typora-user-images\image-20250304094726307.png)

#### ✅Zabbix添加nginx模板

![image-20250304095625188](C:\Users\冯富江\AppData\Roaming\Typora\typora-user-images\image-20250304095625188.png)