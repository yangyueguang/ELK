# Elasticsearch
## Elasticsearch的基本概念
* 索引（index）
* 类型（type）
* 映射（mapping）
* 文档（document）
* 倒排索引原理
* 文档打分机制
* 集群（cluster）——单节点、集群安装与部署
* 健康状态（red/yellow/green）
* 数据存储
* 数据类型（long/date/text、keyword/nested等）
* 数据展示（结合Head插件的基础可视化）

## Elasitcsearch的基本操作
* 新增（insert）
* 删除（delete/deletebyquery）
* 修改（update/updatebyquery）
* 查找（search）
* 精确匹配检索（term、terms、range、exists）
* 模糊匹配检索（wildcard、prefix、negix正则）
* 分词全文检索（match/match_phrase等）
* 多条件 bool 检索（must/must_not/should多重组合）
* 分词（英文分词、拼音分词、中文分词）
* 高亮
* 分页查询
* 指定关键词返回
* 批量操作 bulk
* scroll 查询
* reindex 操作

## Elasticsearch高级操作
* 聚合统计（数量聚合、最大值、最小值、平均值、求和等聚合操作）
* 图像化展示（hisgram 按照日期等聚合）
* 聚合后分页
* 父子文档
* 数组类型
* nested 嵌套类型
* ES 插件错误排查（集群问题、检索问题、性能问题）
* ES 性能调优（配置调优、集群调优等）

## Elasticsearch API
* Elasticsearch 原生自带 API、JEST、Springboot 等 API 选型
* Elasticsearch 多条件 bool 复杂检索 API
* Elasticsearch 分页 API
* Elasticsearch 高亮 API
* Elasticsearch 聚合 API
* Elasticsearch 相关 JSON 数据解析

## Elasticsearch结合场景开发实战
* 数据可视化（Kibana、Grafana 等 其中 Grafana 比较适合监控类场景）
* 通过 logstash/beats 等导入数据
* Elasticsearch 和 Kafka 结合的应用场景
* Elasticsearch 和 Mongo 结合的应用场景
* Elasticsearch 和 Hadoop 结合的应用场景
* 结合业务需求的定制化应用场景（日志分析、文档检索、全文检索、金融等各行业检索）

# Kibana
* Kibana 安装与部署
* ES 节点数据同步到 Kibana
* Kibana Dev Tools 开发工具熟练使用
* Kibana 图像化组合展示
* 将 Kibana 图像化展示效果图应用到自己的开发环境中

# Logstash
* Logstash 的安装与部署
* Logstash 将本地文件导入 ES
* logstashinputjdbc 插件（5.X后无需安装）将 MySQL/Oracle 等关系型数据库数据导入 ES，全量导入和增量导入实现。
* logstashinputmongo插件将 Mongo 数据导入 ES
* logstashinputkafaka 插件将 Kafak 数据导入 ES
* logstashoutput* 插件将 ES 数据导入不同的数据库和实时数据流中

# Beats
* 不同类型的 Beats 安装与部署
* 将业务数据通过 Beats 导入 ES

# 掌握最高效工具
1. Kibana 工具  
除了支持各种数据的可视化之外，最重要的是支持 Dev Tool 进行 RESTFUL API 增删改查操作。比 Postman 工具和 cURL 都要方便。

2. head 插件  
可实现 ES 集群状态查看、索引数据查看、ES DSL 实现（增、删、改、查操作），比较实用的地方是 JSON 串的格式化。

3. Cerebro 工具  
用于实现 ES 集群状态查看（堆内存使用率、CPU使用率、内存使用率、磁盘使用率）。

4. ElasticHD工具  
其强势功能包括支持 SQL 转 DSL，不要完全依赖，可以借鉴用。

5. 中文分词工具  
建议选用 IK 分词。 

6. 类 SQL 查询工具  
在此，推荐 elasticsearch-SQL，其支持的 SQL，极大缩小了复杂 DSL 的实现成本。  
通过 elasticsearch-SQL 工具可以基于以下 SQL 语句方式请求 ES 集群。  
select COUNT(*),SUM(age),MIN(age) as m, AVG(age) FROM bank GROUP BY gender ORDER BY SUM(age)

7. 测试工具  
在原来执行的 DSL 的基础上新增 profile 参数，我把它称作“测试工具”。  
profile API的目的是，将 ES 高层的 ES 请求拉平展开，直观的让你看到请求做了什么，每个细分点花了多少时间。  
profile API给你改善性能提供相关支撑工作。  
使用举例如下：  
```bash
GET /_search
{  "profile": true,  "query" : {    "match" : { "message" : "message number" }
  }
}
```

8. ES性能分析工具  
推荐 rally。相比传统的发包请求测试工具，rally 更加直观和准确、且指标很丰富。

