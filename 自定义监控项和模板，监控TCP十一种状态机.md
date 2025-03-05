### 3.2.3 范列：自定义监控项和模板，监控TCP十一种状态机

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
**💡配置样例：监控TCP十一种状态机**

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
