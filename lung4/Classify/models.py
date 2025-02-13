from django.db import models

# Create your models here.
class ViT_Model(models.Model):
    Name = models.CharField(max_length = 64)
    ###
    Description = models.CharField(max_length = 1024)
    Route = models.CharField(max_length = 128)
    Classes = models.IntegerField(default = 0)


