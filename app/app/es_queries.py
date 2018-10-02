from elasticsearch import Elasticsearch
import os

class ESQ():
    es = Elasticsearch([{'host': os.environ['ELASTICSEARCH_SERVER'], 'port': 9200}])

    def __init__(self, **kwargs):
        pass

    @staticmethod
    def search_quakes_by_keyword_place(index,keyword):
        print ('testing query by keyword')
        dict_query={"sort":[{"properties.time":"desc"}],"from":0, "size":1000 ,"query":{"match":{'properties.place':keyword}}}

        result_query = ESQ.es.search(index=index,body=dict_query)
        return result_query

    def get_counts_per_day(index, keyword, days_count):
        dict_query = {"size": 0, "aggs": {"group_by_day": {"terms": {"size":days_count,"field": "properties.days","order":{"_key":"desc"}}}},
                      "query": {"match": {'properties.place': keyword}}}
        result_query = ESQ.es.search(index=index, body=dict_query)
        return result_query

    def get_quakes_per_period_per_place(index, keyword, date_init, date_end, lower_mag, upper_mag):
        dict_query = {"sort":[{"properties.time":"desc"}],"from":0, "size":1000 ,
                      "query":{
                          "bool":{
                              "must":[
                                  {"match": {'properties.place': keyword}},
                                  {"range": {"properties.time": {"gte": date_init, "lte": date_end}}},
                                  {"range": {"properties.mag": {"gte": lower_mag, "lte": upper_mag}}}
                              ]}},
                      }

        result_query = ESQ.es.search(index=index, body=dict_query)
        return result_query


    def get_quakes_per_period_per_magnitude(index, keyword, timestamp_init, timestamp_end, lower_mag, upper_mag,  min_lat, max_lat, min_lng, max_lng):
        print('es_queries.py')
        print('get_quakes_per_period_per_magnitude')
        print('keyword',keyword)
        print('timestamp_init', timestamp_init)
        print('timestamp_end', timestamp_end)
        print('value time stamp from db', 1538116015399)
        print('lower_mag', lower_mag)
        print('upper_mag', upper_mag)

        if keyword is None:
            if min_lng>max_lng:
                dict_query = {"sort": [{"properties.mag": "desc"}], "from": 0, "size": 1000,
                              "query": {
                                  "bool": {
                                      "must": [
                                          {"range": {"properties.time": {"gte": timestamp_init, "lte": timestamp_end}}},
                                          {"range": {"properties.mag": {"gte": lower_mag, "lte": upper_mag}}},
                                          {"range": {"properties.lat": {"gte": min_lat, "lte": max_lat}}},
                                          {"bool": {"should":[
                                              {"range": {"properties.lng": {"gte": -180, "lte": max_lng}}},
                                              {"range": {"properties.lng": {"gte": min_lng, "lte": 180}}}
                                          ]}
                                          }
                                      ]}},
                              }

            else:
                dict_query = {"sort": [{"properties.mag": "desc"}], "from": 0, "size": 1000,
                              "query": {
                                  "bool": {
                                      "must": [
                                          {"range": {"properties.time": {"gte": timestamp_init, "lte": timestamp_end}}},
                                          {"range": {"properties.mag": {"gte": lower_mag, "lte": upper_mag}}},
                                          {"range": {"properties.lat": {"gte": min_lat, "lte": max_lat}}},
                                          {"range": {"properties.lng": {"gte": min_lng, "lte": max_lng}}},
                                      ]}},
                              }

        else:
            dict_query = {"sort": [{"properties.mag": "desc"}], "from": 0, "size": 1000,
                          "query": {
                              "bool": {
                                  "must": [
                                      {"match": {'properties.place': keyword}},
                                      {"range": {"properties.time": {"gte": timestamp_init, "lte": timestamp_end}}},
                                      {"range": {"properties.mag": {"gte": lower_mag, "lte": upper_mag}}},
                                  ]}}
                          }




        print(dict_query)

        result_query = ESQ.es.search(index=index, body=dict_query)
        print(result_query)

        return result_query





    def get_summary_per_period_per_place(index, keyword, date_init, date_end):
        dict_query = {"size": 0,
                      "query":{
                          "bool":{
                              "must":[
                                  {"match": {'properties.place': keyword}},
                                  {"range": {"properties.time": {"gte": date_init, "lte": date_end}}}
                              ]}},
                      "aggs": {
                          "group_by_day":
                              {"terms": {
                                  "size":1000,
                                  "field": "properties.days",
                                  "order":{"_key":"desc"}
                              }}
                      }}


        #86400000

        result_query = ESQ.es.search(index=index, body=dict_query)

        number_miliseconds_per_day = 86400000

        ls_buckets_updated=[]
        old_key=None
        for b in result_query['aggregations']['group_by_day']['buckets']:
            if old_key is not None:
                diff_days=old_key-b['key']
                if diff_days>1:
                    i=0
                    while i<(diff_days-1):
                        i=i+1
                        new_key=old_key-i

                        new_b = {}
                        new_b['key'] = new_key
                        new_b['doc_count'] = 0
                        new_b['timestamp'] = new_b['key'] * number_miliseconds_per_day
                        ls_buckets_updated.append(new_b)

            b['timestamp']=b['key']*number_miliseconds_per_day
            ls_buckets_updated.append(b)
            old_key=b['key']

        result_query['aggregations']['group_by_day']['buckets']=ls_buckets_updated

        return result_query

    def get_ls_quakes(index, keyword,key_days):
        dict_query = {"size": 1000,
                      "query":{
                          "bool":{
                              "must":[
                                  {"match": {'properties.place': keyword}},
                                  {"match": {'properties.days': key_days}},
                              ]}}
                      }


        #86400000
        #1535328000000
        #1527804000
        print(dict_query)
        result_query = ESQ.es.search(index=index, body=dict_query)


        return result_query

