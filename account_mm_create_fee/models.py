from django.db import models
from datetime import date

# --- ১. Expense Voucher মডেল (খরচ/ভাউচার এন্ট্রির জন্য) ---

# class FormFilupAmount(models.Model):

#     # টাকার পরিমাণ সংরক্ষণের জন্য CharField-এর বদলে DecimalField ব্যবহার করুন
#     # CharField দিলে আপনি সংখ্যার ভিত্তিতে সর্টিং বা যোগ-বিয়োগ করতে পারবেন না
#     DECIMAL_OPTIONS = {'max_digits': 10, 'decimal_places': 2, 'default': 0.00, 'blank': True, 'null': True}

#     Printing_Xerox_Expense = models.DecimalField(**DECIMAL_OPTIONS, verbose_name=("Printing/Xerox Expense"))
#     Magazine_Fee_Expense = models.DecimalField(**DECIMAL_OPTIONS, verbose_name=("Magazine Fee/Expense"))
#     Sports_Fee = models.DecimalField(**DECIMAL_OPTIONS, verbose_name=("Sports Fee"))
#     Cultural_Debate_Fee = models.DecimalField(**DECIMAL_OPTIONS, verbose_name=("Cultural/Debate Fee"))
#     Victory_Day_Celebration = models.DecimalField(**DECIMAL_OPTIONS, verbose_name=("Victory Day Celebration"))
#     Formation_of_various_clubs = models.DecimalField(**DECIMAL_OPTIONS, verbose_name=("Formation of various clubs"))
#     Library = models.DecimalField(**DECIMAL_OPTIONS, verbose_name=("Library"))
#     Welfare_Poor_Fund = models.DecimalField(**DECIMAL_OPTIONS, verbose_name=("Welfare/Poor Fund"))
#     ICT = models.DecimalField(**DECIMAL_OPTIONS, verbose_name=("ICT"))
#     Garden_Maintenance = models.DecimalField(**DECIMAL_OPTIONS, verbose_name=("Garden Maintenance"))
#     Labratory = models.DecimalField(**DECIMAL_OPTIONS, verbose_name=("Labratory"))
#     scout_Red_Crescent_Celebration = models.DecimalField(**DECIMAL_OPTIONS, verbose_name=("scout/Red-Crescent Celebration"))
#     Common_Room = models.DecimalField(**DECIMAL_OPTIONS, verbose_name=("Common Room"))
#     Identity_Card = models.DecimalField(**DECIMAL_OPTIONS, verbose_name=("Identity Card"))
#     Essential_Expense = models.DecimalField(**DECIMAL_OPTIONS, verbose_name=("Essential Expense"))
#     Freshers_Farewell_Reception = models.DecimalField(**DECIMAL_OPTIONS, verbose_name=("Freshers/Farewell Reception"))
#     Medical_Service = models.DecimalField(**DECIMAL_OPTIONS, verbose_name=("Medical Service"))
#     Miscellaneous_Ancillary = models.DecimalField(**DECIMAL_OPTIONS, verbose_name=("Miscellaneous/Ancillary"))
#     Development = models.DecimalField(**DECIMAL_OPTIONS, verbose_name=("Development"))
#     Electricity = models.DecimalField(**DECIMAL_OPTIONS, verbose_name=("Electricity"))
#     Educational_Tour = models.DecimalField(**DECIMAL_OPTIONS, verbose_name=("Educational Tour"))
#     Swimming_Training = models.DecimalField(**DECIMAL_OPTIONS, verbose_name=("Swimming Training"))
#     Retirement = models.DecimalField(**DECIMAL_OPTIONS, verbose_name=("Retirement"))
#     Welfare = models.DecimalField(**DECIMAL_OPTIONS, verbose_name=("Welfare (Duplicate field, maybe delete later)"))
#     Mosque = models.DecimalField(**DECIMAL_OPTIONS, verbose_name=("Mosque"))
    
#     def __str__(self):
#         return f"Form Filup Amount ID: {self.pk}"
# # --- ২. Fee Assignment এবং Nested Models (ফী-এর জন্য) ---

class CreateFee(models.Model):
    # Assignment Type
    ASSIGNMENT_TYPE_CHOICES = [
        ('class_wise', 'Class-wise Fee'),
        ('individual', 'Individual Student Fee'),
    ]

    SELECT_CLASS_CHOICES = [
        ('class 6', 'Class 6'),
        ('class 7', 'Class 7'),
        ('class 8', 'Class 8'),
        ('class 9', 'Class 9'),
        ('class 10', 'Class 10'),
    ]

    SELECT_SECTION_CHOICES = [
        ('section A', 'Section A'),
        ('section B', 'Section B'),
        ('section C', 'Section C'),
        ('section D', 'Section D'),
    ]
    
    # Fee Type (আপনার তালিকা থেকে)
    FEE_TYPE_CHOICES = [
        ('tuition fee', 'Tuition Fee'),
        ('exam fee', 'Examination Fee'),
        ('form_fillup fee', 'Form Fillup Fee'), # নেস্টেড ডেটার জন্য
        ('registration fee', 'Registration Fee'),
        ('session fee', 'Session Fee'),
    ]
    
    assignment_type = models.CharField(max_length=20, choices=ASSIGNMENT_TYPE_CHOICES)
    select_class = models.CharField(max_length=50, choices=SELECT_CLASS_CHOICES) 
    select_section = models.CharField(max_length=50, choices=SELECT_SECTION_CHOICES)    
    fee_type = models.CharField(max_length=50, choices=FEE_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Total amount assigned.")
    due_date = models.DateField()
    payment_period = models.CharField(max_length=50)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Fee ID: {self.pk} - {self.fee_type} for {self.select_class}"


# # --- ৩. Form Fillup-এর জন্য সাব-অ্যামাউন্ট মডেল ---
# # Form Fillup Fee সিলেক্ট হলে তার বিস্তারিত টাকা সংরক্ষণ করবে।

# class FormFillupSubAmount(models.Model):
#     # 'FeeAssignment'-এর বদলে 'CreateFee' ব্যবহার করুন
#     fee_assignment = models.ForeignKey(
#         'CreateFee', 
#         related_name='sub_amounts',
#         on_delete=models.CASCADE
#     )
#     name = models.CharField(max_length=100, blank=True, null=True) # যেমন: "Application Fee", "Board Fee"
#     amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

#     def __str__(self):
#         return f"{self.name}: {self.amount}"