View mapping
```
GET{index_name}/_mapping
```

Search and match field

```
GET{index_name}/_search
{
  "query": {
    "match" : {
      "field": "value"
    }
  }
}
```
Search with less than or greater than
- epoch
```
GET {index_name}/_search
{
  "query": {
     "range":{
        "timeStampName":{ "lte" : "1653409585000"}
    }
  }
}
```
- zoneDateTime
```
        "createAt":{ "gt" : "2022-06-02T10:56:27.000Z"}
```

Search for a single doc
```
GET {index_name}/_doc/{doc_id}
```

Clone an index
```
POST {existingIndex}/_clone/{newIndexName}
```

Update by query
- copy old field to new field
```
POST {indexName}/_update_by_query
{
  "query": {
        "constant_score" : {
            "filter" : {
                "exists" : { "field" : "old.field" }
            }
        }

  },
  "script" : {
      "source": "ctx._source.new.field = ctx._source.old.field;"
  }
}
```
- remove field
```
POST {indexName}/_update_by_query
{
  "query": {
        "constant_score" : {
            "filter" : {
                "exists" : { "field" : "raw" }
            }
        }
  },
  "script" : "ctx._source.remove('raw')"
}
```
Delete by query
- all
```
POST {indexName}/_delete_by_query
{
  "query": {     
        "match_all" : {}
  }
}

```
- match field
```
POST {indexName}/_delete_by_query
{
  "query": {     
    "match": {
      "type": "dss"
    }
  }
}
```

Fix "org.elasticsearch.indices.IndexClosedException: closed". 
```
POST {index_name}/_open
```
