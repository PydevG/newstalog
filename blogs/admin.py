from django.contrib import admin
from .models import *
from django.utils.html import format_html
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
from .forms import ContactMessageReplyForm
from django.urls import path
from django.shortcuts import get_object_or_404, redirect

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
    
    
from django.urls import path
from django.utils.html import format_html
from django.shortcuts import get_object_or_404, redirect
from django.contrib import admin, messages
from .models import Blog

class PendingApprovalFilter(admin.SimpleListFilter):
    """Filter to display only posts that need approval."""
    title = 'Pending Approval'
    parameter_name = 'pending_approval'

    def lookups(self, request, model_admin):
        return [('pending', 'Pending Approval')]

    def queryset(self, request, queryset):
        if self.value() == 'pending':
            return queryset.filter(is_approved=False, is_published=False)
        return queryset

class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'is_approved', 'is_published', 'is_headline', 'is_trending', 'to_slide', 'review_status', 'admin_actions')
    list_filter = ('is_approved', 'is_published', 'is_headline', 'is_trending', 'to_slide', PendingApprovalFilter)
    search_fields = ('title', 'author__username')

    def review_status(self, obj):
        """Displays the review status in Django Admin."""
        if obj.is_approved:
            return format_html('<span style="color: green;">Approved</span>')
        elif obj.rejection_reason:
            return format_html('<span style="color: red;">Rejected</span>')
        return format_html('<span style="color: orange;">Pending</span>')

    def admin_actions(self, obj):
        """Provides action buttons in Django Admin."""
        return format_html(
            '<a class="button approve" href="approve/{}/">Approve</a> '
            '<a class="button reject" href="reject/{}/">Reject</a> '
            '<a class="button headline" href="toggle_headline/{}/">Headline</a> '
            '<a class="button trending" href="toggle_trending/{}/">Trending</a> '
            '<a class="button slide" href="toggle_slide/{}/">Slide</a>',
            obj.id, obj.id, obj.id, obj.id, obj.id
        )

    admin_actions.short_description = "Actions"

    class Media:
        """Add custom CSS to style buttons in Django Admin."""
        css = {"all": ("admin/css/custom_admin.css",)}

    def get_urls(self):
        """Adds custom admin URLs for approving, rejecting, and marking posts."""
        urls = super().get_urls()
        custom_urls = [
            path('approve/<int:post_id>/', self.admin_site.admin_view(self.approve_post), name='admin_approve_post'),
            path('reject/<int:post_id>/', self.admin_site.admin_view(self.reject_post), name='admin_reject_post'),
            path('toggle_headline/<int:post_id>/', self.admin_site.admin_view(self.toggle_headline), name='admin_toggle_headline'),
            path('toggle_trending/<int:post_id>/', self.admin_site.admin_view(self.toggle_trending), name='admin_toggle_trending'),
            path('toggle_slide/<int:post_id>/', self.admin_site.admin_view(self.toggle_slide), name='admin_toggle_slide'),
        ]
        return custom_urls + urls  

    def approve_post(self, request, post_id):
        """Handles approving a post from the Django Admin panel."""
        post = get_object_or_404(Blog, id=post_id)
        post.is_approved = True
        post.is_published = True
        post.rejection_reason = None
        post.save()
        messages.success(request, f'Post "{post.title}" has been approved!')
        return redirect(request.META.get("HTTP_REFERER", "/admin/blogs/blog/"))

    def reject_post(self, request, post_id):
        """Handles rejecting a post from the Django Admin panel."""
        post = get_object_or_404(Blog, id=post_id)
        post.is_approved = False
        post.is_published = False
        post.rejection_reason = "Your post did not meet the content guidelines."
        post.save()
        messages.error(request, f'Post "{post.title}" has been rejected.')
        return redirect(request.META.get("HTTP_REFERER", "/admin/blogs/blog/"))

    def toggle_headline(self, request, post_id):
        """Handles toggling a post as a headline."""
        post = get_object_or_404(Blog, id=post_id)
        post.is_headline = not post.is_headline
        post.save()
        status = "set as a headline" if post.is_headline else "removed from headlines"
        messages.success(request, f'Post "{post.title}" has been {status}.')
        return redirect(request.META.get("HTTP_REFERER", "/admin/blogs/blog/"))

    def toggle_trending(self, request, post_id):
        """Handles toggling a post as trending."""
        post = get_object_or_404(Blog, id=post_id)
        post.is_trending = not post.is_trending
        post.save()
        status = "set as trending" if post.is_trending else "removed from trending"
        messages.success(request, f'Post "{post.title}" has been {status}.')
        return redirect(request.META.get("HTTP_REFERER", "/admin/blogs/blog/"))

    def toggle_slide(self, request, post_id):
        """Handles toggling a post to slide."""
        post = get_object_or_404(Blog, id=post_id)
        post.to_slide = not post.to_slide
        post.save()
        status = "set to slide" if post.to_slide else "removed from slides"
        messages.success(request, f'Post "{post.title}" has been {status}.')
        return redirect(request.META.get("HTTP_REFERER", "/admin/blogs/blog/"))

admin.site.register(Blog, BlogAdmin)
admin.site.register(ContactMessage, ContactAdmin)
admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Comment)
admin.site.register(Profile)
admin.site.register(CustomUser)
