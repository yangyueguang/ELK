# ELK结构框架
![](https://s2.ax1x.com/2020/01/09/lWqbPH.png)
* Elasticsearch是一个分布式搜索分析引擎，稳定、可水平扩展、易于管理是它的主要设计初衷;
* Logstash是一个灵活的数据收集、加工和传输的管道软件;
* Kibana是一个数据可视化平台，可以通过将数据转化为酷炫而强大的图像而实现与数据的交互
* 将三者的收集加工，存储分析和可视转化整合在一起就形成了ELK;  

# 基本流程
1. filebeat 或 Logstash-Shipper获取日志信息发送到redis。
2. Redis在此处的作用是防止ElasticSearch服务异常导致丢失日志，提供消息队列的作用。redis会立马传输到ES。
3. logstash是读取Redis中的日志信息发送给ElasticSearch。
4. ElasticSearch提供日志存储和检索。
5. Kibana是ElasticSearch可视化界面插件。
6. 部署到服务器上之后通过Nginx端口转发与反向代理把服务暴露出去。

## 默认端口说明：
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

* [elk-stack](https://www.elastic.co/elk-stack)
* [ELK搭建篇](https://www.cnblogs.com/cheyunhua/p/11238489.html)
* [集中式日志系统 ELK 协议栈详解](https://developer.ibm.com/zh/articles/os-cn-elk/)

