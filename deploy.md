# ELK具体安装过程如下
* [1. 安装 JDK](#1. 安装 JDK)
* [2. [安装 Elasticsearch](#2. 安装 Elasticsearch)
* [3. 安装 Kibana](#3. 安装 Kibana)
* [4. 安装 Nginx](#4. 安装 Nginx)
* [5. 安装 Logstash](#5. 安装 Logstash)
* [6. 配置 Logstash](#6. 配置 Logstash)
* [7. 安装 Logstash-forwarder](#7. 安装 Logstash-forwarder)
* [8. 最终验证](#8. 最终验证)

## 1. 安装 JDK
`vi /etc/yum.repos.d/centos.repo` 添加如下:
```bash
[base]
name=CentOS-$releasever - Base
mirrorlist=http://mirrorlist.centos.org/?release=$releasever&arch=$basearch&repo=os&infra=$infra
#baseurl=http://mirror.centos.org/centos/$releasever/os/$basearch/
gpgcheck=1
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-CentOS-7
#released updates
[updates]
name=CentOS-$releasever - Updates
mirrorlist=http://mirrorlist.centos.org/?release=$releasever&arch=$basearch&repo=updates&infra=$infra
#baseurl=http://mirror.centos.org/centos/$releasever/updates/$basearch/
gpgcheck=1
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-CentOS-7
```
`yum install java-1.8.0-openjdk`
`java -version`

## 2. 安装 Elasticsearch
`wget https://download.elasticsearch.org/elasticsearch/release/org/elasticsearch/distribution/tar/elasticsearch/2.1.0/elasticsearch-2.1.0.tar.gz`
`tar xzvf elasticsearch-2.1.0.tar.gz`
`pwd`
_/home/elk/elasticsearch-2.1.0_
`ls`
_bin config lib LICENSE.txt NOTICE.txt README.textile_
`cd config`
`vi elasticsearch.yml`
找到network.host一行，修改成以下：
_network.host: localhost_
``../bin/elasticsearch`
`curl 'localhost:9200/'`
```bash
{
    "name" : "Surge",
    "cluster_name" : "elasticsearch",
    "version" : {
        "number" : "2.1.0",
        "build_hash" : "72cd1f1a3eee09505e036106146dc1949dc5dc87",
        "build_timestamp" : "2015-11-18T22:40:03Z",
        "build_snapshot" : false,
        "lucene_version" : "5.3.1"
    }
    "tagline" : "You Know, for Search"
}
```

## 3. 安装 Kibana
`wget https://download.elastic.co/kibana/kibana/kibana-4.3.0-linux-x64.tar.gz`
`tar xzvf kibana-4.3.0-linux-x64.tar.gz`
`pwd`
_/home/elk/kibana-4.3.0-linux-x64_
`ls`
_bin config installedPlugins LICENSE.txt node node_modules optimize package.json README.txt src webpackShims_
`cd config`
`vi kibana.yml`
_server.host:"localhost”_
`../bin/kibana`
`curl localhost:5601`

## 4. 安装 Nginx
`vi /etc/yum.repos.d/nginx.repo`
```
[nginx]
name=nginx repo
baseurl=http://nginx.org/packages/centos/7/$basearch/
gpgcheck=0
enabled=1
```
`yum install nginx httpd-tools`
`vi /etc/nginx/nginx.conf`
_include /etc/nginx/conf.d/*conf_
`vi /etc/nginx/conf.d/kibana.conf`
```log
server {
 listen 80;

 server_name example.com;

 location / {
 proxy_pass http://localhost:5601;
 proxy_http_version 1.1;
 proxy_set_header Upgrade $http_upgrade;
 proxy_set_header Connection 'upgrade';
 proxy_set_header Host $host;
 proxy_cache_bypass $http_upgrade;
 }
｝
```
启动 Nginx 服务
`sudo systemctl enable nginx`
`sudo systemctl start nginx`
`http://FQDN 或者 http://IP`

## 5. 安装 Logstash
`wget https://download.elastic.co/logstash/logstash/logstash-2.1.1.tar.gz`
`tar xzvf logstash-2.1.1.tar.gz`
`pwd`
_/home/elk/logstash-2.1.1_
`ls`
_bin CHANGELOG.md CONTRIBUTORS Gemfile Gemfile.jruby-1.9.lock lib LICENSE NOTICE.TXT vendor_
`cd bin`
`./logstash -e 'input { stdin { } } output { stdout {} }'`

## 6. 配置 Logstash
```log
input {
}
filter {
}
output {
}
```

配置 SSL
`mkdir -p /etc/pki/tls/certs etc/pki/tls/private`
`vi /etc/ssl/openssl.cnf`
找到 [v3_ca] 段，添加下面一行，保存退出。
_subjectAltName = IP: logstash_server_ip_
`cd /etc/pki/tls`
`sudo openssl req -config /etc/ssl/openssl.cnf -x509 -days 3650 -batch -nodes -newkey rsa:2048 -keyout
         private/logstash-forwarder.key -out certs/logstash-forwarder.crt`

这里产生的 logstash-forwarder.crt 文件会在下一节安装配置 Logstash-forwarder 的时候使用到。

配置 Logstash 管道文件

`cd /home/elk/logstash-2.1.1`
`mkdir conf`
`vi simple.conf`
```log
input {
 lumberjack {
 port => 5043
 type => "logs"
 ssl_certificate => "/etc/pki/tls/certs/logstash-forwarder.crt"
 ssl_key => "/etc/pki/tls/private/logstash-forwarder.key"
 }
}
filter {
 grok {
 match => { "message" => "%{COMBINEDAPACHELOG}" }
 }
 date {
 match => [ "timestamp" , "dd/MMM/yyyy:HH:mm:ss Z" ]
 }
}
output {
 elasticsearch { hosts => ["localhost:9200"] }
 stdout { codec => rubydebug }
}
```
启动 Logstsh
`cd /home/elk/logstash-2.1.1/bin`
`./logstash -f ../conf/simple.conf`


在 CentOS 7.1 上配置 Logstash，只有一步配置 SSL 是稍微有点不同，其他全部一样。
`vi /etc/pki/tls/openssl.cnf`
找到 [v3_ca] 段，添加下面一行，保存退出。
_subjectAltName = IP: logstash_server_ip_
`cd /etc/pki/tls`
`sudo openssl req -config /etc/pki/tls/openssl.cnf -x509 -days 3650 -batch -nodes -newkey
         rsa:2048 -keyout private/logstash-forwarder.key -out certs/logstash-forwarder.crt`

## 7. 安装 Logstash-forwarder
配置 Logstash-forwarder 安装源
`rpm --import http://packages.elastic.co/GPG-KEY-elasticsearch`
`vi /etc/yum.repos.d/logstash-forwarder.repo`
加入以下内容：
```log
[logstash-forwarder]
name=logstash-forwarder repository
baseurl=http://packages.elastic.co/logstashforwarder/centos
gpgcheck=1
gpgkey=http://packages.elasticsearch.org/GPG-KEY-elasticsearch
enabled=1
```
`yum -y install logstash-forwarder`

## 8. 最后验证
`open http://IP:5601`




