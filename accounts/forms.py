from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Profile, JobPost

INPUT_STYLE = (
    "w-full px-3.5 py-2.5 rounded-xl bg-slate-950 "
    "border border-slate-800 text-slate-100 "
    "placeholder-slate-500 focus:outline-none "
    "focus:border-blue-500 transition text-xs"
)

class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'name@company.com'})
    )
    role = forms.ChoiceField(
        choices=CustomUser.ROLE_CHOICES,
        widget=forms.Select()
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'role')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = INPUT_STYLE

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'skills', 'education', 'institution', 'grad_year', 'location', 'points']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe your experience, technical skills, and background...'}),
            'skills': forms.TextInput(attrs={'placeholder': 'Python, Django, HTML, CSS...'}),
            'education': forms.TextInput(attrs={'placeholder': 'e.g. Diploma in Computer Technology'}),
            'institution': forms.TextInput(attrs={'placeholder': 'e.g. Mumbai University'}),
            'grad_year': forms.NumberInput(attrs={'placeholder': 'e.g. 2026'}),
            'location': forms.TextInput(attrs={'placeholder': 'e.g. Thane, India'}),
            'points': forms.NumberInput(attrs={'placeholder': 'e.g. 10000'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # accept user from the view
        super().__init__(*args, **kwargs)

        # Only clients should see/edit points
        if not user or user.role != 'client':
            self.fields.pop('points', None)

        for field in self.fields.values():
            existing_classes = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f"{INPUT_STYLE} {existing_classes}".strip()


class JobPostForm(forms.ModelForm):
    class Meta:
        model = JobPost
        fields = ['title', 'description', 'budget', 'location', 'deadline', 'repo_url', 'attachments_url']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Job Title'}),
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Job details...'}),
            'budget': forms.NumberInput(attrs={'placeholder': '500.00', 'step': '0.01'}),
            'location': forms.TextInput(attrs={'placeholder': 'Remote / Location'}),
            'deadline': forms.DateInput(attrs={'type': 'date'}),
            'repo_url': forms.URLInput(attrs={'placeholder': 'https://github.com/...'}),
            'attachments_url': forms.URLInput(attrs={'placeholder': 'https://...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            existing_classes = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f"{INPUT_STYLE} {existing_classes}".strip()