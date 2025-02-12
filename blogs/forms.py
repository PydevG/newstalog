from django import forms
from .models import ContactMessage, Blog, Profile
from ckeditor.widgets import CKEditorWidget 

class ContactMessageReplyForm(forms.ModelForm):
    reply = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'cols': 40}),
        required=False,
        label="Reply",
    )

    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'message', 'reply']
        widgets = {
            'name': forms.TextInput(attrs={'readonly': 'readonly'}),
            'email': forms.EmailInput(attrs={'readonly': 'readonly'}),
            'message': forms.Textarea(attrs={'readonly': 'readonly'}),
        }


class BlogForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorWidget())
    class Meta:
        model = Blog
        fields = ['title', 'content', 'category', 'image', 'is_published']
        
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_picture', 'bio', 'website', 'facebook', 'twitter', 'x', 'tiktok']
    
    def clean_facebook(self):
        url = (self.cleaned_data.get('facebook') or "").strip()
        if url and not url.startswith("https://www.facebook.com/"):
            return f"https://www.facebook.com/{url.lstrip('/')}"
        return url

    def clean_twitter(self):
        url = (self.cleaned_data.get('twitter') or "").strip()
        if url and not url.startswith("https://www.twitter.com/"):
            return f"https://www.twitter.com/{url.lstrip('/')}"
        return url

    def clean_x(self):
        url = (self.cleaned_data.get('x') or "").strip()
        if url and not url.startswith("https://www.x.com/"):
            return f"https://www.x.com/{url.lstrip('/')}"
        return url

    def clean_tiktok(self):
        url = (self.cleaned_data.get('tiktok') or "").strip()
        if url and not url.startswith("https://www.tiktok.com/@"):
            return f"https://www.tiktok.com/@{url.lstrip('@/')}"
        return url
