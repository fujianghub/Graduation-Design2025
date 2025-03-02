## 💡RHEL9安装zabbix7

✅**链接参考**
https://www.zabbix.com/cn/download?zabbix=7.0&os_distribution=red_hat_enterprise_linux&os_version=9&components=server_frontend_agent&db=mysql&ws=nginx


![image](https://github.com/user-attachments/assets/92cd90fd-5069-4f4d-a09e-02303890a816)

---

#### ✅**前置准备**

- 安装数据库：

```bash
# dnf install -y mysql-server
# systemctl restart mysqld
# systemctl enable mysqld
```

- 关闭对应安全机制：

```bash
#sudo systemctl stop firewalld          # 立即停止防火墙
#sudo systemctl disable firewalld       # 禁止开机启动

#cat /etc/selinux/config #永久关闭
SELINUX=disable
#注：需要reboot
```

---

#### ✅**安装步骤：**

1. 安装

```sql
# rpm -Uvh https://repo.zabbix.com/zabbix/7.0/rhel/9/x86_64/zabbix-release-latest-7.0.el9.noarch.rpm
# dnf clean all

# dnf install -y zabbix-server-mysql zabbix-web-mysql zabbix-nginx-conf zabbix-sql-scripts zabbix-selinux-policy zabbix-agent2  zabbix-get
# dnf install -y zabbix-agent2-plugin-mongodb zabbix-agent2-plugin-mssql zabbix-agent2-plugin-postgresql

# mysql -uroot -p
password
mysql> create database zabbix character set utf8mb4 collate utf8mb4_bin;
mysql> create user zabbix@localhost identified by 'password';
mysql> grant all privileges on zabbix.* to zabbix@localhost;
mysql> set global log_bin_trust_function_creators = 1;
mysql> quit;

# zcat /usr/share/zabbix-sql-scripts/mysql/server.sql.gz | mysql --default-character-set=utf8mb4 -uzabbix -p zabbix

# mysql -uroot -p
password
mysql> set global log_bin_trust_function_creators = 0;
mysql> quit;
```

2. 修改配置文件

```bash
#vim /etc/zabbix/zabbix_server.conf
DBPassword=password
[root@zabbix yum.repos.d]# grep -E '^DB|DBHost=' /etc/zabbix/zabbix_server.conf
# DBHost=localhost
DBName=zabbix
DBUser=zabbix
DBPassword=123456
```

```bash
#vim /etc/nginx/conf.d/zabbix.conf
listen          80;
server_name     zabbix7.feng.org;
```

3. web访问继续配置

```bash
http://zabbix7.feng.org/
```

按照所在配置文件里写入的图片配置（这里和zabbix其他版本一样略......）：

用户名密码：`Admin/zabbix`

---

#### ✅**修正字体乱码：**

```bash
[root@zabbix yum.repos.d]# cd  /usr/share/zabbix/assets/fonts/
[root@zabbix fonts]# ls
graphfont.ttf
[root@zabbix fonts]# mv graphfont.ttf graphfont.ttf.bak
[root@zabbix fonts]# ls
Alibaba-PuHuiTi-Medium.ttf  graphfont.ttf.bak
[root@zabbix fonts]# mv Alibaba-PuHuiTi-Medium.ttf graphfont.ttf
```

---

#### ✅**问题记录**：

```bash
❌#问题：安装zabbix PHP gd 扩展不支持(PHP配置参数--with-gd).
```

解决：默认安装的php版本8.0.30的gd没有加载出来(版本过旧/依赖不兼容），升级php版本

1. 停止所有服务：

   ```bash
   # systemctl stop zabbix-server zabbix-agent2 nginx php-fpm
   ```

2. 安装EPEL 9仓库

   - EPEL 是由 Fedora 社区维护的第三方仓库，为 RHEL/CentOS 等企业级 Linux 系统提供官方仓库中未包含的额外软件包。
     - 例如：某些开发工具、依赖库（如 `libjpeg-devel`、`freetype-devel`）或第三方工具

   ```bash
   #dnf install -y https://mirrors.aliyun.com/epel/epel-release-latest-9.noarch.rpm
   #rpm -qa | grep epel-release
   # 应输出：epel-release-9-*.noarch
   ```

3. 安装Remi仓库

   ```markdown
   Remi 仓库由 Remi Collet 维护，专门提供 新版 PHP 及其他编程语言环境（如 Python、Node.js）的软件包。
   RHEL 官方仓库默认提供的 PHP 版本通常较旧（如 RHEL 9 默认是 PHP 8.0），而 Zabbix 7.0 等新软件需要更高版本的 PHP 支持。Remi 仓库允许您在不破坏系统稳定性的情况下升级到新版 PHP。
   ```

   ```bash
   #安装
   dnf install -y https://rpms.remirepo.net/enterprise/remi-release-9.rpm
   #启用php8.1模块
   dnf module reset php
   dnf module enable php:remi-8.1
   ```

4. 安装php 8.1

   ```bash
   dnf install -y php php-fpm php-gd php-mysqlnd php-bcmath php-mbstring php-xml php-ldap
   systemctl restart zabbix-server zabbix-agent2 nginx php-fpm
   ```

   最后成功！
   ![image](https://github.com/user-attachments/assets/ff523b11-2d31-4c93-acb2-d9f8c0e1e268)

   #### ✅数据库迁移到新主机：

   ```sql
   #旧服务器主机
   systemctl stop zabbix-server.service 
   mkdir /data
   mysqldump -uroot -A -F --single-transaction > /data/all.sql
   systemctl disable --now mysqld
   scp /data/all.sql root@172.16.12.73:/opt
   
   #新主机
   yum install -y mysql-server
   systemctl start mysqld.service 
   systemctl enable mysqld.service 
   mysql < /opt/all.sql
   create user zabbix@'172.16.12.%' identified by '123456';
   grant all privileges on zabbix.* to zabbix@'172.16.12.%';
   ```

   ```bash
   #旧主机
   vim /etc/zabbix/web/zabbix.conf.php
   $DB['SERVER']			= '172.16.12.73';
   
   [root@zabbix ~]# vim /etc/zabbix/zabbix_server.conf 
   [root@zabbix ~]# grep ^DB /etc/zabbix/zabbix_server.conf
   DBHost=172.16.12.73
   DBName=zabbix
   DBUser=zabbix
   DBPassword=123456
   DBPort=3306
   
   systemctl start zabbix-server.service
   ```
---
## 💡RHEL9安装zabbix-agent2

链接：https://www.zabbix.com/cn/download?zabbix=7.0&os_distribution=red_hat_enterprise_linux&os_version=9&components=agent_2&db=&ws=

   ```bash
	rpm -Uvh https://repo.zabbix.com/zabbix/7.0/rhel/9/x86_64/zabbix-release-latest-7.0.el9.noarch.rpm
	dnf clean all
	dnf install -y zabbix-agent2
	dnf install -y zabbix-agent2-plugin-mongodb zabbix-agent2-plugin-mssql zabbix-agent2-plugin-postgresql
	vim /etc/zabbix/zabbix_agent2.conf
	  Server=172.16.12.70
	systemctl restart zabbix-agent2
	systemctl enable zabbix-agent2
   ```




