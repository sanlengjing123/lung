from django.db import models

# Create your models here.
class Login_PW(models.Model):
    User_Name = models.CharField(max_length = 32)
    Password = models.CharField(max_length = 32)

class Is_login(models.Model):
    log_flag = models.IntegerField(default='0')