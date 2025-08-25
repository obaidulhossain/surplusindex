from django.db import models

class MediaFile(models.Model):
    file = models.FileField(upload_to='uploads/%Y/%m/%d/')
    title = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.title or self.file.name

    def get_url(self):
        return self.file.url