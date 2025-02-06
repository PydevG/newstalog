from django.contrib import admin
from .models import *

@admin.register(PageVisit)
class PageVisitAdmin(admin.ModelAdmin):
    list_display = ('user', 'session_key', 'ip_address', 'url', 'start_time', 'end_time', 'time_spent')
    list_filter = ('start_time', 'url')
    search_fields = ('user__username', 'ip_address', 'url', 'session_key')
    ordering = ('-start_time',)

    def time_spent(self, obj):
        return obj.time_spent()

admin.site.register(Blog)
admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Comment)
admin.site.register(Profile)
admin.site.register(ContactMessage)
