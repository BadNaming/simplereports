from rest_framework.exceptions import APIException


class DataNotReceivedException(APIException):
    status_code = 500
    default_detail = 'Данные не получены'
    default_code = 'data_not_received'


class InvalidDataException(APIException):
    status_code = 400
    default_detail = 'Некорректные данные'
    default_code = 'invalid_data'


class ResponseNotRecievedException(APIException):
    status_code = 400
    default_detail = 'Ответ не получен'
    default_code = 'response_not_recieve'
