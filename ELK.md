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
