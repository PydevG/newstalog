from django.contrib import admin, messages
from .models import *
from django.utils.html import format_html
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
from .forms import ContactMessageReplyForm
from django.urls import path
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.middleware.csrf import get_token
from django.http import HttpRequest

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
    
    


class PendingApprovalFilter(admin.SimpleListFilter):
    """Custom filter to show only posts that need admin review."""
    title = "Approval Status"
    parameter_name = "pending_approval"

    def lookups(self, request, model_admin):
        return [
            ("pending", "Pending Approval"),
        ]

    def queryset(self, request, queryset):
        if self.value() == "pending":
            return queryset.filter(is_approved=False, rejection_reason__isnull=True)
        return queryset


class UpdatedPostsFilter(admin.SimpleListFilter):
    """Custom filter to show only updated posts."""
    title = "Updated Posts"
    parameter_name = "updated"

    def lookups(self, request, model_admin):
        return [('yes', 'Updated Posts')]

    def queryset(self, request, queryset):
        """Filter to show only posts that were modified after approval."""
        if self.value() == 'yes':
            return queryset.filter(is_approved=True, last_updated__gt=models.F('created_at'))
        return queryset

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'is_approved', 'is_published', 'is_headline', 'is_trending', 'to_slide', 'is_updated', 'review_status', 'admin_actions')
    list_filter = ('is_approved', 'is_published', 'is_headline', 'is_trending', 'to_slide')
    search_fields = ('title', 'author__username')
    actions = ['approve_selected', 'publish_selected', 'add_to_slide_selected', 'mark_as_trending_selected']

    def review_status(self, obj):
        """Displays the review status in Django Admin."""
        if obj.is_approved:
            return format_html('<span style="color: green;">Approved</span>')
        elif obj.rejection_reason:
            return format_html('<span style="color: red;">Rejected</span>')
        return format_html('<span style="color: orange;">Pending</span>')

    def admin_actions(self, obj):
        """Provides approve, reject, publish, headline, trending, and slide buttons."""
        return format_html(
            '<a class="button" href="/admin/blogs/blog/approve/{}/" style="color:green;">Approve</a> | '
            '<a class="button" href="/admin/blogs/blog/reject/{}/" style="color:red;">Reject</a> | '
            '<a class="button" href="/admin/blogs/blog/publish/{}/" style="color:blue;">Publish</a> | '
            '<a class="button" href="/admin/blogs/blog/toggle_headline/{}/" style="color:purple;">Headline</a> | '
            '<a class="button" href="/admin/blogs/blog/toggle_trending/{}/" style="color:orange;">Trending</a> | '
            '<a class="button" href="/admin/blogs/blog/toggle_slide/{}/" style="color:brown;">Slide</a>',
            obj.id, obj.id, obj.id, obj.id, obj.id, obj.id
        )

    def get_urls(self):
        """Adds custom admin URLs for approving, rejecting, publishing, and toggling statuses."""
        urls = super().get_urls()
        custom_urls = [
            path('approve/<int:post_id>/', self.admin_site.admin_view(self.approve_post), name='admin_approve_post'),
            path('reject/<int:post_id>/', self.admin_site.admin_view(self.reject_post), name='admin_reject_post'),
            path('publish/<int:post_id>/', self.admin_site.admin_view(self.publish_post), name='admin_publish_post'),
            path('toggle_headline/<int:post_id>/', self.admin_site.admin_view(self.toggle_headline), name='admin_toggle_headline'),
            path('toggle_trending/<int:post_id>/', self.admin_site.admin_view(self.toggle_trending), name='admin_toggle_trending'),
            path('toggle_slide/<int:post_id>/', self.admin_site.admin_view(self.toggle_slide), name='admin_toggle_slide'),
        ]
        return custom_urls + urls  

    # ✅ **Bulk Actions**
    @admin.action(description="Approve Selected Posts")
    def approve_selected(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f"{updated} post(s) approved successfully.", messages.SUCCESS)

    @admin.action(description="Publish Selected Posts")
    def publish_selected(self, request, queryset):
        updated = queryset.update(is_published=True)
        self.message_user(request, f"{updated} post(s) published successfully.", messages.SUCCESS)

    @admin.action(description="Add Selected Posts to Slide")
    def add_to_slide_selected(self, request, queryset):
        updated = queryset.update(to_slide=True)
        self.message_user(request, f"{updated} post(s) added to the slide.", messages.SUCCESS)

    @admin.action(description="Mark Selected Posts as Trending")
    def mark_as_trending_selected(self, request, queryset):
        updated = queryset.update(is_trending=True)
        self.message_user(request, f"{updated} post(s) marked as trending.", messages.SUCCESS)

    # ✅ **Single Post Actions**
    def approve_post(self, request, post_id):
        post = get_object_or_404(Blog, id=post_id)
        post.is_approved = True
        post.is_published = False  
        post.rejection_reason = None  
        post.save()
        messages.success(request, f'Post "{post.title}" has been approved but not yet published.')
        return redirect('/admin/blogs/blog/')

    def reject_post(self, request, post_id):
        post = get_object_or_404(Blog, id=post_id)
        post.is_approved = False
        post.is_published = False
        post.rejection_reason = "Your post did not meet the content guidelines.\n Kindly read the content guidelines and update your post for review"
        post.save()
        messages.error(request, f'Post "{post.title}" has been rejected.')
        return redirect('/admin/blogs/blog/')

    def publish_post(self, request, post_id):
        post = get_object_or_404(Blog, id=post_id)
        if not post.is_approved:
            messages.error(request, f'Cannot publish "{post.title}" because it is not approved.')
        else:
            post.is_published = True
            post.save()
            messages.success(request, f'Post "{post.title}" has been published successfully.')
        return redirect('/admin/blogs/blog/')

    def toggle_headline(self, request, post_id):
        post = get_object_or_404(Blog, id=post_id)
        post.is_headline = not post.is_headline
        post.save()
        status = "set as a headline" if post.is_headline else "removed from headlines"
        messages.success(request, f'Post "{post.title}" has been {status}.')
        return redirect('/admin/blogs/blog/')

    def toggle_trending(self, request, post_id):
        post = get_object_or_404(Blog, id=post_id)
        post.is_trending = not post.is_trending
        post.save()
        status = "set as trending" if post.is_trending else "removed from trending"
        messages.success(request, f'Post "{post.title}" has been {status}.')
        return redirect('/admin/blogs/blog/')

    def toggle_slide(self, request, post_id):
        post = get_object_or_404(Blog, id=post_id)
        post.to_slide = not post.to_slide
        post.save()
        status = "set to slide" if post.to_slide else "removed from slides"
        messages.success(request, f'Post "{post.title}" has been {status}.')
        return redirect('/admin/blogs/blog/')

from django.contrib import admin
from django.utils.html import format_html
from django.contrib import messages
from .models import UpdatedPost  # Import your model


@admin.register(UpdatedPost)
class UpdatedPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_status', 'approve_action', 'reject_action')
    actions = ['approve_selected', 'reject_selected']

    def get_status(self, obj):
        """ Show the status from the related Blog post. """
        if obj.original_post.is_approved:
            return "✅ Approved"
        elif obj.original_post.rejection_reason:
            return "❌ Rejected"
        return "⏳ Pending"

    get_status.short_description = "Status"

    def approve_selected(self, request, queryset):
        """ Approve the original blog post for selected updates. """
        for updated_post in queryset:
            blog_post = updated_post.original_post
            blog_post.is_approved = True
            blog_post.rejection_reason = ""  
            blog_post.save()

        self.message_user(request, "✅ Selected updates approved successfully.", messages.SUCCESS)

    approve_selected.short_description = "Approve selected updates"

    def reject_selected(self, request, queryset):
        """ Reject the original blog post for selected updates. """
        for updated_post in queryset:
            blog_post = updated_post.original_post
            blog_post.is_approved = False
            blog_post.rejection_reason = "❌ Rejected by admin"
            blog_post.save()

        self.message_user(request, "❌ Selected updates rejected.", messages.WARNING)

    reject_selected.short_description = "Reject selected updates"

    def approve_action(self, obj):
        """ Button to approve a single post. """
        request = HttpRequest()
        csrf_token = get_token(request) 
        return format_html(
            '''
            <form method="POST" action="{}">
                <input type="hidden" name="action" value="approve_selected">
                <input type="hidden" name="_selected_action" value="{}">
                <button type="submit" style="background:green;color:white;padding:5px 10px;border-radius:5px;border:none;cursor:pointer;">Approve</button>
            </form>
            ''',
            reverse('admin:blogs_updatedpost_changelist'),  # Admin action URL
            csrf_token,
            obj.id
        )

    def reject_action(self, obj):
        """ Button to reject a single post. """
        request = HttpRequest()
        csrf_token = get_token(request) 
        return format_html(
            '''
            <form method="POST" action="{}">
                <input type="hidden" name="action" value="reject_selected">
                <input type="hidden" name="_selected_action" value="{}">
                <button type="submit" style="background:red;color:white;padding:5px 10px;border-radius:5px;border:none;cursor:pointer;">Reject</button>
            </form>
            ''',
            reverse('admin:blogs_updatedpost_changelist'),
            csrf_token,
            obj.id
        )

    approve_action.allow_tags = True
    reject_action.allow_tags = True

admin.site.register(ContactMessage, ContactAdmin)
admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Comment)
admin.site.register(Profile)
admin.site.register(CustomUser)
admin.site.register(PremiumPayment)
admin.site.register(UserBadge)
admin.site.register(Badge)