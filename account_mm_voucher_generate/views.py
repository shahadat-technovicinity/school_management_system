import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from django.http import FileResponse
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response
from rest_framework import status

from .models import ExpenseVoucher
from .serializers import ExpenseVoucherSerializer

# --- ReportLab PDF function ---
def generate_pdf_from_data(voucher_data, voucher_pk):
    """
    Voucher data থেকে ReportLab ব্যবহার করে সরাসরি PDF তৈরি করে।
    voucher_pk হলো মডেলের আইডি।
    """
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # === 1. headline ===
    p.setFont("Helvetica-Bold", 18)
    p.drawCentredString(width / 2, height - 50, "EXPENSE VOUCHER") 
    p.line(50, height - 60, width - 50, height - 60)
    
    # === 2. data  ===
    LABEL_X = inch
    VALUE_X = 3 * inch
    line_height = height - 100
    
    # A. voucher id (PK)
    p.setFont("Helvetica-Bold", 12)
    p.drawString(LABEL_X, line_height, "Voucher ID (PK):")
    p.setFont("Helvetica", 12)
    p.drawString(VALUE_X, line_height, str(voucher_pk)) # <-- PK ব্যবহার করা হলো
    line_height -= 25 
    
    # B. date
    p.setFont("Helvetica-Bold", 12)
    p.drawString(LABEL_X, line_height, "Date:")
    p.setFont("Helvetica", 12)
    p.drawString(VALUE_X, line_height, str(voucher_data.get('date', 'N/A')))
    line_height -= 25
    
    # C, D, E...data no change।

    p.setFont("Helvetica-Bold", 12)
    p.drawString(LABEL_X, line_height, "Category:")
    p.setFont("Helvetica", 12)
    p.drawString(VALUE_X, line_height, voucher_data.get('deposit_category', 'N/A'))
    line_height -= 25

    p.setFont("Helvetica-Bold", 12)
    p.drawString(LABEL_X, line_height, "Amount:")
    p.setFont("Helvetica", 12)
    p.drawString(VALUE_X, line_height, f"Tk={voucher_data.get('amount', 0.00)}")
    line_height -= 40
    
    p.setFont("Helvetica-Bold", 12)
    p.drawString(LABEL_X, line_height, "Description:")
    line_height -= 20
    
    description = voucher_data.get('description', 'No description provided.')
    BOX_X, BOX_Y, BOX_WIDTH, BOX_HEIGHT = inch, line_height - 100, width - 2*inch, 90
    p.rect(BOX_X, BOX_Y, BOX_WIDTH, BOX_HEIGHT) 
    p.setFont("Helvetica", 10)
    display_desc = description[:200] + ('...' if len(description) > 200 else '')
    p.drawString(BOX_X + 5, BOX_Y + BOX_HEIGHT - 15, display_desc)

    # === ৩. স্বাক্ষর স্থান ===
    SIGN_Y = 100
    p.setFont("Helvetica", 10)
    p.line(width - 4 * inch, SIGN_Y, width - 1.5 * inch, SIGN_Y)
    p.drawCentredString(width - 2.75 * inch, SIGN_Y - 15, "Authorised Signature")


    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer

# --- DRF Generic View  ---
class GenerateVoucherAPIView(ListCreateAPIView):
    queryset = ExpenseVoucher.objects.all()
    serializer_class = ExpenseVoucherSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        voucher_instance = serializer.save()
        
        voucher_data = serializer.data
        voucher_pk = voucher_instance.pk 
        
        try:
            
            pdf_buffer = generate_pdf_from_data(voucher_data, voucher_pk) 
            return FileResponse(
                pdf_buffer, 
                as_attachment=True, 
                filename=f'voucher_id_{voucher_pk}.pdf',
                content_type='application/pdf',
                status=status.HTTP_201_CREATED
            )
        
        except Exception as e:
            return Response({
                "error": "Failed to generate PDF",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)