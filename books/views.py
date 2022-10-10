import datetime
import json

from django.http import HttpResponse
from rest_framework import status, generics
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from adapters.elastic.elastic_adapter import ElasticAdaptor
from adapters.kafka.kafka_adapter import KafkaAdapter
from books.models import Book
from books.pagination import ResultsSetPagination
from books.serializers import BookSerializer, AddBookSerializer

# Create your views here.

kafka_adaptor = KafkaAdapter()
elastic_adaptor = ElasticAdaptor()


# @permission_classes([IsAuthenticated])
class BookListApi(generics.ListAPIView):
    serializer_class = BookSerializer
    pagination_class = ResultsSetPagination
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        queryset = Book.objects.filter(number_of_stock__gte=1)
        author = self.request.query_params.get('author')
        genre = self.request.query_params.get('genre')
        if author is not None:
            queryset = queryset.filter(author__name__contains=author)
        if genre is not None:
            queryset = queryset.filter(genre=genre)
        _make_log_dic(self.request, "BookListApi")
        return queryset


class LoanBookListApi(generics.ListAPIView):
    serializer_class = BookSerializer
    pagination_class = ResultsSetPagination
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        queryset = Book.objects.filter(loan__book__isnull=False)
        _make_log_dic(self.request, "LoanBookList")
        return queryset


class AddBookApi(generics.CreateAPIView):
    serializer_class = AddBookSerializer


# @api_view(['POST'])
# def book_list_api(request, format=None):
#     if request.method == 'POST':
#         author = request.data['author']
#         book_list = Book.objects.exclude(loan__book__isnull=False).filter(author__name__contains=author)
#         serializer = BookSerializer(book_list, many=True)
#         return Response(serializer.data)
@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def book_detail_api(request, book_id, format=None):
    try:
        book = Book.objects.get(pk=book_id)
    except Book.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        serializer = BookSerializer(book)
        _make_log_dic(request, 'GetDetailBook', book_id)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = BookSerializer(book, data=request.data)
        if serializer.is_valid():
            serializer.save()
            _make_log_dic(request, 'EditedBook', book_id)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        _make_log_dic(request, 'DeletedBook', book_id)
        book.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
def loan_book_api(request):
    if request.method == 'POST':
        try:
            book_id = request.data['id']
            book = Book.objects.get(pk=book_id)
            if request.user.is_authenticated:
                if book.loan.filter(username=request.user).exists():
                    _make_log_dic(request, "loaned", book_id)
                    return HttpResponse("keatb {book_name} be karbar {username} qablan dade shode ast"
                                        .format(book_name=book.name,
                                                username=request.user.username))
                else:
                    if book.number_of_stock >= 1:
                        book.loan.add(request.user)
                        book.number_of_stock -= 1
                        book.save()
                        _make_log_dic(request, 'loan', book_id)
                        return HttpResponse("keatb {book_name} be karbar {username} dade shod"
                                            .format(book_name=book.name,
                                                    username=request.user.username))
                    else:
                        _make_log_dic(request, 'OutOfStock', book_id)
                        return HttpResponse('Out of stock')
            else:
                return HttpResponse('You are not logged in. Please log in and try again')
        except Book.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def return_loan_book_api(request):
    if request.method == 'POST':
        try:
            book_id = request.data['id']
            book = Book.objects.get(pk=book_id)
            if request.user.is_authenticated:
                if book.loan.filter(username=request.user).exists():
                    book.loan.remove(request.user)
                    book.number_of_stock += 1
                    book.save()
                    _make_log_dic(request, 'ReturnLoanedBook', book_id)
                    return HttpResponse("karbar {username} ketab {book_name} ra pas dad"
                                        .format(book_name=book.name,
                                                username=request.user.username))
            else:
                return HttpResponse('You are not logged in. Please log in and try again')
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def track_logs_api(request):
    if request.method == "POST":
        if request.user.is_superuser:
            book_id = request.data.get("book_id")
            user_name = request.data.get("user_name")
            page_size = request.data.get("page_size", 10)
            page = request.data.get("page", 1)
            start_datetime = request.data.get("start_datetime")
            end_datetime = request.data.get("end_datetime")
            action_type = request.data.get("action_type")
            query_body = _make_elastic_query(book_id, user_name, page_size, page, start_datetime, end_datetime,
                                             action_type)
            print(query_body)
            elastic_result = elastic_adaptor.client.search(body=query_body, index='log')
            elastic_result = elastic_result.get('hits').get('hits')
            result_list = list()
            for i in elastic_result:
                result_list.append(i.get('_source'))
            json_result = json.dumps(result_list)
            return Response(json.dumps(result_list))


def _make_log_dic(request, action_type, book_id=None):
    log_dict = dict()
    string_datetime = str(datetime.datetime.now())
    string_datetime = string_datetime.replace(" ", "T")
    log_dict['action_datetime'] = string_datetime
    log_dict['user_name'] = request.user.username
    if book_id is not None:
        log_dict['book_id'] = book_id
    log_dict['action_type'] = action_type
    kafka_adaptor.produce_to_kafka(topic='log', value=log_dict)


def _make_elastic_query(book_id, user_name, page_size, page, start_datetime, end_datetime, action_type):
    query_dict = dict()
    query_dict['size'] = page_size
    query_dict['from'] = page - 1
    query_dict['sort'] = list()
    sort_dict = dict()
    sort_dict['action_datetime'] = dict()
    sort_dict['action_datetime']['order'] = "desc"
    query_dict['sort'].append(sort_dict)
    query_dict['query'] = dict()
    query_dict['query']['bool'] = dict()
    query_dict['query']['bool']['must'] = list()
    if user_name:
        user_name_query = dict()
        user_name_query['term'] = dict()
        user_name_query['term']['user_name'] = dict()
        user_name_query['term']['user_name']['value'] = user_name
        query_dict['query']['bool']['must'].append(user_name_query)
    if book_id:
        book_id_query = dict()
        book_id_query['term'] = dict()
        book_id_query['term']['book_id'] = dict()
        book_id_query['term']['book_id']['value'] = book_id
        query_dict['query']['bool']['must'].append(book_id_query)

    if action_type:
        action_type_query = dict()
        action_type_query['term'] = dict()
        action_type_query['term']['action_type'] = dict()
        action_type_query['term']['action_type']['value'] = action_type
        query_dict['query']['bool']['must'].append(action_type_query)

    if start_datetime or end_datetime:
        datetime_query = dict()
        datetime_query['range'] = dict()
        datetime_query['range']['action_datetime'] = dict()
        datetime_query['range']['action_datetime']['gte'] = start_datetime
        datetime_query['range']['action_datetime']['lte'] = end_datetime
        query_dict['query']['bool']['must'].append(datetime_query)

    return query_dict
