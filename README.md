# 部署开发辅助工具
:white_check_mark: Gitlab: 代码管理仓库

:white_check_mark: Gitlab-runner: gitlab中cicd的runner

:white_check_mark: Code-server: 浏览器版vscode

:white_check_mark: Registry: dockerhub仓库

:white_check_mark: Portainer: portainer容器管理

:white_check_mark: Logstash: 日志收集管道

:white_check_mark: Elasticsearch: 分布式搜索引擎

:white_check_mark: Filebeat: 日志收集客户端

:white_check_mark: Kibana: 数据展示界面

:white_check_mark: Redis: 分布式数据存储

:white_check_mark: Nginx: 端口转发与反向代理

:white_check_mark: Elasticsearch-HQ: ES集群管理

# 接口说明
* 8001: Gitlab root:hb123456
* 8003: Code-server root:hb123456
* 8004: Registry 
* 9000: Portainer 
* 5000: Logstash TCP input.
* 9200: Elasticsearch elastic:changeme
* 9300: Elasticsearch TCP transport
* 5601: Kibana elastic:changeme
* 6379: Redis
* 5001: ES-HQ

# Docker与本地部署
* [1. ELK结构框架](#ELK结构框架)
* [2. 基本流程](#基本流程)
* [3. 安装 JDK](#安装JDK)
* [4. 安装 Redis](#安装Redis)
* [5. 安装 Filebeat](#安装Filebeat)
* [6. 安装 Logstash](#安装Logstash)
* [7. 安装 Elasticsearch](#安装Elasticsearch)
* [8. 安装 Kibana](#安装Kibana)
* [9. 安装 Nginx](#安装Nginx)
* [10. 安装Gitlab-runner](#安装Gitlab-runner)
* [11. ES插件安装](#ES插件安装)
* [12. ElasticSearc-sql](#使用Logstash从MySQL中同步数据到ElasticSearch)
* [13. 最终验证](#最终验证)
* [14. redis 集群部署](#部署redis哨兵)
* [15. 注意事项](#注意事项)
* [16. 参考资料](#参考资料)

## ELK结构框架
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

## 安装JDK
`vi /etc/yum.repos.d/centos.repo` 添加base.repo文件里的内容
```bash
es_version=7.9.0
rpm --import https://artifacts.elastic.co/GPG-KEY-elasticsearch
yum install -y filebeat
yum install -y redis
yum install -y logstash
yum install -y elasticsearch
yum install -y kibana
yum install -y nginx httpd-tools
java -version
# 查看下XXX的安装目录
rpm -ql XXX
# 或者到官网下载最新的java jdk https://www.oracle.com/java/technologies/javase-downloads.html
```

## 安装Redis
```python
## 这里使用的是redis-5.0.4，请根据实际情况选择合适的版本
redis_version=redis-5.0.4
wget http://download.redis.io/releases/${redis_version}.tar.gz
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
wget https://artifacts.elastic.co/downloads/beats/filebeat/filebeat-${es_version}-linux-x86_64.tar.gz
tar -xzvf filebeat-${es_version}-linux-x86_64.tar.gz
mv filebeat-${es_version}-linux-x86_64 /usr/local/filebeat
cd /usr/local/filebeat
# 修改filebeat.yml
./filebeat setup
./filebeat -e
```

## 安装Logstash
```bash
wget https://artifacts.elastic.co/downloads/logstash/logstash-${es_version}.zip
unzip logstash-${es_version}.zip
mv logstash-${es_version} /usr/local/logstash
/usr/local/logstash/bin/logstash -e 'input { stdin { } } output { stdout {} }'
/usr/local/logstash/bin/logstash -f ./logstash.conf
```

## 安装Elasticsearch
```bash
wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-${es_version}-linux-x86_64.tar.gz
tar -xzvf elasticsearch-${es_version}-linux-x86_64.tar.gz
mv elasticsearch-${es_version}-linux-x86_64 /usr/local/elasticsearch
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
curl -i -XGET 'localhost:9200/_count?pretty'
netstat -antp |grep 9200
curl http://127.0.0.1:9200/
```

## 安装Kibana
```bash
wget https://artifacts.elastic.co/downloads/kibana/kibana-${es_version}-linux-x86_64.tar.gz
tar xzvf kibana-${es_version}-linux-x86_64.tar.gz
mv kibana-${es_version}-linux-x86_64 /usr/local/kibana
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
nginx_version=1.14.0
wget -c https://nginx.org/download/nginx-${nginx_version}.tar.gz
tar zxf nginx-${nginx_version}.tar.gz
cd nginx-${nginx_version}
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

## 安装Gitlab-runner
```
sudo curl -L --output /usr/local/bin/gitlab-runner https://gitlab-runner-downloads.s3.amazonaws.com/latest/binaries/gitlab-runner-linux-amd64
sudo chmod +x /usr/local/bin/gitlab-runner
#安装docker，可选，如果执行器选择docker，则需要安装，如果可以，最好装个docker加速器
curl -sSL https://get.docker.com/ | sh  
#添加一个普通用户权限，用来运行gitlab runner,然后运行gitlab runner
sudo useradd --comment 'GitLab Runner' --create-home gitlab-runner --shell /bin/bash
sudo gitlab-runner install --user=gitlab-runner --working-directory=/home/gitlab-runner
sudo gitlab-runner start
```
首次使用，需要进入容器内部注册
```
[root@localhost ~]# gitlab-runner register   #注册runner到gitlab
Runtime platform                                    arch=amd64 os=linux pid=12351 revision=d0b76032 version=12.0.2
Running in system-mode.                            
Please enter the gitlab-ci coordinator URL (e.g. https://gitlab.com/): 
http://server.muguayun.top:20080/
Please enter the gitlab-ci token for this runner:
yx6oVQYxrLxczyazysF9
Please enter the gitlab-ci description for this runner:
[localhost.localdomain]: canon_runner
Please enter the gitlab-ci tags for this runner (comma separated): 
gitlab-runner-01
Registering runner... succeeded                     runner=yx6oVQYx
Please enter the executor: docker, docker-ssh, ssh, docker-ssh+machine, parallels, shell, virtualbox, docker+machine, kubernetes: 
#设置runner运行方式(推荐选shell，更灵活)。 ⚠️ 如果这里选择docker，再打包时，runner内部会重新启动一个docker镜像，脚本内部命令会在重新启动的镜像内执行。
docker
Please enter the default Docker image (e.g. ruby:2.6):
centos:7
Runner registered successfully. Feel free to start it, but if it's running already the config should be automatically reloaded! 
[root@localhost ~]# gitlab-runner restart  #重启下gitlab runner
[root@localhost ~]# gitlab-runner list  #查看当前gitlab runner
Runtime platform                                    arch=amd64 os=linux pid=12379 revision=d0b76032 version=12.0.2
Listing configured runners                          ConfigFile=/etc/gitlab-runner/config.toml
gitlab-runner-01                                    Executor=docker Token=KAsxjVbByKauYnNMSKHY URL=http://192.168.31.130/
```
gitlab注册
```shell
# Git global setup
git config --global user.name "cbd"
git config --global user.email "2829969299@qq.com"
# Push an existing folder
git init
git remote add origin ssh://git@abc.git
git add .
git commit -m "Initial commit"
git push -u origin master
```
备注：
1. runner在运行时，默认使用 gitlab-runner用户。
2. 所以涉及到 使用ssh权限，需要把 gitlab-runner的公钥添加到部署服务器，免密登录。
3. 需要手动修改/home/gitlab-runner 文件夹权限 为 777。
4. gitlab runner配置文件在/etc/gitlab-runner/config.toml
5. ssh-keygen -t rsa -C "your.email@example.com" -b 4096

## ES插件安装
1. [HQ监控](https://github.com/royrusso/elasticsearch-HQ) 管理ES集群以及通过web界面来查询操作,支持SQL转DSL  
`docker run -p 5000:5000 elastichq/elasticsearch-hq`  
`http://es_user:es_password@es_ip:es_port`
2. [ik分词](https://github.com/medcl/elasticsearch-analysis-ik)  
`./bin/elasticsearch-plugin install https://github.com/medcl/elasticsearch-analysis-ik/releases/download/v${es_version}/elasticsearch-analysis-ik-${es_version}.zip`
3. [SQL](https://github.com/NLPchina/elasticsearch-sql) 通过sql语法进行查询的工具  
`./bin/elasticsearch-plugin install https://github.com/NLPchina/elasticsearch-sql/releases/download/${es_version}.0/elasticsearch-sql-${es_version}.0.zip`
4. [Cerebro](https://www.jianshu.com/p/433d821f9667) 查看ES集群堆内存使用率、CPU使用率、内存使用率、磁盘使用率。  
```bash
wget https://github.com/lmenezes/cerebro/releases/download/v${es_version}/cerebro-${es_version}.tgz
tar xzf cerebro-${es_version}.tgz
# 指定一个端口启动
cerebro-${es_version}/bin/cerebro -Dhttp.port=8088
```

## 使用Logstash从MySQL中同步数据到ElasticSearch
```bash
bin/logstash-plugin install logstash-input-jdbc
bin/logstash-plugin install logstash-output-elasticsearch
wget https://dev.mysql.com/get/Downloads/Connector-J/mysql-connector-java-5.1.46.zip --no-check-certificate
unzip mysql-connector-java-5.1.46.zip
# 这里面有一个MySQL依赖包jar，用于配置logstash里面的这个参数jdbc_driver_library
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

# 部署redis哨兵
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

# 注意事项
1. 如果使用registry所有服务器需要如下添加配置
```shell
 vim /etc/docker/daemon.json
 {
    "insecure-registries": [
        "server.abc.com:8004"     # 注意，此处的 host 需要对应 实际服务器.修改后需要重启docker服务
    ]
 }
```
2. filebeat/config/filebeat.yml 权限修改：`chmod go-w filebeat.yml`
3. elasticsearch/data要可写 权限修改：`chmod 777 elasticsearch/data`

Create an index pattern via the Kibana API:
```bash
$ curl -XPOST -D- 'http://localhost:5601/api/saved_objects/index-pattern' \
    -H 'Content-Type: application/json' \
    -H 'kbn-version: 7.8.0' \
    -u elastic:changeme \
    -d '{"attributes":{"title":"logstash-*","timeFieldName":"@timestamp"}}'
```

修改容器并更新为新的名字
```shell
    docker commit -p container image_name:tag  
    docker commit -p 02821380a8c5 code-server-3.1.1:ningboyinhang_image  
``` 

DSL
```json5
{
    "query":{
        "bool":{
            "must":[

            ],
            "must_not":[

            ],
            "should":[

            ]
        }
    },
    "aggs":{
        "my_agg":{
            "terms":{
                "field":"user",
                "size":10
            }
        }
    },
    "highlight":{
        "pre_tags":[
            "<em>"
        ],
        "post_tags":[
            "</em>"
        ],
        "fields":{
            "body":{
                "number_of_fragments":1,
                "fragment_size":20
            },
            "title":{

            }
        }
    },
    "size":20,
    "from":100,
    "_source":[
        "title",
        "id"
    ],
    "sort":[
        {
            "_id":{
                "order":"desc"
            }
        }
    ]
}
```

# 参考资料
* [Gitlab Runner介绍安装](https://www.jianshu.com/p/f5f4f2110277)
* [elk-stack](https://www.elastic.co/elk-stack)
* [grokdebug](https://grokdebug.herokuapp.com/)
* [死磕Elasticsearch方法论认知清单](https://blog.csdn.net/newtelcom/article/details/80224379)
* [ElasticSearch中文](https://www.elastic.co/guide/cn/index.html)
* [ElasticSearch中文社区](https://elasticsearch.cn/)
