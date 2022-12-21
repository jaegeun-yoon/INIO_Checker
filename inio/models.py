from django.db import models
from django.urls import reverse

class Category(models.Model):
    category_text = models.CharField(max_length=200)

    class Meta:
        verbose_name = 'category_text'
        verbose_name_plural = 'categories'

    def __str__(self):
        return 'Category : ' + self.category_text

class Inio(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    domain = models.URLField(max_length=200, unique=True, db_index=True, blank=False)
    description = models.TextField(blank=True)
    status = models.BooleanField(blank=False, default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated']
    
    def __str__(self):
        return 'Domain : ' + self.domain

    def get_absolute_url(self):
        return reverse('detail', kwargs={'pk':self.id})

class UploadFileModel(models.Model):
    title = models.TextField(default='')
    file = models.FileField(null=True)