# ELK Docker与本地部署
* [1. 安装 JDK](#安装JDK)
* [2. 安装 Redis](#安装Redis)
* [3. 安装 Filebeat](#安装Filebeat)
* [4. 安装 Logstash](#安装Logstash)
* [5. 配置 Logstash](#配置Logstash)
* [6. 安装 Elasticsearch](#安装Elasticsearch)
* [7. 安装 Kibana](#安装Kibana)
* [8. 安装 Nginx](#安装Nginx)
* [9. 最终验证](#最终验证)
* [10.redis 集群部署](#部署redis主从+哨兵)

# ELK结构框架
![](https://s2.ax1x.com/2020/01/09/lWqbPH.png)
* Elasticsearch是一个分布式搜索分析引擎，稳定、可水平扩展、易于管理是它的主要设计初衷;
* Logstash是一个灵活的数据收集、加工和传输的管道软件;
* Kibana是一个数据可视化平台，可以通过将数据转化为酷炫而强大的图像而实现与数据的交互
* 将三者的收集加工，存储分析和可视转化整合在一起就形成了ELK;  

## 基本流程
1. filebeat 或 Logstash-Shipper获取日志信息发送到redis。
2. Redis在此处的作用是防止ElasticSearch服务异常导致丢失日志，提供消息队列的作用。redis会立马传输到ES。
3. logstash是读取Redis中的日志信息发送给ElasticSearch。
4. ElasticSearch提供日志存储和检索。
5. Kibana是ElasticSearch可视化界面插件。
6. 部署到服务器上之后通过Nginx端口转发与反向代理把服务暴露出去。

## 默认端口
* 5000: Logstash TCP input.
* 9200: Elasticsearch HTTP
* 9300: Elasticsearch TCP transport
* 5601: Kibana

Create an index pattern via the Kibana API:
```bash
$ curl -XPOST -D- 'http://localhost:5601/api/saved_objects/index-pattern' \
    -H 'Content-Type: application/json' \
    -H 'kbn-version: 7.8.0' \
    -u elastic:changeme \
    -d '{"attributes":{"title":"logstash-*","timeFieldName":"@timestamp"}}'
```

# 本地部署
## 安装JDK
`vi /etc/yum.repos.d/centos.repo` 添加base.repo文件里的内容
```bash
es_version=7.9.0
rpm --import http://packages.elastic.co/GPG-KEY-elasticsearch
yum install java-1.8.0-openjdk
yum install -y filebeat
yum install -y redis
yum install -y logstash
yum install -y elasticsearch
yum install -y kibana
yum install -y nginx httpd-tools
java -version
```

## 安装Redis
```python
## 这里使用的是redis-5.0.4，请根据实际情况选择合适的版本
redis_version=redis-5.0.4
wget http://download.redis.io/releases/$redis_version.tar.gz
tar -zxf $redis_version.tar.gz -C /usr/local 
mv /usr/local/$redis_version/ /usr/local/redis
cd /usr/local/redis
make MALLOC=libc
make
make install
PATH=/usr/local/redis/src:$PATH
redis-server redis.conf &
# 修改密码
# sed -i "s/# requirepass foobared/requirepass 123456/g" redis.conf
# sudo service redis restart
# 查看redis服务端口
netstat -lnp|grep redis
# 验证节点信息
redis-cli INFO|grep role
```

## 安装Filebeat
```bash
wget https://artifacts.elastic.co/downloads/beats/filebeat/filebeat-$es_version-linux-x86_64.tar.gz
tar -xzvf filebeat-$es_version-darwin-x86_64.tar.gz
mv filebeat-$es_version-darwin-x86_64 /usr/local/filebeat
cd /usr/local/filebeat
# 修改filebeat.yml
./filebeat setup
./filebeat -e
```

## 安装Logstash
```bash
wget https://artifacts.elastic.co/downloads/beats/logstash/logstash-$es_version-linux-x86_64.tar.gz
tar xzvf logstash-$es_version-linux-x86_64.tar.gz
mv logstash-$es_version /usr/local/logstash
/usr/local/logstash/bin/logstash -e 'input { stdin { } } output { stdout {} }'
/usr/local/logstash/bin/logstash -f ./logstash.conf
```

## 安装Elasticsearch
```bash
wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-$es_version-linux-x86_64.tar.gz
tar -xzvf elasticsearch-$es_version-linux-x86_64.tar.gz
mv elasticsearch-$es_version-linux-x86_64 /usr/local/elasticsearch
cat /etc/security/limits.conf | grep -v "#" | while read line
  do
    sed -i "s/${line}/ /"  /etc/security/limits.conf
  done
  echo 'root soft memlock unlimited' >> /etc/security/limits.conf
  echo 'root hard memlock unlimited' >> /etc/security/limits.conf
  echo 'root soft nofile 65536' >> /etc/security/limits.conf
  echo 'root hard nofile 65536' >> /etc/security/limits.conf
 # 关闭已有的可能启动的elasticsearch服务
  ps -aux | grep elasticsearch | grep -v "grep" | awk '{print $2}' | xargs kill -9
 cd /usr/local/elasticsearch/config/
  # 需要交互输入，慎重
  read -p "Input elasticsearch ip:" es_ip
  sed -i "s/network.host: 192.168.0.1/network.host: $es_ip/" elasticsearch.yml
  sed -i "s/ping.unicast.hosts: \[.*\]/ping.unicast.hosts: \[\"$es_ip:9300\"\]/" elasticsearch.yml
/usr/local/elasticsearch/bin/elasticsearch -d
# 看下是否成功
netstat -antp |grep 9200
curl http://127.0.0.1:9200/
```
利用API查看状态
`curl -i -XGET 'localhost:9200/_count?pretty'`
安装elasticsearch-head插件
`docker run -p 9100:9100 mobz/elasticsearch-head:5`
docker容器下载成功并启动以后，运行浏览器打开http://localhost:9100/
`curl 'localhost:9200/'`  

## 安装Kibana
```bash
wget https://artifacts.elastic.co/downloads/kibana/kibana-$es_version-linux-x86_64.tar.gz
tar xzvf kibana-$es_version-linux-x86_64.tar.gz
mv kibana-$es_version-linux-x86_64 /usr/local/kibana
# 修改kibana.yml文件
# 安装screen,以便于kibana在后台运行（当然也可以不用安装，用其他方式进行后台启动）
yum -y install screen
screen ./bin/kibana
#./bin/kibana
netstat -antp |grep 5601
curl localhost:5601 
```

## 安装Nginx
```python
## 下载安装包和解压缩
wget -c https://nginx.org/download/nginx-1.14.0.tar.gz
tar zxf nginx-1.14.0.tar.gz
cd nginx-1.14.0
## 编译安装
./configure --prefix=/etc/nginx --sbin-path=/usr/sbin/nginx --modules-path=/usr/lib64/nginx/modules --conf-path=/etc/nginx/nginx.conf --error-log-path=/var/log/nginx/error.log --http-log-path=/var/log/nginx/access.log --pid-path=/var/run/nginx.pid --lock-path=/var/run/nginx.lock --http-client-body-temp-path=/var/cache/nginx/client_temp --http-proxy-temp-path=/var/cache/nginx/proxy_temp --http-fastcgi-temp-path=/var/cache/nginx/fastcgi_temp --http-uwsgi-temp-path=/var/cache/nginx/uwsgi_temp --http-scgi-temp-path=/var/cache/nginx/scgi_temp --user=nginx --group=nginx --with-compat --with-file-aio --with-threads --with-http_addition_module --with-http_auth_request_module --with-http_dav_module --with-http_flv_module --with-http_gunzip_module --with-http_gzip_static_module --with-http_mp4_module --with-http_random_index_module --with-http_realip_module --with-http_secure_link_module --with-http_slice_module --with-http_ssl_module --with-http_stub_status_module --with-http_sub_module --with-http_v2_module --with-mail --with-mail_ssl_module --with-stream --with-stream_realip_module --with-stream_ssl_module --with-stream_ssl_preread_module --with-cc-opt='-O2 -g -pipe -Wall -Wp,-D_FORTIFY_SOURCE=2 -fexceptions -fstack-protector-strong --param=ssp-buffer-size=4 -grecord-gcc-switches -m64 -mtune=generic -fPIC' --with-ld-opt='-Wl,-z,relro -Wl,-z,now -pie'
make
make install
## 配置nginx 
vi /etc/nginx/nginx.conf
# include /etc/nginx/conf.d/*conf_  
# 启动 Nginx 服务  
nginx -t
nginx -s reload
sudo systemctl enable nginx
sudo systemctl start nginx
open http://IP:5601
```

## 最后验证
编辑nginx配置文件，修改以下内容（在http模块下添加）
```bash
log_format json '{"@timestamp":"$time_iso8601",'
             '"@version":"1",'
             '"client":"$remote_addr",'
             '"url":"$uri",'
             '"status":"$status",'
             '"domian":"$host",'
             '"host":"$server_addr",'
             '"size":"$body_bytes_sent",'
             '"responsetime":"$request_time",'
             '"referer":"$http_referer",'
             '"ua":"$http_user_agent"'
          '}';
# 修改access_log的输出格式为刚才定义的json 
access_log  logs/elk.access.log  json;
```
运行看看效果如何`logstash -f /etc/logstash/conf.d/full.conf`
运行看看效果如何`logstash -f /etc/logstash/conf.d/redis-out.conf`
因为ES保存日志是永久保存，所以需要定期删除一下日志，下面命令为删除指定时间前的日志  
`curl -X DELETE http://xx.xx.com:9200/logstash-*-`date +%Y-%m-%d -d "-$n days"`


# 部署redis主从+哨兵
## 结构图
![UH645d.png](https://s1.ax1x.com/2020/07/22/UH645d.png)

## 机器信息
| 服务器IP | redis端口 | 哨兵端口 | 服务器角色 | 网卡名称 | IP掩码位 |
| :----: | :----: | :----: | :----: | :----: | :----: |
| 172.21.0.9 | 6379 | 26379 | 主 | eno16777984 | 24 |
| 172.21.0.11 | 6379 | 26379 | 从 | eno16777984 | 24 |

## 部署nginx主备模式
这里使用` nginx `的主备模式
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
## 安装 Redis 服务
```python
# 设置开机自启动
chkconfig --add redis
chkconfig redis on
## 配置 Redis 主节点
appendonly yes                   
## 配置 Redis 从节点
slaveof 172.21.0.9 6379
```

## 启动 Redis 服务
注意：Redis 启动时一定要先启动 Master 节点，然后再 Slave！
```python
#  验证节点信息
#在主节点执行
redis-cli INFO|grep role
role:master
#从节点执行
redis-cli INFO|grep role
role:slave
#主节点上
redis-cli
127.0.0.1:6379> set name etf
OK
127.0.0.1:6379> get nam
#从节点上：
redis-cli
127.0.0.1:6379> get name
"etf"
127.0.0.1:6379> set city shanghai
(error) READONLY You can't write against a read only replica.
```

## 部署 Redis 哨兵模式
### 配置 Master 和 Slave 节点 相同的操作
```python
##创建哨兵数据目录
mkdir -p /var/redis/redis-sentinel
cd /usr/local/redis-5.0.4
cat sentinel.conf
```
```python
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
### 测试
关闭` 172.21.0.9（主）`的` app01 `应用，发现客户端请求流量会打到` 172.21.0.11（从）`的` app02 `上，服务可以正常访问；
关闭` 172.21.0.9（主）`的` redis01 `，发现客户端请求流量打到` 172.21.0.9（主）`的` app01 `上，这时` redis02 `由slave变成master，服务可以正常访问；
此时再启动redis01，redis01不会接管主成为master，即redis02还是主，master不会因为redis01的重启而飘移；


# 参考资料
* [elk-stack](https://www.elastic.co/elk-stack)
* [ELK搭建篇](https://www.cnblogs.com/cheyunhua/p/11238489.html)
* [集中式日志系统 ELK 协议栈详解](https://developer.ibm.com/zh/articles/os-cn-elk/)
* [grokdebug](https://grokdebug.herokuapp.com/)
* [死磕Elasticsearch方法论认知清单](https://blog.csdn.net/newtelcom/article/details/80224379)
* [ElasticSearch中文](https://www.elastic.co/guide/cn/index.html)
* [ElasticSearch中文社区](https://elasticsearch.cn/)