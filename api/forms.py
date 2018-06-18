from django import forms
from django.contrib.admin.widgets import AdminFileWidget
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.utils.translation import ugettext_lazy as _

from api.models import Case, User, PaperDocument, EDocument


class LoginForm(AuthenticationForm):

    password = forms.CharField(label=_('Password:'), widget=forms.PasswordInput)

    def clean_password(self):
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        valid = True
        try:
            user = User.objects.get(email=email)
            if not user.check_password(password):
                valid = False
        except ObjectDoesNotExist:
            valid = False
        if not valid: raise ValidationError(_('Wrong password. Try again...'))
        return password

    def confirm_login_allowed(self, user):

        if not user.is_active:
            raise forms.ValidationError(
                self.error_messages['inactive'],
                code='inactive',
            )


class CaseForm(forms.ModelForm):

    description = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = Case
        fields=('identifier',
                'passcode',
                'submition_datetime',
                'description',
                'status',
                'type',
                'executor',
                'checkpoint',)


class PaperDocumentForm(forms.ModelForm):

    class Meta:
        model = PaperDocument
        fields="__all__"

    def __init__(self, *args, **kwargs):
        try:
            case_id = kwargs.pop('case_id')
        except KeyError:
            has_key = False
        else:
            has_key = True
        super(PaperDocumentForm,self).__init__(*args,**kwargs)
        if has_key:
            self.fields['case'].queryset = Case.objects.filter(id=case_id).all()


class CaseAddForm(forms.ModelForm):

    description = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = Case
        fields = ('submition_datetime',
                  'description',
                  'type',)


class EDocumentForm(forms.ModelForm):

    file = forms.FileField(widget=AdminFileWidget)

    class Meta:
        model = EDocument
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        try:
            case_id = kwargs.pop('case_id')
        except KeyError:
            has_key = False
        else:
            has_key = True
        super(EDocumentForm,self).__init__(*args,**kwargs)
        if has_key:
            self.fields['case'].queryset = Case.objects.filter(id=case_id).all()








