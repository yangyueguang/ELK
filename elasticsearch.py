import json
from datetime import datetime
from elasticsearch import Elasticsearch
from elasticsearch_dsl.query import MultiMatch, Match
from elasticsearch_dsl.connections import connections
from elasticsearch_dsl import Q, A, Search, Keyword, Mapping, Text, Index, Document, InnerDoc
from elasticsearch_dsl import Date, Nested, Boolean, analyzer, Completion, MultiSearch

# https://www.jianshu.com/p/462007422e65


def dlog(res):
    print(json.dumps(res, ensure_ascii=False, indent=4))


es = Elasticsearch(
    hosts=['127.0.0.1:9200'],
    http_auth=('elastic', 'changeme'),
    # 在做任何操作之前，先进行嗅探
    sniff_on_start=True,
    # 节点没有响应时，进行刷新，重新连接
    sniff_on_connection_fail=True,
    # 每 60 秒刷新一次
    sniffer_timeout=60
)
es.ping()
es.info()
es.cluster.health()
es.cluster.client.info()
es.cluster.stats()
es.cluster.state()
es.cat.indices()
es.cat.health()
es.cat.master()
es.cat.nodes()
es.cat.count()
es.cat.plugins()
es.cat.templates()
es.tasks.get()
es.tasks.list()

es.indices.create(index='news', ignore=[400, 429])
data = {'title': '美国', 'url': 'http://www.baidu.com'}
es.create(index='news', doc_type='politics', id=1, body=data, ignore=[409])
# result = es.index(index='news', doc_type='politics', body=data)

data = {
    'title': '美国留给伊拉克的是个烂摊子吗',
    'url': 'http://view.news.qq.com/zt2011/usa_iraq/index.htm',
    'date': '2011-12-16'
}
result = es.delete(index='news', doc_type='politics', id=1)
result = es.indices.delete(index='news', ignore=[400, 404, 429])

mapping = {
    'properties': {
        'title': {
            'type': 'text',
            'analyzer': 'ik_max_word',
            'search_analyzer': 'ik_max_word'
        }
    }
}
result = es.indices.put_mapping(index='news', doc_type='politics', body=mapping)
result = es.update(index='news', doc_type='politics', body=data, id=1)
datas = [
    {
        'title': '美国留给伊拉克的是个烂摊子吗',
        'url': 'http://view.news.qq.com/zt2011/usa_iraq/index.htm',
        'date': '2011-12-16'
    },
    {
        'title': '公安部：各地校车将享最高路权',
        'url': 'http://www.chinanews.com/gn/2011/12-16/3536077.shtml',
        'date': '2011-12-16'
    },
    {
        'title': '中韩渔警冲突调查：韩警平均每天扣1艘中国渔船',
        'url': 'https://news.qq.com/a/20111216/001044.htm',
        'date': '2011-12-17'
    },
    {
        'title': '中国驻洛杉矶领事馆遭亚裔男子枪击 嫌犯已自首',
        'url': 'http://news.ifeng.com/world/detail_2011_12/16/11372558_0.shtml',
        'date': '2011-12-18'
    }
]

for data in datas:
    es.index(index='news', doc_type='politics', body=data)


result = es.search(index='news', doc_type='politics')
dsl = {
    'query': {
        'match': {
            'title': '中国 领事馆'
        }
    }
}

result = es.search(index='news', doc_type='politics', body=dsl)
print(json.dumps(result, indent=2, ensure_ascii=False))

res = es.search(
    index="news",  # 索引名
    body={  # 请求体
        "query": {  # 关键字，把查询语句给 query
            "bool": {  # 关键字，表示使用 filter 精确查询
                "must": [  # 表示里面的条件必须匹配，多个匹配元素可以放在列表里
                    {
                        "match": {
                            "date": '2011-12-16'
                        }
                    },
                ],
                "must_not": {
                    "match": {
                        "title": "公安"  # 返回的结果里不能包含公安
                    }
                }
            }
        },
        "sort": [{"date": {"order": "desc"}}],
        "from": 0,
        "size": 10
    }
)

# filter是精确匹配 query是模糊匹配 exclude是排除匹配
s = Search(using=es, index="news")\
    .filter("match", date='2011-12-16')\
    .query("match", title='美国')\
    .exclude("match", title="公安")

response = s.execute()
total = s.count()
total = response.hits.total.value

# 要定义全局使用的默认连接，请使用 connections模块和create_connection方法：
client = connections.create_connection(alias='qa', hosts=['127.0.0.1:9200'], http_auth=('elastic', 'changeme'), timeout=20)
s = Search(index="news")\
    .filter("match", date='2011-12-16')\
    .query("match", title='美国')\
    .exclude("match", title="公安")
sa = Search().query().query('match', title='美国')
for hit in sa:
    print("%s|%s" % (hit.title, hit.url))
sa.to_dict()

# 或者后来修改连接的数据库
client = Elasticsearch()
s = Search(using=client)
# s = Search(using='qa') # 用别名连接
s = Search().using(client).query("match", title="美国")
s.execute()
for hit in s:
    print("%s|%s" % (hit.title, hit.url))



q = Q("multi_match", query='美国', fields=['title', 'url'])
Q({"multi_match": {"query": "美国", "fields": ["title", "url"]}})
# 这两种方式最后转换的结果是一致的
MultiMatch(fields=['title', 'body'], query='python django')
s = s.query(q)
# Q 接收的参数，，query 方法都支持
s = s.query("multi_match", query='美国', fields=['title', 'url'])

# Q 对象可以使用逻辑运算符进行组合
Q("match", title='美国') & Q("match", url='view')  # 与
Q("match", title='美国') | Q("match", title='中国')  # 或
~Q("match", title="美国")                           # 非
# query 方法可以被连续调用
sa = Search().query().query('match', title='python').query('match', body='django')
sa.to_dict()
# {
#     "query": {
#         "bool": {
#             "must": [
#                 {"match": {"title": "python"}},
#                 {"match": {"body": "django"}}
#             ]
#         }
#     }
# }

# 假如你希望对查询的条件进行精确的控制，请使用 Q 构造组合查询
q = Q('bool',
    must=[Q('match', title='美国')],
    should=[Q(...), Q(...)],
    minimum_should_match=1
)
s = Search().query(q)

s = Search()
s = s.filter('terms', tags=['search', 'python'])
# 等价于
s = s.query('bool', filter=[Q('terms', tags=['search', 'python'])])
# {'query': {'bool': {'filter': [{'terms': {'tags': ['search', 'python']}}]}}}

# 定义一个聚合，请使用 A
a = A('terms', field='category')
# {"terms": {"field": "category"}}
# 嵌套聚合,可以使用.bucket()，.metric()和 .pipeline()方法：
a.metric('clicks_per_category', 'sum', field='clicks').bucket('tags_per_category', 'terms', field='tags')
# {
#   'terms': {'field': 'category'},
#   'aggs': {
#     'clicks_per_category': {'sum': {'field': 'clicks'}},
#     'tags_per_category': {'terms': {'field': 'tags'}}
#   }
# }
# 要将聚合添加到Search对象，请使用.aggs充当顶级聚合的属性
s = Search()
a = A('terms', field='category')
s.aggs.bucket('category_terms', a)
# {
#   'aggs': {
#     'category_terms': {
#       'terms': {
#         'field': 'category'
#       }
#     }
#   }
# }

s = Search()
s.aggs.bucket('articles_per_day', 'date_histogram', field='publish_date', interval='day')\
    .metric('clicks_per_day', 'sum', field='clicks')\
    .pipeline('moving_click_average', 'moving_avg', buckets_path='clicks_per_day')\
    .bucket('tags_per_day', 'terms', field='tags')

s.to_dict()
# {
#   "aggs": {
#     "articles_per_day": {
#       "date_histogram": { "interval": "day", "field": "publish_date" },
#       "aggs": {
#         "clicks_per_day": { "sum": { "field": "clicks" } },
#         "moving_click_average": { "moving_avg": { "buckets_path": "clicks_per_day" } },
#         "tags_per_day": { "terms": { "field": "tags" } }
#       }
#     }
#   }
# }

# 排序
s = Search().sort(
    'category',
    '-title',
    {"lines": {"order": "asc", "mode": "avg"}}
)

# 分页
# 要指定from / size参数，请使用Python切片AP
s = s[10:20]
# {"from": 10, "size": 10}
# 如果要访问与查询匹配的所有文档，可以使用 scan使用扫描/滚动弹性搜索API的方法
for hit in s.scan():
    print(hit.title)

# 突出高亮
# 要设置突出显示的常用属性，请使用以下highlight_options方法：
s = s.highlight_options(order='score')
# 为各个字段启用突出显示使用以下highlight方法完成：
s = s.highlight('title')
# or, including parameters:
s = s.highlight('title', fragment_size=50)
# 返回的结果将在被赋值到一个对象(变量)上可用，.meta.highlight.FIELD 将包含结果的列表：

response = s.execute()
for hit in response:
    for fragment in hit.meta.highlight.title:
        print(fragment)

# # 如果您需要限制elasticsearch返回的字段，请使用以下 source()方法：
# s = s.source(['title', 'body'])
# # 不返回任何字段，只是元数据
# s = s.source(False)
# # 明确包含/排除字段
# s = s.source(include=["title"], exclude=["user.*"])
# # 重置字段选择
# s = s.source(None)

s = Search.from_dict({"query": {"match": {"title": "美国"}}})
# 如果要修改现有的Search对象，并重写它的属性，可以使用这个实例的 update_from_dict() 方法，改变是实时生效的：
s = Search()
s.to_dict()
# {'query': {'match_all': {}}}
s.update_from_dict({"query": {"match": {"title": "美国"}}, "size": 42})
s.to_dict()
# {'query': {'match': {'title': '美国'}}, 'size': 42}

response = s.execute()
print(response.success())
print(response.took)  # 命中数
print(response.hits.total)
print(response.suggest.my_suggestions)

# MultiSearch 如果您需要同时执行多个搜索，则可以使用 MultiSearch 类，这将使用该类的 _msearch API ：

ms = MultiSearch(index='blogs')
ms = ms.add(Search().filter('term', tags='python'))
ms = ms.add(Search().filter('term', tags='elasticsearch'))
responses = ms.execute()
for response in responses:
    print("Results for query %r." % response.search.query)
    for hit in response:
        print(hit.title)

# 持久化
# name your type
m = Mapping('my-type')
# add fields
m.field('title', 'text')
# you can use multi-fields easily
m.field('category', 'text', fields={'raw': Keyword()})
# you can also create a field manually
comment = Nested()
comment.field('author', Text())
comment.field('created_at', Date())
# and attach it to the mapping
m.field('comments', comment)
# you can also define mappings for the meta fields
m.meta('_all', enabled=False)
# save the mapping into index 'my-index'
m.save('my-index')

# 如果你想在你的文档中创建一个类似于模型的包装，请使用Document：
html_strip = analyzer('html_strip',
    tokenizer="standard",
    filter=["standard", "lowercase", "stop", "snowball"],
    char_filter=["html_strip"]
)

class Comment(InnerDoc):
    def age(self):
        return datetime.now() - self.created_at


class Post(Document):
    title = Text()
    title_suggest = Completion()
    created_at = Date()
    published = Boolean()
    category = Text(
        analyzer=html_strip,
        fields={'raw': Keyword()}
    )

    comments = Nested(
        doc_class=Comment,
        properties={
            'author': Text(fields={'raw': Keyword()}),
            'content': Text(analyzer='snowball'),
            'created_at': Date()
        }
    )

    class Meta:
        index = 'blog'

    def add_comment(self, author, content):
        self.comments.append(
          {'author': author, 'content': content})

    def save(self, ** kwargs):
        self.created_at = datetime.now()
        return super().save(** kwargs)

# instantiate the document
first = Post(title='My First Blog Post, yay!', published=True)
# assign some field values, can be values or lists of values
first.category = ['everything', 'nothing']
# every document has an id in meta
first.meta.id = 47
# save the document into the cluster
first.save()

post = Post(meta={'id': 42})
# prints 42, same as post._id
print(post.meta.id)
# override default index, same as post._index
post.meta.index = 'my-blog'

# retrieve the document
first = Post.get(id=42)
# now we can call methods, change fields, ...
first.add_comment('me', 'This is nice!')
# and save the changes into the cluster again
first.save()
# you can also(也) update just individual fields which will call the update API
# and also(并且) update the document in place（首先）
first.update(published=True, published_by='me')

# To delete a document just call its delete method:
first = Post.get(id=42)
first.delete()
# by calling .search we get back a standard Search object
# 通过调用 .search()， 我们得到一个标准的搜索对象
s = Post.search()
# the search is already limited to the index and doc_type of our document
s = s.filter('term', published=True).query('match', title='first')


results = s.execute()
# when you execute the search the results are wrapped in your document class (Post)
for post in results:
    print(post.meta.score, post.title)
s = Post.search()
s = s.suggest('title_suggestions', 'pyth', completion={'field': 'title_suggest'})
# you can even execute just the suggestions via the _suggest API
suggestions = s.execute_suggest()
for result in suggestions.title_suggestions:
    print('Suggestions for %s:' % result.text)
    for option in result.options:
        print('  %s (%r)' % (option.text, option.payload))


blogs = Index('blogs')
# define custom settings
blogs.settings(
    number_of_shards=1,
    number_of_replicas=0
)
# define aliases
blogs.aliases(
    old_blogs={}
)
# register a doc_type with the index
blogs.document(Post)
# can also be used as class decorator when defining the DocType
@blogs.document
class Post(Document):
    title = Text()
# You can attach custom analyzers to the index
html_strip = analyzer('html_strip',
    tokenizer="standard",
    filter=["standard", "lowercase", "stop", "snowball"],
    char_filter=["html_strip"]
)
blogs.analyzer(html_strip)
# delete the index, ignore if it doesn't exist
blogs.delete(ignore=404)
# create the index in elasticsearch
blogs.create()

print('hello')
