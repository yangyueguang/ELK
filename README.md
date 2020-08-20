# Elastic stack (ELK) on Docker
$ source .env
$ docker-compose up -d

说明
Kibana的web入口：
http://localhost:5601
该elk栈的默认端口为：
5000: Logstash TCP input.
9200: Elasticsearch HTTP
9300: Elasticsearch TCP transport
5601: Kibana
Create an index pattern via the Kibana API:
```console
$ curl -XPOST -D- 'http://localhost:5601/api/saved_objects/index-pattern' \
    -H 'Content-Type: application/json' \
    -H 'kbn-version: 7.8.0' \
    -u elastic:<your generated elastic password> \
    -d '{"attributes":{"title":"logstash-*","timeFieldName":"@timestamp"}}'
```
```bash
$ docker stack deploy -c docker-stack.yml elk
```
  # Use built-in users with passwords set by 'elasticsearch-setup-passwords.exp'
  - sed -i -e 's/\(elasticsearch.username:\) elastic/\1 kibana_system/g' -e 's/\(elasticsearch.password:\) changeme/\1 testpasswd/g' kibana/config/kibana.yml
  - sed -i -e 's/\(xpack.monitoring.elasticsearch.username:\) elastic/\1 logstash_system/g' -e 's/\(xpack.monitoring.elasticsearch.password:\) changeme/\1 testpasswd/g' logstash/config/logstash.yml
  - sed -i 's/\(password =>\) "changeme"/\1 "testpasswd"/g' logstash/pipeline/logstash.conf
  - sed -i -e 's/\(elasticsearch.password:\) changeme/\1 testpasswd/g' -e 's/\(secret_management.encryption_keys:\)/\1 [test-encrypt]/g' extensions/enterprise-search/config/enterprise-search.yml
  - sed -i 's/\(password:\) changeme/\1 testpasswd/g' extensions/apm-server/config/apm-server.yml


[elk-stack](https://www.elastic.co/elk-stack)
[stack-features](https://www.elastic.co/products/stack)
[paid-features](https://www.elastic.co/subscriptions)
[trial-license](https://www.elastic.co/guide/en/elasticsearch/reference/current/license-settings.html)

[linux-postinstall](https://docs.docker.com/install/linux/linux-postinstall/)

[booststap-checks](https://www.elastic.co/guide/en/elasticsearch/reference/current/bootstrap-checks.html)
[es-sys-config](https://www.elastic.co/guide/en/elasticsearch/reference/current/system-config.html)

[win-shareddrives](https://docs.docker.com/docker-for-windows/#shared-drives)
[mac-mounts](https://docs.docker.com/docker-for-mac/osxfs/)

[builtin-users](https://www.elastic.co/guide/en/elasticsearch/reference/current/built-in-users.html)
[ls-security](https://www.elastic.co/guide/en/logstash/current/ls-security.html)
[sec-tutorial](https://www.elastic.co/guide/en/elasticsearch/reference/current/security-getting-started.html)

[connect-kibana](https://www.elastic.co/guide/en/kibana/current/connect-to-elasticsearch.html)
[index-pattern](https://www.elastic.co/guide/en/kibana/current/index-patterns.html)

[config-es](./elasticsearch/config/elasticsearch.yml)
[config-kbn](./kibana/config/kibana.yml)
[config-ls](./logstash/config/logstash.yml)

[es-docker](https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html)
[kbn-docker](https://www.elastic.co/guide/en/kibana/current/docker.html)
[ls-docker](https://www.elastic.co/guide/en/logstash/current/docker-config.html)

[log4j-props](https://github.com/elastic/logstash/tree/7.6/docker/data/logstash/config)
[esuser](https://github.com/elastic/elasticsearch/blob/7.6/distribution/docker/src/docker/Dockerfile#L23-L24)

[upgrade](https://www.elastic.co/guide/en/elasticsearch/reference/current/setup-upgrade.html)

[swarm-mode](https://docs.docker.com/engine/swarm/)
