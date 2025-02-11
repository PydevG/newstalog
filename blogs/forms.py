from django import forms
from .models import ContactMessage, Blog
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
        fields = ['title', 'content', 'category', 'tags', 'image', 'is_published']
