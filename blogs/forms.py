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
        username = self.cleaned_data.get('facebook')
        return f"https://www.facebook.com/{username}" if username else ""

    def clean_twitter(self):
        username = self.cleaned_data.get('twitter')
        return f"https://www.twitter.com/{username}" if username else ""

    def clean_x(self):
        username = self.cleaned_data.get('x')
        return f"https://www.x.com/{username}" if username else ""

    def clean_tiktok(self):
        username = self.cleaned_data.get('tiktok')
        return f"https://www.tiktok.com/@{username}" if username else ""