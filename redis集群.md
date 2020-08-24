# 结构图

![UH645d.png](https://s1.ax1x.com/2020/07/22/UH645d.png)

# 机器信息

| 服务器IP | redis端口 | 哨兵端口 | 服务器角色 | 网卡名称 | IP掩码位 |
| :----: | :----: | :----: | :----: | :----: | :----: |
| 172.21.0.9 | 6379 | 26379 | 主 | eno16777984 | 24 |
| 172.21.0.11 | 6379 | 26379 | 从 | eno16777984 | 24 |

# 部署nginx

这里使用编译部署nginx，原因是编译安装可以自定义安装路径和相关模块，比如：`stream`。

## 安装nginx主要步骤：

```python
## 下载安装包和解压缩
wget -c https://nginx.org/download/nginx-1.14.0.tar.gz
tar zxf nginx-1.14.0.tar.gz
cd nginx-1.14.0
## 编译安装
./configure --prefix=/etc/nginx --sbin-path=/usr/sbin/nginx --modules-path=/usr/lib64/nginx/modules --conf-path=/etc/nginx/nginx.conf --error-log-path=/var/log/nginx/error.log --http-log-path=/var/log/nginx/access.log --pid-path=/var/run/nginx.pid --lock-path=/var/run/nginx.lock --http-client-body-temp-path=/var/cache/nginx/client_temp --http-proxy-temp-path=/var/cache/nginx/proxy_temp --http-fastcgi-temp-path=/var/cache/nginx/fastcgi_temp --http-uwsgi-temp-path=/var/cache/nginx/uwsgi_temp --http-scgi-temp-path=/var/cache/nginx/scgi_temp --user=nginx --group=nginx --with-compat --with-file-aio --with-threads --with-http_addition_module --with-http_auth_request_module --with-http_dav_module --with-http_flv_module --with-http_gunzip_module --with-http_gzip_static_module --with-http_mp4_module --with-http_random_index_module --with-http_realip_module --with-http_secure_link_module --with-http_slice_module --with-http_ssl_module --with-http_stub_status_module --with-http_sub_module --with-http_v2_module --with-mail --with-mail_ssl_module --with-stream --with-stream_realip_module --with-stream_ssl_module --with-stream_ssl_preread_module --with-cc-opt='-O2 -g -pipe -Wall -Wp,-D_FORTIFY_SOURCE=2 -fexceptions -fstack-protector-strong --param=ssp-buffer-size=4 -grecord-gcc-switches -m64 -mtune=generic -fPIC' --with-ld-opt='-Wl,-z,relro -Wl,-z,now -pie'
make
make install
```
```python
## 配置nginx 
cd /etc/nginx/
## 启动nginx
mkdir -p /etc/nginx/http.d
mkdir -p /etc/nginx/stream.d
nginx -t
nginx
```
# 配置F5/Nginx

这里使用` nginx `的主备模式，可参考[传送门01](https://blog.csdn.net/sinat_32473083/article/details/103164368)和[传送门02](https://www.jianshu.com/p/03864a6634a9)配置信息如下：

```python
cd /etc/nginx/http.d
cat changsha-rpa.conf

upstream testproxy {
      server 172.21.0.9:58780;  
      server 172.21.0.11:58780 backup;
}
server {
        listen       58780;
        server_name  localhost;
        location / {
            proxy_pass   http://testproxy;
        }
         access_log  /var/log/changsha-rpa/access.log main;
}
```
说明⚠️：58780是docker应用的映射端口！

# 配置应用服务

## 部署nginx

这里的nginx作用是代理两台应用服务器上的redis，实现redis和应用服务的高可用！

nginx的安装部署如上，两台应用服务器均需要安装！

注意⚠️：两台应用服务器的nginx配置和服务配置文件是一样的～

```python
## 代理服务配置
cd /etc/nginx/stream.d
cat test-redis.conf
upstream testproxy {
      server 172.21.0.9:6379;
      server 172.21.0.11:6379 backup;
     }
server {
        listen       56379;
        proxy_pass testproxy;
        access_log  /var/log/changsha-rpa/myservic.log  proxy;
      }
```
```python
## 平滑重启nginx
nginx -t
nginx -s reload
```
## 部署redis主从+哨兵

### 安装 Redis 服务

注意⚠️：两台机器都需要部署！

```python
## 这里使用的是redis-5.0.4，请根据实际情况选择合适的版本
wget http://download.redis.io/releases/redis-5.0.4.tar.gz
tar -zxf redis-5.0.4.tar.gz -C /usr/local 
cd /usr/local/redis-5.0.4
make MALLOC=libc
make
make install
```
### 拷贝相关执行和配置文件

```python
mkdir -p /usr/local/redis/bin/
cd /usr/local/redis-5.0.4/src
cp redis-benchmark redis-check-aof redis-check-rdb redis-cli redis-server redis-sentinel /usr/local/redis/bin/
cd ../
cp redis.conf /etc/
```
### 添加 Redis 启动脚本

```python
cat /etc/init.d/redis 

#!/bin/bash
#chkconfig: 2345 10 90
#description: Start and Stop redis
REDISPORT=6379
EXEC=/usr/local/redis/bin/redis-server
REDIS_CLI=/usr/local/redis/bin/redis-cli
PIDFILE=/var/run/redis.pid
CONF="/etc/redis.conf"
case "$1" in
start)
if [ -f $PIDFILE ]
then
echo "$PIDFILE exists, process is already running or crashed"
else
echo "Starting Redis server..."
$EXEC $CONF
fi
if [ "$?"="0" ]
then
echo "Redis is running..."
fi
;;
stop)
if [ ! -f $PIDFILE ]
then
echo "$PIDFILE does not exist, process is not running"
else
PID=$(cat $PIDFILE)
echo "Stopping ..."
$REDIS_CLI -p $REDISPORT SHUTDOWN
while [ -x ${PIDFILE} ]
do
echo "Waiting for Redis to shutdown ..."
sleep 1
done
echo "Redis stopped"
fi
;;
restart|force-reload)
${0} stop
${0} start
;;
*)
echo "Usage: /etc/init.d/redis {start|stop|restart|force-reload}" >&2
exit 1
esac
```
### 添加执行权限

```python
chmod 755 /etc/init.d/redis
```
### 设置开机自启动

```python
chkconfig --add redis
chkconfig redis on
```
### 创建 Redis 状态日志

```python
mkdir /var/log/redis/
touch /var/log/redis/redis.log
```
### 配置 Redis 主从

#### 配置 Redis 主节点

```python
cat /etc/redis.conf |egrep -v '#|^$'
bind 0.0.0.0
protected-mode yes
port 6379
tcp-backlog 511
timeout 0
tcp-keepalive 300
daemonize yes
supervised no
pidfile /var/run/redis.pid
loglevel notice
logfile /var/log/redis/redis.log
databases 16
always-show-logo yes
##启用RDB快照功能，默认就是启用的
save 900 1                   
save 300 10
##即在多少秒的时间内，有多少key被改变的数据添加到.rdb文件里
save 60 10000                
##默认就会开启
slave-serve-stale-data yes  
slave-read-only  yes
stop-writes-on-bgsave-error yes
rdbcompression yes
rdbchecksum yes
##快照文件名称
dbfilename dump.rdb             
##redis数据目录
dir /var/redis/redis            
replica-serve-stale-data yes
replica-read-only yes
repl-diskless-sync no
repl-diskless-sync-delay 5
repl-disable-tcp-nodelay no
replica-priority 100
lazyfree-lazy-eviction no
lazyfree-lazy-expire no
lazyfree-lazy-server-del no
replica-lazy-flush no
##启用AOF持久化方式
appendonly yes                   
##AOF文件的名称，默认为appendonly.aof
appendfilename "appendonly.aof"  
##每秒钟强制写入磁盘一次，在性能和持久化方面做了很好的折中，是受推荐的方式。
appendfsync everysec             
no-appendfsync-on-rewrite no
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb
aof-load-truncated yes
aof-use-rdb-preamble yes
lua-time-limit 5000
slowlog-log-slower-than 10000
slowlog-max-len 128
latency-monitor-threshold 0
notify-keyspace-events ""
hash-max-ziplist-entries 512
hash-max-ziplist-value 64
list-max-ziplist-size -2
list-compress-depth 0
set-max-intset-entries 512
zset-max-ziplist-entries 128
zset-max-ziplist-value 64
hll-sparse-max-bytes 3000
stream-node-max-bytes 4096
stream-node-max-entries 100
activerehashing yes
client-output-buffer-limit normal 0 0 0
client-output-buffer-limit replica 256mb 64mb 60
client-output-buffer-limit pubsub 32mb 8mb 60
hz 10
dynamic-hz yes
aof-rewrite-incremental-fsync yes
rdb-save-incremental-fsync yes
```
说明：另一个从节点redis-slave的 redis.conf 配置和上面基本差不多，只是多了下面一行配置：` slaveof 172.21.0.9 6379 `

#### 创建 Redis 主节点数据目录

```python
mkdir -p /var/redis/redis
```

#### 配置 Redis 从节点

```python
cat /etc/redis.conf |egrep -v '#|^$'
bind 0.0.0.0
protected-mode yes
port 6379
tcp-backlog 511
timeout 0
tcp-keepalive 300
daemonize yes
supervised no
pidfile /var/run/redis.pid
loglevel notice
logfile /var/log/redis/redis.log
databases 16
always-show-logo yes
save 900 1
save 300 10
save 60 10000
slave-serve-stale-data yes
slave-read-only  yes
slaveof 172.21.0.9 6379
stop-writes-on-bgsave-error yes
rdbcompression yes
rdbchecksum yes
dbfilename dump.rdb
dir /var/redis/redis
replica-serve-stale-data yes
replica-read-only yes
repl-diskless-sync no
repl-diskless-sync-delay 5
repl-disable-tcp-nodelay no
replica-priority 100
lazyfree-lazy-eviction no
lazyfree-lazy-expire no
lazyfree-lazy-server-del no
replica-lazy-flush no
appendonly yes
appendfilename "appendonly.aof"
appendfsync everysec
no-appendfsync-on-rewrite no
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb
aof-load-truncated yes
aof-use-rdb-preamble yes
lua-time-limit 5000
slowlog-log-slower-than 10000
slowlog-max-len 128
latency-monitor-threshold 0
notify-keyspace-events ""
hash-max-ziplist-entries 512
hash-max-ziplist-value 64
list-max-ziplist-size -2
list-compress-depth 0
set-max-intset-entries 512
zset-max-ziplist-entries 128
zset-max-ziplist-value 64
hll-sparse-max-bytes 3000
stream-node-max-bytes 4096
stream-node-max-entries 100
activerehashing yes
client-output-buffer-limit normal 0 0 0
client-output-buffer-limit replica 256mb 64mb 60
client-output-buffer-limit pubsub 32mb 8mb 60
hz 10
dynamic-hz yes
aof-rewrite-incremental-fsync yes
rdb-save-incremental-fsync yes
```

#### 创建 Redis 从节点数据目录

```python
mkdir -p /var/redis/redis
```
### 启动 Redis 服务

注意：Redis 启动时一定要先启动 Master 节点，然后再 Slave！

```python
# 启动redis
/etc/init.d/redis start
Starting Redis server...
Redis is running...
# 查看redis服务端口
netstat -lnp|grep redis
tcp        0      0 0.0.0.0:6379            0.0.0.0:*               LISTEN      3551/redis-server 0
```

### 验证节点信息

```python
#在主节点执行
redis-cli INFO|grep role
role:master
#从节点执行
redis-cli INFO|grep role
role:slave
```
```python
##主节点上：
redis-cli
127.0.0.1:6379> set name etf
OK
127.0.0.1:6379> get nam
##两台从节点上：
# redis-cli
127.0.0.1:6379> get name
"etf"
127.0.0.1:6379> set city shanghai
(error) READONLY You can't write against a read only replica.
```

## 部署 Redis 哨兵模式

### 配置 Master 和 Slave 节点

注意：两者的配置文件内容是一样的！

```python
##创建哨兵数据目录
mkdir -p /var/redis/redis-sentinel
```

```python
cd /usr/local/redis-5.0.4 && mv sentinel.conf sentinel.conf_20200416
```
```python
cat sentinel.conf

protected-mode no
##后台运行
daemonize yes

sentinel deny-scripts-reconfig yes
##指定监控的master地址和端口号，1表示多个sentinel同意才进行主从切换
sentinel monitor mymaster 172.21.0.9 6379 2
##超过多少毫秒连接不到master认定为master死掉
sentinel down-after-milliseconds mymaster 5000
##当主从切换多久后认为主从切换失败
sentinel failover-timeout mymaster 15000

sentinel auth-pass mymaster Hangzhou@123

# Generated by CONFIG REWRITE

port 26379

dir "/var/redis/redis-sentinel"
##日志文件保存路径
logfile "/var/log/redis_sentinel.log" 
sentinel config-epoch mymaster 1

sentinel leader-epoch mymaster 1

sentinel known-slave mymaster 172.21.0.11 6379
sentinel current-epoch 1

sentinel announce-ip "172.21.0.9"
```

### 依次启动哨兵sentinel

首先启动master  然后slave～

```python
redis-sentinel /usr/local/redis-5.0.4/sentinel.conf &
```
启动完毕后可以用如下命令查看哨兵信息：

```python
redis-cli -p 26379 INFO Sentinel 
# Sentinel
sentinel_masters:1
sentinel_tilt:0
sentinel_running_scripts:0
sentinel_scripts_queue_length:0
sentinel_simulate_failure_flags:0
master0:name=mymaster,status=ok,address=172.21.0.9:6379,slaves=2,sentinels=4
```
# 测试

## 情形一：关闭app01

关闭` 172.21.0.9（主）`的` app01 `应用，发现客户端请求流量会打到` 172.21.0.11（从）`的` app02 `上，服务可以正常访问；

## 情形二：关闭redis01

关闭` 172.21.0.9（主）`的` redis01 `，发现客户端请求流量打到` 172.21.0.9（主）`的` app01 `上，这时` redis02 `由slave变成master，服务可以正常访问；

## 情形三：启动情形二中redis01

redis01不会接管主成为master，即redis02还是主，master不会因为redis01的重启而飘移；












