# ELK Docker与本地话部署
* [1. 安装 JDK](#安装JDK)
* [2. 安装 Redis](#安装Redis)
* [3. 安装 Filebeat](#安装Filebeat)
* [4. 安装 Logstash](#安装Logstash)
* [5. 配置 Logstash](#配置Logstash)
* [6. 安装 Logstash-forwarder](#安装Logstash-forwarder)
* [7. 安装 Elasticsearch](#安装Elasticsearch)
* [8. 安装 Kibana](#安装Kibana)
* [9. 安装 Nginx](#安装Nginx)
* [10. 最终验证](#最终验证)

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
rpm --import http://packages.elastic.co/GPG-KEY-elasticsearch
yum install java-1.8.0-openjdk
yum install -y redis
yum install -y filebeat
yum install -y logstash
yum install -y logstash-forwarder
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
wget https://artifacts.elastic.co/downloads/beats/filebeat/filebeat-7.8.0-linux-x86_64.tar.gz
tar -xzvf filebeat-7.8.0-darwin-x86_64.tar.gz
mv filebeat-7.8.0-darwin-x86_64 /usr/local/filebeat
cd /usr/local/filebeat
# 修改filebeat.yml
./filebeat setup
./filebeat -e
```

## 安装Logstash
```bash
wget https://download.elastic.co/logstash/logstash/logstash-2.1.1.tar.gz
tar xzvf logstash-2.1.1.tar.gz
mv logstash-2.1.1 /usr/local/logstash
/usr/local/logstash/bin/logstash -e 'input { stdin { } } output { stdout {} }'
/usr/local/logstash/bin/logstash -f ./logstash.conf
```

## 安装Elasticsearch
```
wget https://download.elasticsearch.org/elasticsearch/release/org/elasticsearch/distribution/tar/elasticsearch/2.1.0/elasticsearch-2.1.0.tar.gz
tar -xzvf elasticsearch-2.1.0.tar.gz
mv elasticsearch-2.1.0 /usr/local/elasticsearch
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
#wget https://download.elastic.co/kibana/kibana/kibana-4.3.0-linux-x64.tar.gz 
wget https://artifacts.elastic.co/downloads/kibana/kibana-5.4.0-linux-x86_64.tar.gz
tar xzvf kibana-5.4.0-linux-x86_64.tar.gz
mv kibana-5.4.0-linux-x86_64 /usr/local/kibana
# 修改kibana.yml文件
# 安装screen,以便于kibana在后台运行（当然也可以不用安装，用其他方式进行后台启动）
yum -y install screen
screen ./bin/kibana
#./bin/kibana
netstat -antp |grep 5601
curl localhost:5601 
```

## 安装Nginx
```bash
vi /etc/nginx/nginx.conf
# include /etc/nginx/conf.d/*conf_  
# 启动 Nginx 服务  
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


* [elk-stack](https://www.elastic.co/elk-stack)
* [ELK搭建篇](https://www.cnblogs.com/cheyunhua/p/11238489.html)
* [集中式日志系统 ELK 协议栈详解](https://developer.ibm.com/zh/articles/os-cn-elk/)

