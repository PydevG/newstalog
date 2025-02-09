from django.contrib import admin
from .models import *
from django.utils.html import format_html
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
from .forms import ContactMessageReplyForm

@admin.register(PageVisit)
class PageVisitAdmin(admin.ModelAdmin):
    list_display = ('user', 'session_key', 'ip_address', 'url', 'start_time', 'end_time', 'time_spent')
    list_filter = ('start_time', 'url')
    search_fields = ('user__username', 'ip_address', 'url', 'session_key')
    ordering = ('-start_time',)

    def time_spent(self, obj):
        return obj.time_spent()
    
class ContactAdmin(admin.ModelAdmin):
    form = ContactMessageReplyForm
    list_display = ('name', 'email', 'sent_at', 'replied_status')
    readonly_fields = ('name', 'email', 'message')

    def save_model(self, request, obj, form, change):
        # If there's a reply, send it as an email
        if form.cleaned_data.get('reply'):
            try:
                send_mail(
                    subject=f"Re: Reply from Stalog",
                    message=form.cleaned_data['reply'],
                    from_email=settings.EMAIL_HOST_USER,  # Replace with your email
                    recipient_list=[obj.email],
                    fail_silently=False,
                )
                messages.success(request, f"Reply sent to {obj.email}")
                obj.reply = form.cleaned_data['reply']  # Save the reply in the database
                obj.replied = True  # Mark as replied
            except Exception as e:
                messages.error(request, f"Failed to send reply: {e}")
        super().save_model(request, obj, form, change)

    # Custom method to display the reply status with icons
    def replied_status(self, obj):
        if obj.replied:
            return format_html('<span style="color: green;" title="Replied">✔️</span>')
        else:
            return format_html('<span style="color: red;" title="Not Replied">❌</span>')

    replied_status.short_description = "Replied"


admin.site.register(ContactMessage, ContactAdmin)
admin.site.register(Blog)
admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Comment)
admin.site.register(Profile)
admin.site.register(CustomUser)
