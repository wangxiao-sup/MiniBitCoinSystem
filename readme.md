# MiniBitCoinSystem

### 节点配置：

在启动docker容器时，先启动server1，然后server2，最后client1，这样节点的ip为如下：

server1节点ip：172.17.0.2；

server2节点ip：172.17.0.3；

client1节点ip：172.17.0.4；



### 运行：

* 先运行server1节点的Server.py

```shell
python Server.py
```

* 运行server2节点的Server.py

```shell
python Server.py
```

* 运行client1节点的Client.py

```shell
python Client.py
```