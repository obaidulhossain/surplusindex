from django.contrib import admin
from django.utils.html import format_html
from .models import MediaFile

@admin.register(MediaFile)
class MediaFileAdmin(admin.ModelAdmin):
    list_display = ('thumb', 'title', 'file', 'uploaded_at')
    search_fields = ('title', 'file')

    def thumb(self, obj):
        # simple thumbnail preview for images
        if obj.file and obj.file.url.lower().endswith(('jpg','jpeg','png','gif','webp')):
            return format_html('<img src="{}" style="height:40px; object-fit:cover;"/>', obj.file.url)
        return '—'
    thumb.short_description = 'Preview'
