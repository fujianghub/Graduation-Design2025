![image](https://github.com/user-attachments/assets/d2514723-5882-4e95-ae1a-156a016553b5)

## ✅Iptables

```bash
#启用IP转发
vim /etc/sysctl.conf
net.ipv4.ip_forward=1
sysctl -p

#添加DNAT
iptables -t nat -A PREROUTING \
  -d 201.1.1.128 -p tcp --dport 80 \
  -j DNAT --to-destination 172.16.12.64:80

#添加SNAT
iptables -t nat -A POSTROUTING \
  -p tcp -d 172.16.12.64 --dport 80 \
  -j MASQUERADE  # 或使用 SNAT --to-source [NAT服务器内网IP]
 
 # 允许外部到内网服务器的正向流量
iptables -A FORWARD -d 172.16.12.64 -p tcp --dport 80 \
  -m state --state NEW,ESTABLISHED,RELATED -j ACCEPT

# 允许内网服务器返回的反向流量
iptables -A FORWARD -s 172.16.12.64 -p tcp --sport 80 \
  -m state --state ESTABLISHED,RELATED -j ACCEPT
 
 # 测试：在外部客户端执行
curl http://201.1.1.128:80
```

#### 保存规则（RHEL 9特殊步骤）

RHEL 9默认使用 `nftables`，需将 `iptables` 规则持久化：

```bash
# 安装iptables兼容工具
dnf install iptables-services -y
systemctl enable --now iptables

# 保存当前规则
iptables-save > /etc/sysconfig/iptables
systemctl restart iptables
```

---

## ✅firewall-cmd（经测试ok）

```bash
# 启用IP转发
vim /etc/sysctl.conf
net.ipv4.ip_forward=1
sysctl -p

# 配置DNAT
firewall-cmd --zone=public --add-rich-rule='
  rule family="ipv4"
  destination address="201.1.1.128"
  forward-port port="80" protocol="tcp"
  to-addr="172.16.12.64" to-port="80"
' --permanent

# 配置SNAT
firewall-cmd --zone=public --add-masquerade --permanent

# 允许HTTP服务（可选）
firewall-cmd --zone=public --add-service=http --permanent

# 重载配置
firewall-cmd --reload
```



#### **1. 检查富规则**

```bash
firewall-cmd --zone=public --list-rich-rules
```

输出应包含：

```bash
rule family="ipv4" destination address="201.1.1.128" forward-port port="80" protocol="tcp" to-addr="172.16.12.64" to-port="80"
```

#### **2. 检查MASQUERADE**

```bash
firewall-cmd --zone=public --query-masquerade
```
