# Elastic stack (ELK) on Docker
```
$ source .env
$ docker-compose up -d
```
## 说明
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

