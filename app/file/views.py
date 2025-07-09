from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from app.core.file_service import file_service
from app.core.utils.logger import logger


class FileUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            file_url = file_service.upload(file_obj)
        except Exception as e:
            logger.error(f"Error uploading file: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'url': file_url}, status=status.HTTP_201_CREATED)


class FileDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        url = request.data.get('url')
        if not url:
            return Response({'error': 'No URL provided'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            file_service.delete(url)
        except Exception as e:
            logger.error(f"Error deleting file: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)
