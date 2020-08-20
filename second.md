# [ELK搭建篇](https://www.cnblogs.com/cheyunhua/p/11238489.html)

    Centos6.5 两台  
    IP：192.168.1.202 安装： elasticsearch、logstash、Kibana、Nginx、Http、Redis  
    192.168.1.201 安装:  logstash
    
## 安装elasticsearch

    rpm --import https://artifacts.elastic.co/GPG-KEY-elasticsearch
    vim /etc/yum.repos.d/elasticsearch.repo
在elasticsearch.repo文件中添加如下内容
```log
[elasticsearch-5.x]
name=Elasticsearch repository for 5.x packages
baseurl=https://artifacts.elastic.co/packages/5.x/yum
gpgcheck=1
gpgkey=https://artifacts.elastic.co/GPG-KEY-elasticsearch
enabled=1
autorefresh=1
type=rpm-md
```
```bash
yum install -y elasticsearch
yum install -y java-1.8.0-openjdk
```
创建elasticsearch data的存放目录，并修改该目录的属主属组
```bash
mkdir -p /data/es-data   # (自定义用于存放data数据的目录)
chown -R elasticsearch:elasticsearch /data/es-data
chown -R elasticsearch:elasticsearch /var/log/elasticsearch/
```
```bash
vim /etc/elasticsearch/elasticsearch.yml
# 找到配置文件中的cluster.name，打开该配置并设置集群名称
cluster.name: demon
# 找到配置文件中的node.name，打开该配置并设置节点名称
node.name: elk-1
# 修改data存放的路径
path.data: /data/es-data
# 修改logs日志的路径
path.logs: /var/log/elasticsearch/
# 配置内存使用用交换分区
bootstrap.memory_lock: true
# 监听的网络地址
network.host: 0.0.0.0
# 开启监听的端口
http.port: 9200
# 增加新的参数，这样head插件可以访问es (5.x版本，如果没有可以自己手动加)
http.cors.enabled: true
http.cors.allow-origin: "*"
```
启动服务
```bash
/etc/init.d/elasticsearch start
# Starting elasticsearch: Java HotSpot(TM) 64-Bit Server VM warning: INFO: os::commit_memory(0x0000000085330000, 2060255232, 0) failed; error='Cannot allocate memory' (errno=12)
# There is insufficient memory for the Java Runtime Environment to continue.
# Native memory allocation (mmap) failed to map 2060255232 bytes for committing reserved memory.
# An error report file with more information is saved as:
# /tmp/hs_err_pid2616.log
#                 [FAILED]
#这个报错是因为默认使用的内存大小为2G，虚拟机没有那么多的空间
修改参数：
vim /etc/elasticsearch/jvm.options
-Xms512m
-Xmx512m
再次启动
/etc/init.d/elasticsearch start
创建开机自启动服务
# chkconfig elasticsearch on
```
注意事项
```bash
需要修改几个参数，不然启动会报错
vim /etc/security/limits.conf
在末尾追加以下内容（elk为启动用户，当然也可以指定为*）
elk soft nofile 65536
elk hard nofile 65536
elk soft nproc 2048
elk hard nproc 2048
elk soft memlock unlimited
elk hard memlock unlimited
继续再修改一个参数
vim /etc/security/limits.d/90-nproc.conf
将里面的1024改为2048（ES最少要求为2048）
*          soft    nproc     2048
另外还需注意一个问题（在日志发现如下内容，这样也会导致启动失败，这一问题困扰了很久）
[2017-06-14T19:19:01,641][INFO ][o.e.b.BootstrapChecks    ] [elk-1] bound or publishing to a non-loopback or non-link-local address, enforcing bootstrap checks
[2017-06-14T19:19:01,658][ERROR][o.e.b.Bootstrap          ] [elk-1] node validation exception
[1] bootstrap checks failed
[1]: system call filters failed to install; check the logs and fix your configuration or disable system call filters at your own risk
解决：修改配置文件，在配置文件添加一项参数（目前还没明白此参数的作用）
vim /etc/elasticsearch/elasticsearch.yml 
bootstrap.system_call_filter: false
看下是否成功
netstat -antp |grep 9200
curl http://127.0.0.1:9200/
```

利用API查看状态
`curl -i -XGET 'localhost:9200/_count?pretty'`
```log 
    HTTP/1.1 200 OK
    content-type: application/json; charset=UTF-8
    content-length: 95
    {
      "count" : 0,
      "_shards" : {
        "total" : 0,
        "successful" : 0,
        "failed" : 0
      }
    }
```
安装elasticsearch-head插件
`docker run -p 9100:9100 mobz/elasticsearch-head:5`
docker容器下载成功并启动以后，运行浏览器打开http://localhost:9100/

# 安装Logstash环境：
```bash
rpm --import https://artifacts.elastic.co/GPG-KEY-elasticsearch
yum install -y logstash
查看下logstash的安装目录
rpm -ql logstash
创建一个软连接，每次执行命令的时候不用在写安装路劲（默认安装在/usr/share下）
ln -s /usr/share/logstash/bin/logstash /bin/
执行logstash的命令
logstash -e 'input { stdin { } } output { stdout {} }'
运行成功以后输入:  nihao
# logstash -e 'input { stdin { } } output { stdout {codec => rubydebug} }'
# /usr/share/logstash/bin/logstash -e 'input { stdin { } } output { elasticsearch { hosts => ["192.168.1.202:9200"] } stdout { codec => rubydebug }}'
```

## logstash使用配置文件
```bash
创建配置文件01-logstash.conf
# vim /etc/logstash/conf.d/elk.conf
文件中添加以下内容
input { stdin { } }
output {
  elasticsearch { hosts => ["192.168.1.202:9200"] }
  stdout { codec => rubydebug }
}
使用配置文件运行logstash
# logstash -f ./elk.conf
运行成功以后输入以及标准输出结果
# vim /etc/logstash/conf.d/elk.conf
    
input {
    file {
        path => "/var/log/messages"
        type => "system"
        start_position => "beginning"
    }
    file {
        path => "/var/log/secure"
        type => "secure"
        start_position => "beginning"
    }
}

output {
    if [type] == "system" {
        elasticsearch {
            hosts => ["192.168.1.202:9200"]
            index => "nagios-system-%{+YYYY.MM.dd}"
        }
    }
    if [type] == "secure" {
        elasticsearch {
            hosts => ["192.168.1.202:9200"]
            index => "nagios-secure-%{+YYYY.MM.dd}"
        }
    }
}

#logstash -f /etc/logstash/conf.d/elk.conf
```

## Kibana的安装及使用
```bash
wget https://artifacts.elastic.co/downloads/kibana/kibana-5.4.0-linux-x86_64.tar.gz
tar -xzf kibana-5.4.0-linux-x86_64.tar.gz
mv kibana-5.4.0-linux-x86_64 /usr/local
ln -s /usr/local/kibana-5.4.0-linux-x86_64/ /usr/local/kibana 
vim /usr/local/kibana/config/kibana.yml
```

修改配置文件如下，开启以下的配置
```log
server.port: 5601
server.host: "0.0.0.0"
elasticsearch.url: "http://192.168.1.202:9200"
kibana.index: ".kibana" 
```
安装screen,以便于kibana在后台运行（当然也可以不用安装，用其他方式进行后台启动）
```bash
yum -y install screen
screen
/usr/local/kibana/bin/kibana
netstat -antp |grep 5601
# tcp        0      0 0.0.0.0:5601                0.0.0.0:*                   LISTEN      17007/node 
# 打开浏览器并设置对应的index
http://IP:5601
```



# 二、ELK实战篇
好，现在索引也可以创建了，现在可以来输出nginx、apache、message、secrue的日志到前台展示（Nginx有的话直接修改，没有自行安装）
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

修改access_log的输出格式为刚才定义的json 
access_log  logs/elk.access.log  json;

继续修改apache的配置文件

LogFormat "{ \
        \"@timestamp\": \"%{%Y-%m-%dT%H:%M:%S%z}t\", \
        \"@version\": \"1\", \
        \"tags\":[\"apache\"], \
        \"message\": \"%h %l %u %t \\\"%r\\\" %>s %b\", \
        \"clientip\": \"%a\", \
        \"duration\": %D, \
        \"status\": %>s, \
        \"request\": \"%U%q\", \
        \"urlpath\": \"%U\", \
        \"urlquery\": \"%q\", \
        \"bytes\": %B, \
        \"method\": \"%m\", \
        \"site\": \"%{Host}i\", \
        \"referer\": \"%{Referer}i\", \
        \"useragent\": \"%{User-agent}i\" \
       }" ls_apache_json
```
一样修改输出格式为上面定义的json格式  
CustomLog logs/access_log ls_apache_json  
编辑logstash配置文件，进行日志收集  
vim /etc/logstash/conf.d/full.conf
```bash
    input {
    file {
        path => "/var/log/messages"
        type => "system"
        start_position => "beginning"
    }   
    file {
        path => "/var/log/secure"
        type => "secure"
        start_position => "beginning"
    }   
    file {
        path => "/var/log/httpd/access_log"
        type => "http"
        start_position => "beginning"
    }   
    file {
        path => "/usr/local/nginx/logs/elk.access.log"
        type => "nginx"
        start_position => "beginning"
    }   
}
    
output {
    if [type] == "system" { 
        elasticsearch {
            hosts => ["192.168.1.202:9200"]
            index => "nagios-system-%{+YYYY.MM.dd}"
        }       
    }   
    if [type] == "secure" {
        elasticsearch {
            hosts => ["192.168.1.202:9200"]
            index => "nagios-secure-%{+YYYY.MM.dd}"
        }
    }
    if [type] == "http" {
        elasticsearch {
            hosts => ["192.168.1.202:9200"]
            index => "nagios-http-%{+YYYY.MM.dd}"
        }
    }
    if [type] == "nginx" {
        elasticsearch {
            hosts => ["192.168.1.202:9200"]
            index => "nagios-nginx-%{+YYYY.MM.dd}"
        }
    }
}
```
运行看看效果如何`logstash -f /etc/logstash/conf.d/full.conf`


# 三：ELK终极篇
```bash
# 安装reids 
yum install -y redis
# 修改redis的配置文件
vim /etc/redis.conf
修改内容如下
daemonize yes
bind 192.168.1.202
启动redis服务
# /etc/init.d/redis restart
测试redis的是否启用成功
# redis-cli -h 192.168.1.202
输入info如果有不报错即可
redis 192.168.1.202:6379> info
redis_version:2.4.10
....
```
编辑配置redis-out.conf配置文件  
把标准输入的数据存储到redis中  
`vim /etc/logstash/conf.d/redis-out.conf`
添加如下内容  
```bash
input {
        stdin {}
}
output {
        redis {
                host => "192.168.1.202"
                port => "6379"
                password => 'test'
                db => '1'
                data_type => "list"
                key => 'elk-test'
        }
}   
```
运行logstash指定redis-out.conf的配置文件  
`/usr/share/logstash/bin/logstash -f /etc/logstash/conf.d/redis-out.conf`
运行成功以后，在logstash中输入内容（查看下效果）  
编辑配置redis-in.conf配置文件，把reids的存储的数据输出到elasticsearch中  
`vim /etc/logstash/conf.d/redis-out.conf`

添加如下内容
```bash
input{
    redis {
                    host => "192.168.1.202"
                    port => "6379"
                    password => 'test'
                    db => '1'
                    data_type => "list"
                    key => 'elk-test'
                    batch_count => 1 #这个值是指从队列中读取数据时，一次性取出多少条，默认125条（如果redis中没有125条，就会报错，所以在测试期间加上这个值）
            }
}
output {
        elasticsearch {
                hosts => ['192.168.1.202:9200']
                index => 'redis-test-%{+YYYY.MM.dd}'
        }
}
```
运行logstash指定redis-in.conf的配置文件  
`/usr/share/logstash/bin/logstash -f /etc/logstash/conf.d/redis-out.conf`


把之前的配置文件修改一下，变成所有的日志监控的来源文件都存放到redis中，然后通过redis在输出到elasticsearch中,更改为如下，编辑full.conf
```
input {
    file {
            path => "/var/log/httpd/access_log"
            type => "http"
            start_position => "beginning"
    }

    file {
            path => "/usr/local/nginx/logs/elk.access.log"
            type => "nginx"
            start_position => "beginning"
    }
    file {
            path => "/var/log/secure"
            type => "secure"
            start_position => "beginning"
    }
    file {
            path => "/var/log/messages"
            type => "system"
            start_position => "beginning"
    }
}
output {
    if [type] == "http" {
        redis {
            host => "192.168.1.202"
            password => 'test'
            port => "6379"
            db => "6"
            data_type => "list"
            key => 'nagios_http' 
        }
    }

    if [type] == "nginx" {
        redis {
            host => "192.168.1.202"
            password => 'test'
            port => "6379"
            db => "6"
            data_type => "list"
            key => 'nagios_nginx' 
        }
    }

    if [type] == "secure" {
        redis {
            host => "192.168.1.202"
            password => 'test'
            port => "6379"
            db => "6"
            data_type => "list"
            key => 'nagios_secure' 
        }
    }

    if [type] == "system" {
        redis {
            host => "192.168.1.202"
            password => 'test'
            port => "6379"
            db => "6"
            data_type => "list"
            key => 'nagios_system' 
        }
    }
} 
```

运行logstash指定shipper.conf的配置文件  
`/usr/share/logstash/bin/logstash -f /etc/logstash/conf.d/full.conf`  
在redis中查看是否已经将数据写到里面(有时候输入的日志文件不产生日志，会导致redis里面也没有写入日志)  
把redis中的数据读取出来，写入到elasticsearch中(需要另外一台主机做实验)  
编辑配置文件  
`vim /etc/logstash/conf.d/redis-out.conf`
```bash
input {
    redis {
        type => "system"
        host => "192.168.1.202"
        password => 'test'
        port => "6379"
        db => "6"
        data_type => "list"
        key => 'nagios_system' 
    batch_count => 1
     }
    
    redis {
        type => "http"
        host => "192.168.1.202"
        password => 'test'
        port => "6379"
        db => "6"
        data_type => "list"
        key => 'nagios_http' 
    batch_count => 1
     }

    redis {
        type => "nginx"
        host => "192.168.1.202"
        password => 'test'
        port => "6379"
        db => "6"
        data_type => "list"
        key => 'nagios_nginx'
    batch_count => 1
     }
    
    redis {
        type => "secure"
        host => "192.168.1.202"
        password => 'test'
        port => "6379"
        db => "6"
        data_type => "list"
        key => 'nagios_secure' 
    batch_count => 1
    }
}
    
output {
    if [type] == "system" {
        elasticsearch {
            hosts => ["192.168.1.202:9200"]
            index => "nagios-system-%{+YYYY.MM.dd}"
        }
    }   

    if [type] == "http" {
        elasticsearch {
            hosts => ["192.168.1.202:9200"]
            index => "nagios-http-%{+YYYY.MM.dd}"
        }   
    }   

    if [type] == "nginx" {
        elasticsearch {
            hosts => ["192.168.1.202:9200"]
            index => "nagios-nginx-%{+YYYY.MM.dd}"
        }   
    }  

    if [type] == "secure" {
        elasticsearch {
            hosts => ["192.168.1.202:9200"]
            index => "nagios-secure-%{+YYYY.MM.dd}"
        }   
    }  
}
```

运行命令看看效果  
`/usr/share/logstash/bin/logstash -f /etc/logstash/conf.d/redis-out.conf`

因为ES保存日志是永久保存，所以需要定期删除一下日志，下面命令为删除指定时间前的日志  
`curl -X DELETE http://xx.xx.com:9200/logstash-*-`date +%Y-%m-%d -d "-$n days"`