### 🔔自定义监控项和模板，监控TCP十一种状态机-->导出模板

监控项 -- > 模板  -->  主机

模板：一些监控项，图形，触发器的集合

**💡监控流程**

1. 明确监控的内容

2. 内置的模板中是否有内容的实现

3. 如果没有，只能自定义

4. 编写采集数据的命令程序实现

5. 修改agent 配置，添加自定义监控项

6. 创建模板

7. 在模板创建监控项

8. 主机上关联模板
---
#### **💡配置样例：监控TCP十一种状态机**

1. ✅Zabbix Agent定义监控项

```bash
vim /etc/zabbix/zabbix_agent2.d/Test.conf
#UserParameter=<key>,<shell command>
#写法一：每一个监控项都单独写
UserParameter=tcp_state_est,netstat -nat|awk '$NF ~ "ESTABLISHED"{state[$NF]++}END{for(i in state){print state[i]}}'
#写法二：合并写法，使用位置参数
UserParameter=tcp_state[*],/etc/zabbix/zabbix_agentd.conf2.d/tcp_state.sh $1
```

```shell
#shell脚本内容
vim tcp_state.sh
#!/bin/bash
#tcp_state.sh
netstat -nat|awk -v STATE=$1 '$NF ~ STATE{state[$NF]++}END{for(i in state){print state[i]}}'
[root@ZabbixSQL zabbix_agent2.d]#bash tcp_state.sh ESTABLISHED
4
chmod a+x tcp_state.sh 
```

2. ✅测试

```bash
①在Zabbix Agent 上执行测试
	#zabbix_agentd -t "在客户端定义的key名[arg1,arg2,...]"
zabbix_agent2 -t tcp_state[ESTABLISHED]

②测试（在Zabbix Server上可以使用zabbix_get工具获取自定义监控项）
    #需要重启服务：systemctl restart zabbix-agent2.service
    #zabbix_get -s 客户端IP -p 10050 -k "在客户端定义的key名[arg1,arg2,...]"
	#zabbix_get -s 客户端IP -p 10050 -k "tcp_state[ESTABLISHED]"
zabbix_get -s 172.16.12.73 -p 10050 -k "tcp_state[ESTABLISHED]"
```

- ✏️注意

```bash'
如果不让文件tcp_state.sh 拥有所有权限，也就是不执行chmod a+x tcp_state.sh ，只是执行chmod u+x tcp_state.sh的话，
那么服务端测试会出现下列现象：权限拒绝，因为zabbix-server默认使用的用户是zabbix
[root@zabbix ~]# zabbix_get -s 172.16.12.73 -p 10050 -k "tcp_state[ESTABLISHED]"
sh: line 1: /etc/zabbix/zabbix_agent2.d/tcp_state.sh: Permission denied

解决方案：方式一
#注：此方式在zabbix-agent2上失败，zabbix-agent2也没有AllowRoot选项
vim /lib/systemd/system/zabbix-agentd.service
    #注释默认的用户和组
    #User=zabbix
    #Group=zabbix
vim /etc/zabbix/zabbix_agentd.conf
	AllowRoot=1
systemctl daemon-reload
systemctl restart zabbix-agentd.service
ps -aux | grep zabbix

解决方案：方式二，sudo授权(推荐)
vim /etc/sudoers
zabbix ALL=(ALL) NOPASSWD: ALL
vim /etc/zabbix/zabbix_agent2.d/Test.conf
UserParameter=tcp_state[*],sudo /etc/zabbix/zabbix_agentd.conf2.d/tcp_state.sh $1
#测试：zabbix_get -s 172.16.12.73 -p 10050 -k "tcp_state[ESTABLISHED]"
```

```bash
## 选项：AllowRoot
#    允许代理以 'root' 身份运行。如果禁用并且代理由 'root' 启动，代理将尝试切换到由User配置选项指定的用户。
#    如果在普通用户下启动，则没有效果。
#    0 - 不允许
#    1 - 允许
#
# 必需：否
# 默认值：
# AllowRoot=0
```


3. ✅模板的创建和添加（一个一个添加）

![image](https://github.com/user-attachments/assets/542f44b1-00f5-4281-bc2d-8a0ea5fdb59f)
#### **💡导出模板**
```yaml
zabbix_export:
  version: '6.0'
  date: '2025-03-05T02:08:56Z'
  groups:
    - uuid: dc579cd7a1a34222933f24f52a68bcd8
      name: 'Linux servers'
  templates:
    - uuid: 6b06e53f978b41beb3a49a772db1289c
      template: TCP-Status
      name: TCP-Status
      groups:
        - name: 'Linux servers'
      items:
        - uuid: 374aedeeefe3451db335e76fca221930
          name: 'TCP CLOSE_WAIT'
          key: 'tcp_state[CLOSE_WAIT]'
          delay: '30'
        - uuid: 843b3519904740f0b04ff2ac032334ae
          name: 'TCP CLOSING'
          key: 'tcp_state[CLOSING]'
          delay: '30'
        - uuid: d17fdd85f6954b168bad3c81ae8854c5
          name: 'TCP ESTABLISHED'
          key: 'tcp_state[ESTABLISHED]'
          delay: '30'
        - uuid: 68b3b146b894495eab0d9849feb9509c
          name: 'TCP FIN_WAIT1'
          key: 'tcp_state[FIN_WAIT1]'
          delay: '30'
        - uuid: a619f4cd40db446dabd314d45462ba5c
          name: 'TCP FIN_WAIT2'
          key: 'tcp_state[FIN_WAIT2]'
          delay: '30'
        - uuid: de5b5f73ecb44322b1d743d2e90456d2
          name: 'TCP LAST_ACK'
          key: 'tcp_state[LAST_ACK]'
          delay: '30'
        - uuid: 948838a852e44f8490be3a06d443d635
          name: 'TCP LISTEN'
          key: 'tcp_state[LISTEN]'
          delay: '30'
        - uuid: 4013c0ec33c84d2bbbb29b59d8dbd3a9
          name: 'TCP SYN_RECV'
          key: 'tcp_state[SYN_RECV]'
          delay: '30'
        - uuid: 0feb79afc75945ceac77da9c3434c985
          name: 'TCP SYN_SENT'
          key: 'tcp_state[SYN_SENT]'
          delay: '30'
        - uuid: ed2ff7cbfa7a4b9aac290b1cbd23f777
          name: 'TCP TIME_WAIT'
          key: 'tcp_state[TIME_WAIT]'
          delay: '30'
        - uuid: 658e53859d384a4fa9b273c1b0323fed
          name: 'TCP UNKNOWN'
          key: 'tcp_state[UNKNOWN]'
          delay: '30'
```
![image](https://github.com/user-attachments/assets/8ec9ddd1-cd18-4aa0-90da-3c5830b060b7)

