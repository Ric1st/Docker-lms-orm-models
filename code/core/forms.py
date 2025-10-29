from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm 
from .models import Course

class UserEditForm(forms.ModelForm):
    # Field tambahan untuk kontrol Staff/Admin
    is_staff = forms.BooleanField(
        label='Status Staff (Bisa Mengelola Kursus)',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    class Meta:
        model = User
        # Kita hanya mengizinkan edit field berikut dari frontend
        fields = ['username', 'first_name', 'last_name', 'email', 'is_active', 'is_staff']
        
        # Tambahkan kelas Bootstrap ke widget
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}), 
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['is_active'].label = 'Akun Aktif (Dapat Login)'


# --- 2. Form untuk Menambahkan User Baru (Digunakan oleh user_create view) ---
class UserAddForm(UserCreationForm):
    first_name = forms.CharField(label='Nama Depan', max_length=150, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(label='Nama Belakang', max_length=150, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label='Email', required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    is_staff = forms.BooleanField(
        label='Tetapkan sebagai Staff',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email', 'is_staff')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Menyesuaikan widget bawaan UserCreationForm
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
     
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
        
    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        user.email = self.cleaned_data.get('email')
        user.is_staff = self.cleaned_data.get('is_staff')
        if commit:
            user.save()
        return user
    
class RegisterForm(UserCreationForm):
    first_name = forms.CharField( label='Nama Depan', max_length=150, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(label='Nama Belakang', max_length=150, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField( label='Email', required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.setdefault('class', 'form-control')

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['teacher', 'name', 'description', 'price', 'image']
        widgets = {
            'teacher': forms.Select(attrs={
                'class': 'form-select text-dark',
                'id': 'teacherSelect',
                'data-bs-toggle': 'dropdown',
            }),
            'name': forms.TextInput(attrs={'class': 'form-control text-dark'}),
            'description': forms.Textarea(attrs={'class': 'form-control text-dark', 'rows': 3}),
            'price': forms.NumberInput(attrs={'class': 'form-control text-dark'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }