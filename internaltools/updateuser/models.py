from django.db import models

class UsersId(models.Model):
    LoginName = models.CharField(
        primary_key=True,
        max_length=20
    )
    FirstName = models.CharField(max_length=30)
    LastName = models.CharField(max_length=30)
    class Meta:
       managed = False
       db_table = 'UsersId'
