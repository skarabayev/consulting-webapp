from django import forms
from django.contrib import admin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group

from api.forms import CaseForm
from .models import User, Manager, Employee, Case, CaseType, Location, Locker


class UserCreationForm(forms.ModelForm):

    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        exclude = ("password","last_login")

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):

    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        exclude = ("last_login",)
        readonly_fields = ['is_manager', 'is_employee']


    def clean_password(self):
        return self.initial["password"]


class UserAdminForm(BaseUserAdmin):

    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ('full_name','email','active','admin')
    list_filter = ('active','admin')
    fieldsets = (
        ('Personal info', {'fields': ('first_name','last_name','email',)}),
        ("Password hash", {'fields': ('password',)}),
        ('Permissions', {'fields': ('staff','active','admin',)}),
        ('Profile type', {'fields': ('is_manager','is_employee',)}),
    )

    add_fieldsets = (
        ('Personal info', {
            'fields': ('first_name','last_name','email',)}
         ),
        (None, {'fields': ('password1', 'password2',)}),
        ('Permissions', {'fields': ('staff', 'active', 'admin',)}),
        ('Profile type', {'fields': ('is_manager', 'is_employee',)}),
    )

    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()


class CaseModelAdmin(admin.ModelAdmin):

    form = CaseForm

    readonly_fields = ('identifier','passcode')
    list_display = ('identifier', 'submition_datetime', 'status')
    list_filter = ('status',)


admin.site.unregister(Group)

# Users
admin.site.register(User, UserAdminForm)

# Models
admin.site.register(Case, CaseModelAdmin)
admin.site.register(CaseType)
admin.site.register(Locker)
admin.site.register(Location)
