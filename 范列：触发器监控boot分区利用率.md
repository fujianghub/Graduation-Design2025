### 范列：触发器监控boot分区利用率

```bash
[root@rocky8 ~]# df /boot
Filesystem     1K-blocks    Used Available Use% Mounted on
/dev/sda1       1038336   214868     823468  21% /boot
[root@rocky8 ~]# df /boot | awk -F' +|%' 'NR!=1{print $5}'
21
```

```bash
#自定义监控项
vim /etc/zabbix/zabbix_agent2.d/Test.conf
UserParameter=use_boot,df /boot | awk -F' +|%' 'NR!=1{print $5}'
#重启服务
```

```shell
#测试
[root@ZabbixSQL zabbix_agent2.d]# zabbix_agent2 -t use_boot
use_boot                                      [s|26]
[root@ZabbixSQL zabbix_agent2.d]# df /boot | awk -F' +|%' 'NR!=1{print $5}'
26
```

添加自定义监控项到自定义模板
![image-20250306075719173](https://github.com/user-attachments/assets/52db7fcd-183e-4ec3-a91a-e0bf25563951)

添加触发器
![image-20250306080131841](https://github.com/user-attachments/assets/4877d8e4-8c83-4899-b31b-0e0e0fdc56b0)

![image-20250306080645001](https://github.com/user-attachments/assets/3de9d775-b029-41c7-8fd5-87c4d53784b7)

```bash
#压力测试
dd if=/dev/zero of=/boot/f1.img bs=1500M count=1
```











