from datetime import datetime

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from elasticsearch import Elasticsearch
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

es = Elasticsearch(
    hosts=[{'host': "192.168.56.16", 'port': 9200}]
)


@api_view(['GET'])
@csrf_exempt
def stock_count_by_person(request):
    sender_username = request.GET.get('senderUsername', '')
    res_data = agg_query('senderUsername', sender_username, 'stock')
    return JsonResponse(res_data)


@api_view(['GET'])
@csrf_exempt
def stock_count_in_channel(request):
    channel_username = request.GET.get('channelUsername', '')
    res_data = agg_query('channelUsername', channel_username, 'stock')
    return JsonResponse(res_data)


@api_view(['GET'])
@csrf_exempt
def channel_count_by_stock(request):
    stock = request.GET.get('stock', '')
    res_data = agg_query('stock', stock, 'channelUsername')
    return JsonResponse(res_data)


@api_view(['GET'])
@csrf_exempt
def person_count_by_stock(request):
    stock = request.GET.get('stock', '')
    res_data = agg_query('stock', stock, 'senderUsername')
    return JsonResponse(res_data)


def agg_query(key_query, value_query, aggregation_field):
    request_body = {
        "query": {
            "match": {
                key_query: value_query
            }
        },
        "size": 0,
        "aggs": {
            "my_count": {
                "terms": {
                    "field": aggregation_field,
                    "size": 5
                }
            }
        }
    }

    aa = es.search(index="djangopost2", body=request_body)
    if len(aa['aggregations']['my_count']['buckets']) == 0:
        data = {"results": []}
    else:
        my_list = []
        for item in aa['aggregations']['my_count']['buckets']:
            my_list.append((item['key'], item['doc_count']))
        sorted_list = sorted(my_list, key=lambda x: x[1], reverse=True)
        data = {"results": sorted_list}
    return data


@api_view(['GET'])
@csrf_exempt
def stock_count_by_date(request):
    from_date = request.GET.get('messageDateFrom', "")
    size_request = 5

    request_body = {
        "query": {
            "match_all": {}
        },
        "size": 0,
        "aggs": {
            "my_count": {
                "terms": {
                    "field": "stock",
                    "size": size_request
                },
                "aggs": {
                    "range": {
                        "date_range": {
                            "field": "messageDate",
                            "ranges": [
                                {
                                    "from": from_date,
                                }
                            ]
                        }
                    }
                }
            }

        }
    }
    aa = es.search(index="djangopost2", body=request_body)
    if len(aa['aggregations']['my_count']['buckets']) == 0:
        data = {"results": []}
    else:
        my_list = []
        for item in aa['aggregations']['my_count']['buckets']:
            my_list.append((item['key'], item['range']['buckets'][0]['doc_count']))
        sorted_list = sorted(my_list, key=lambda x: x[1], reverse=True)
        data = {"results": sorted_list}
    return JsonResponse(data);
