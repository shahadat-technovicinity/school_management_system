from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from apps.admissions.services.bulk_import_service import import_students_from_csv

class BulkImportAPIView(APIView):
    """
    Accepts CSV / Excel uploads to bulk insert Admission Forms into the DB.
    """
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        file_obj = request.FILES.get('file')
        class_name = request.data.get('class_id', 'class 6')
        section = request.data.get('section_id', 'A')

        if not file_obj:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            total_imported = import_students_from_csv(file_obj, class_name, section)
            return Response(
                {'message': f'Success! {total_imported} students imported into {class_name}'}, 
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
