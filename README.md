# 说明

简单说明下本次日志采集方案，将节点的日志内容通过 filebeat 或其他工具送到redis消息队列，然后使用 logstash 单机／集群读取消息队列的内容，根据配置文件进行过滤。然后将过滤后的文件输送到elasticsearch中，通过kibana去展示。

# ELK结构框架
Logstash 基本组成

![](https://developer.ibm.com/developer/articles/os-cn-elk/nl/zh/images/img004.png)

这里选择ELK+Redis的方式进行部署，下面简单记录下ELK结合Redis搭建日志分析平台的集群环境部署过程，大致的架构如下：

![](https://s2.ax1x.com/2020/01/09/lWqMvt.png)

* Elasticsearch是一个分布式搜索分析引擎，稳定、可水平扩展、易于管理是它的主要设计初衷;
* Logstash是一个灵活的数据收集、加工和传输的管道软件;
* Kibana是一个数据可视化平台，可以通过将数据转化为酷炫而强大的图像而实现与数据的交互
* 将三者的收集加工，存储分析和可视转化整合在一起就形成了ELK;

详细架构图如下：

![](https://s2.ax1x.com/2020/01/09/lWqbPH.png)

# 基本流程

（1）Logstash-Shipper获取日志信息发送到redis。

（2）Redis在此处的作用是防止ElasticSearch服务异常导致丢失日志，提供消息队列的作用。redis会立马传输到elasticsearch。

（3）logstash是读取Redis中的日志信息发送给ElasticSearch。

（4）ElasticSearch提供日志存储和检索。

（5）Kibana是ElasticSearch可视化界面插件。

## logstash
```bash
cat docker-compose.yml
version: '3.3'
services:
  logstash:
    container_name: logstash
    restart: always
    image: dockerhub.datagrand.com/global/logstash-oss:6.0.0
    volumes:
      - /data/product/logstash/logstash.conf:/usr/share/logstash/pipeline/logstash.conf
      - /data/product/logstash/log4j2.properties:/usr/share/logstash/config/log4j2.properties
      - /data/product/logstash/log/logstash-logfile:/usr/share/logstast/logfile
      - /data/product/logstash/log/logstash-logs:/usr/share/logstash/logs
      - /data/product/logstash/logstash.yml:/usr/share/logstash/config/logstash.yml
    environment:
      - LS_JAVA_OPTS=-Xms2g -Xmx2g
    ports:
      - "5044:5044"
    command: bin/logstash -f pipeline/logstash.conf --config.reload.automatic
```

## kibana
```bash
cat docker-compose-product.yml
version: '3'
services:
  kibana-product:
    container_name: kibana-product
    image: dockerhub.datagrand.com/global/kibana:5.5.2
    restart: always
    environment:
      #- ELASTICSEARCH_URL="http://rpa-es.datagrand.net:9234"
      - ELASTICSEARCH_URL="http://rec-elasticsearch.datagrand.com:8989"
      - XPACK_SECURITY_ENABLED="false"
      - XPACK_MONITORING_ENABLED="true"
      - KIBANA_INDEX=".kibana-product"
    ports:
      - "5602:5601"
```

## 说明
```
$ source .env
$ docker-compose up -d
```
Kibana的web入口：
`http://localhost:5601`

该elk栈的默认端口：
* 5000: Logstash TCP input.
* 9200: Elasticsearch HTTP
* 9300: Elasticsearch TCP transport
* 5601: Kibana
Create an index pattern via the Kibana API:
```bash
$ curl -XPOST -D- 'http://localhost:5601/api/saved_objects/index-pattern' \
    -H 'Content-Type: application/json' \
    -H 'kbn-version: 7.8.0' \
    -u elastic:<your generated elastic password> \
    -d '{"attributes":{"title":"logstash-*","timeFieldName":"@timestamp"}}'
```
```bash
$ docker stack deploy -c docker-stack.yml elk
```
```
  - sed -i -e 's/\(elasticsearch.username:\) elastic/\1 kibana_system/g' -e 's/\(elasticsearch.password:\) changeme/\1 testpasswd/g' kibana/config/kibana.yml
  - sed -i -e 's/\(xpack.monitoring.elasticsearch.username:\) elastic/\1 logstash_system/g' -e 's/\(xpack.monitoring.elasticsearch.password:\) changeme/\1 testpasswd/g' logstash/config/logstash.yml
  - sed -i 's/\(password =>\) "changeme"/\1 "testpasswd"/g' logstash/pipeline/logstash.conf
  - sed -i -e 's/\(elasticsearch.password:\) changeme/\1 testpasswd/g' -e 's/\(secret_management.encryption_keys:\)/\1 [test-encrypt]/g' extensions/enterprise-search/config/enterprise-search.yml
  - sed -i 's/\(password:\) changeme/\1 testpasswd/g' extensions/apm-server/config/apm-server.yml
```

* [elk-stack](https://www.elastic.co/elk-stack)
* [config-es](./elasticsearch/config/elasticsearch.yml)
* [config-kbn](./kibana/config/kibana.yml)
* [config-ls](./logstash/config/logstash.yml)
* [ELK搭建篇](https://www.cnblogs.com/cheyunhua/p/11238489.html)
* [集中式日志系统 ELK 协议栈详解](https://developer.ibm.com/zh/articles/os-cn-elk/)

