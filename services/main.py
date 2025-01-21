from rest_framework import status
from rest_framework.response import Response


class CustomResponseMixin:
    def custom_response(
        self,
        message: str | None = None,
        data: dict | None = None,
        status: int = status.HTTP_200_OK,
    ):
        return Response(
            data={"status": status, "message": message, "data": data},
            status=status,
        )
