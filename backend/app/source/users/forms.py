from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Company

# パスワードも設定する場合は、UserCreationFormを継承する、今回はパスワードを設定したくないため、ModelFormを継承する
class CreateUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['company_id', 'email']

    def __init__(self, *args, **kwargs):
           super(CreateUserForm, self).__init__(*args, **kwargs)
           self.fields['company_id'].disabled = True

class CreateAdminUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['company_id', 'username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
           super(CreateAdminUserForm, self).__init__(*args, **kwargs)
           self.fields['company_id'].disabled = True


# 削除するデータの日付と時刻を指定するフォーム
class DeleteDataForm(forms.Form):
    class Meta:
        model = Company
        fields = ['msg', 'date', 'time']

    def __init__(self, *args, **kwargs):
        super(DeleteDataForm, self).__init__(*args, **kwargs)
        # date = forms.DateField(label='日付', input_formats=['%Y-%m-%d'])
        self.fields['date'] = forms.DateField(label='日付', input_formats=['%Y-%m-%d'], widget=forms.DateInput(attrs={'type': 'date'}))
        self.fields['time'] = forms.TimeField(label='時刻', input_formats=['%H:%M'], widget=forms.TimeInput(attrs={'type': 'time'}))
