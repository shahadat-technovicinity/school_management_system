from django.db import models

# Create your models here.
class Book_model(models.Model):
    BOOK_CATEGORIES = [
        ('Fiction', 'Fiction'),
        ("Non_Fiction", "Non_Fiction"),
        ("Science", "Science"),
        ("History", "History"),
        ("Biography", "Biography"),
        ("Mystery", "Mystery"),
        ("Romance", "Romance"),
        ("Fantasy", "Fantasy")
    ]

    book_serial = models.CharField(max_length=100)
    book_name = models.CharField(max_length=255)
    author_name = models.CharField(max_length=255)
    category = models.CharField(max_length=100, choices=BOOK_CATEGORIES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    location = models.CharField(max_length=255)
    comments = models.TextField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return super().__str__()