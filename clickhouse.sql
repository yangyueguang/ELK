create table conn (
day Date DEFAULT toDate(ts),
ts DateTime,
uid String,
orig_p UInt16,
proto Enum8('icmp'=1, 'tcp'=6, 'udp'=17),
service Array(String),
duration Float32,
resp_bytes UInt64,
conn_state Enum8('OTH'=0, 'REJ'=1, 'RSTO'=2, 'RSTOS0'=3, 'RSTR'=4),
resp_cc FixedString(2),
extracted Nullable(String),
orig_filenames Array(Nullable(String)),
extracted_cutoff Nullable(Enum8('F'=0, 'T'=1)),
extracted_size Nullable(UInt32)
)
ENGINE = MergeTree(day,sipHash64(uid), (day,sipHash64(uid), uid), 8192);
CREATE TABLE stock (
  `code` String,
  `date` Date,
  `open` Decimal32(2),
  `close` Decimal32(2),
  `low` Decimal32(2),
  `high` Decimal32(2),
  `volume` UInt64 ,
  `change` Float32
) ENGINE = MySQL('localhost:3306', 'stock', 'stocks', 'root', '12345678');
CREATE DATABASE mysql ENGINE = MySQL('localhost:3306', 'stock', 'root', '12345678')
select * from mysql.emp_backup
SELECT * FROM mysql('localhost:3306', 'mark', 'activety', 'root', '12345678')
   SELECT database,table,MAX(bytes_on_disk) AS bytes FROM system.parts
   GROUP BY database,table ORDER BY bytes DESC
   LIMIT 3 BY database
   LIMIT 10
OFFSET 5
   SELECT name,v1 FROM union_v1
   UNION ALL
   SELECT title,v1 FROM union_v2
create table ods.user_dim_local on cluster cluster
(
 day Date comment '数据分区-天',
 uid UInt32 default 0 comment 'uid',
 platform String default '' comment '平台 android/ios',
 country String default '' comment '国家',
 province String default '' comment '省及直辖市',
 isp String default '' comment '运营商',
 app_version String default '' comment '应用版本',
 os_version String default '' comment '系统版本',
 mac String default '' comment 'mac',
 ip String default '' comment 'ip',
 second DateTime default '1970-01-01 08:00:00' comment '数据时间-秒',
 insert_second DateTime default now() comment '数据写入时间',
 gender String default '' comment '性别',
 age Int16 default -1 comment '年龄',
    shown_uv AggregateFunction(uniqCombined,UInt32) comment '曝光人数'
)
engine = ReplicatedMergeTree('/clickhouse/tables/{layer}-{shard}/ods.user_dim_local','{replica}')
PARTITION BY day
PRIMARY KEY (day, hour)
ORDER BY (day, gender)
TTL day + toIntervalDay(3) + toIntervalHour(3)
SETTINGS index_granularity = 8192


--drop table dim.user_dim_dis on cluster cluster;
create table dim.user_dim_dis on cluster cluster
as ods.user_dim_local
engine=Distributed(cluster,ods,user_dim_local,rand());
SELECT
    platform,
    ver,
    uniqCombined(xx)
FROM
(
    SELECT
        platform,
        ver,
        uniqCombinedState(uid) AS xx
    FROM
    (
        SELECT
            a.1 AS platform,
            a.2 AS ver,
            a.3 AS uid
        FROM system.one
        ARRAY JOIN [('android', '1.1', 1001), ('android', '1.1', 1002), ('android', '1.1', 1003), ('android', '1.1', 1004)] AS a
    )
    GROUP BY
        platform,
        ver
    UNION ALL
    SELECT
        platform,
        ver,
        uniqCombinedState(uid) AS xx
    FROM
    (
        SELECT
            a.1 AS platform,
            a.2 AS ver,
            a.3 AS uid
        FROM system.one
        ARRAY JOIN [('android', '1.2', 1009), ('android', '1.2', 1010), ('android', '1.2', 1130), ('android', '1.2', 1131)] AS a
    )
    GROUP BY
        platform,
        ver
    UNION ALL
    SELECT
        platform,
        ver,
        uniqCombinedState(uid) AS xx
    FROM
    (
        SELECT
            a.1 AS platform,
            a.2 AS ver,
            a.3 AS uid
        FROM system.one
        ARRAY JOIN [('android', '1.1', 2001), ('android', '1.1', 3002), ('android', '1.1', 1003), ('android', '1.1', 3004)] AS a
    )
    GROUP BY
        platform,
        ver
    UNION ALL
    SELECT
        platform,
        ver,
        uniqCombinedState(uid) AS xx
    FROM
    (
        SELECT
            a.1 AS platform,
            a.2 AS ver,
            a.3 AS uid
        FROM system.one
        ARRAY JOIN [('android', '1.2', 2009), ('android', '1.2', 1010), ('android', '1.2', 2130), ('android', '1.2', 2131)] AS a
    )
    GROUP BY
        platform,
        ver
)
GROUP BY
    platform,
    ver
SELECT
    platform,
    ver,
    uniqCombinedMerge(xx) AS uv
FROM
(
    SELECT
        platform,
        ver,
        uniqCombinedState(uid) AS xx
    FROM
    (
        SELECT
            a.1 AS platform,
            a.2 AS ver,
            a.3 AS uid
        FROM system.one
        ARRAY JOIN [('android', '1.1', 1001), ('android', '1.1', 1002), ('android', '1.1', 1003), ('android', '1.1', 1004)] AS a
    )
    GROUP BY
        platform,
        ver
    UNION ALL
    SELECT
        platform,
        ver,
        uniqCombinedState(uid) AS xx
    FROM
    (
        SELECT
                   a.1 AS platform,
            a.2 AS ver,
            a.3 AS uid
        FROM system.one
        ARRAY JOIN [('android', '1.2', 1009), ('android', '1.2', 1010), ('android', '1.2', 1130), ('android', '1.2', 1131)] AS a
    )
    GROUP BY
        platform,
        ver
    UNION ALL
    SELECT
        platform,
        ver,
        uniqCombinedState(uid) AS xx
    FROM
    (
        SELECT
            a.1 AS platform,
            a.2 AS ver,
            a.3 AS uid
        FROM system.one
        ARRAY JOIN [('android', '1.1', 2001), ('android', '1.1', 3002), ('android', '1.1', 1003), ('android', '1.1', 3004)] AS a
    )
    GROUP BY
        platform,
        ver
    UNION ALL
    SELECT
        platform,
        ver,
        uniqCombinedState(uid) AS xx
    FROM
    (
        SELECT
            a.1 AS platform,
            a.2 AS ver,
            a.3 AS uid
        FROM system.one
        ARRAY JOIN [('android', '1.2', 2009), ('android', '1.2', 1010), ('android', '1.2', 2130), ('android', '1.2', 2131)] AS a
    )
 GROUP BY
        platform,
        ver
)
GROUP BY
    platform,
    ver
alter table dwm.mainpage_stat_mv_local on cluster mycluster
    add column if not exists gender String comment '性别'
    after item_id,
    modify order by
(day,hour,platform,ver,item_id,gender);
alter table dwm.mainpage_stat_mv_local on cluster mycluster
    modify column if exists gender String default '未知' comment '性别' after item_id;
alter table dws.mainpage_stat_mv_dis on cluster cluster
    add column if not exists gender String comment '性别' after item_id;
--新增指标
alter table dwm.mainpage_stat_mv_local on cluster cluster
    add column if not exists show_time_median AggregateFunction(medianExact,UInt32) comment '曝光时长中位数';
alter table dws.mainpage_stat_mv_dis on cluster cluster
    add column if not exists show_time_median AggregateFunction(medianExact,UInt32) comment '曝光时长中位数';
# 写入数据(这里需要注意指定字段写)
INSERT INTO test.mv_union_max (id, m1) SELECT
    id,
    uniqCombinedState(uid) AS m1
FROM
(
    SELECT
        a1.1 AS id,
        toUInt32(a1.2) AS uid
    FROM system.one
    ARRAY JOIN [(1, 10001), (2, 10002), (3, 10003), (3, 10001)] AS a1
)
GROUP BY id
CREATE DICTIONARY dim.dict_user_dim on cluster cluster (
 uid UInt64 ,
 platform String default '' ,
 country String default '' ,
 province String default '' ,
 isp String default '' ,
 app_version String default '' ,
 os_version String default '',
 mac String default '' ,
 ip String default '',
 gender String default '',
 age Int16 default -1
)
PRIMARY KEY uid
SOURCE(
  CLICKHOUSE(
    HOST 'localhost' PORT 9000 USER 'default' PASSWORD '' DB 'dim' TABLE 'user_dim_dis'
  )
 ) LIFETIME(MIN 1800 MAX 3600) LAYOUT(HASHED())