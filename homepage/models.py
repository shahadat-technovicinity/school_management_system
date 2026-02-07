from django.db import models

class Home_Page_Slider(models.Model):
    title = models.CharField(max_length=200, blank=True, null=True)
    image = models.ImageField(upload_to='sliders/')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title if self.title else f"Slider {self.id}"
    


# Message Model
class Message(models.Model):
    MESSAGE_TYPES = (
        ('president', 'সভাপতি মহোদয়ের বাণী'),
        ('principal', 'প্রধান শিক্ষক মহোদয়ের বাণী'),
    )
    
    title = models.CharField(max_length=200, blank=True, null=True)
    type = models.CharField(max_length=20, choices=MESSAGE_TYPES, unique=True)
    content = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    



class AdmissionNotice(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField() 
    
    # গুরুত্বপূর্ণ তারিখসমূহ
    application_start = models.DateField()
    application_end = models.DateField()
    exam_date = models.DateField()
    result_date = models.DateField()
    
    is_active = models.BooleanField(default=True) 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.year})"
    


### contact info model
class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=15)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"
    


### Letter Info Model
class LetterInfo(models.Model):
    later_type_choices = [
        ('edu ministry', 'Edu Ministry'),
        ('committee', 'Committee'),
        ('staff data', 'Staff Data'),]
    
    later_type = models.CharField(max_length=20, choices=later_type_choices)
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='letters/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    

