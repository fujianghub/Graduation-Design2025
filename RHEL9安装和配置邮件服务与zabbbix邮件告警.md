### ✅postfix的安装和配置

```bash
#安装
dnf install postfix s-nail  -y
systemctl enable --now postfix
systemctl status postfix
```



```bash
vim /etc/postfix/main.cf
# ------------New Zabbix Warning--------------------------------
# 设置发件人地址伪装（替换为你的邮箱）
smtp_generic_maps = hash:/etc/postfix/generic
# 或使用 sender_canonical_maps（根据需求选择其一）
# sender_canonical_maps = hash:/etc/postfix/sender_canonical

# 启用 SMTP SASL 认证
smtp_sasl_auth_enable = yes
smtp_sasl_password_maps = hash:/etc/postfix/sasl_passwd
smtp_sasl_security_options = noanonymous
smtp_sasl_mechanism_filter = plain, login

# 指定 SMTP 服务器
relayhost = [smtp.exmail.qq.com]:465
# 如果使用 SSL/TLS，添加以下配置
smtp_tls_wrappermode = yes

# ---------------------------------------------------------------------------------

#创建发件人地址映射文件
vim /etc/postfix/generic
@zabbix.com xxxxxxx@tjgydx.wecom.work
#生成数据库文件：
postmap /etc/postfix/generic
# -------------------------------------------------------------------------------
#创建 SMTP 认证密码文件
vim /etc/postfix/sasl_passwd
[smtp.exmail.qq.com]:465 xxxxxxx@tjgydx.wecom.work:aaaaaa
#设置权限并生成数据库
chmod 600 /etc/postfix/sasl_passwd
postmap /etc/postfix/sasl_passwd

#重启服务
systemctl restart postfix.service
```

```bash
#测试
echo "Test Email Body" | mail -s "Test Email from RHEL9" fujiang0225@163.com
#备选测试方法：echo "Subject: Test Email" | sendmail fujiang0225@163.com
```

---

### ✅Zabbix7 配置和测试告警媒介

```bash
#注意：此处使用个人微信似乎有bug，只能使用企业微信
```
![image-20250309235356981](https://github.com/user-attachments/assets/ea91e622-25b4-4a8e-b93b-5f225fca0a39)

