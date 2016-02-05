from rest_framework.response import Response
from rest_framework.views import exception_handler


def rdap_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        response = Response(
            None,
            status=response.status_code,
            headers={'Access-Control-Allow-Origin': '*'},
            content_type='application/rdap+json'
        )

    return response
