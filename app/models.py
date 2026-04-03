from django.db import models
from django.contrib.auth.models import User

class Expense(models.Model):
    CATEGORIES = [('餐飲','餐飲'), ('交通','交通'), ('娛樂','娛樂'), ('生活','生活'), ('其他','其他')]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    expense_date = models.DateField()
    item = models.TextField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    category = models.CharField(max_length=10, choices=CATEGORIES)

    class Meta:
        ordering = ['-expense_date']