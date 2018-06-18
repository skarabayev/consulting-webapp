from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.crypto import get_random_string


class UserManager(BaseUserManager):

    def create(self, first_name, last_name, password, email, active=True, staff=False, admin=False):
        if not first_name:
            raise ValueError(_('First name is empty: '), first_name)
        if not last_name:
            raise ValueError(_('Password is empty: '), last_name)
        if not email:
            raise ValueError(_('Email is empty: '), email)
        user = self.model(first_name=first_name, last_name=last_name)
        user.set_password(password)
        user.email = self.normalize_email(email)
        user.active = active
        user.staff = staff
        user.admin = admin
        user.save(using=self._db)
        return user

    def create_superuser(self, first_name, last_name, password, email):
        if not first_name:
            raise ValueError(_('First name is empty: '), first_name)
        if not last_name:
            raise ValueError(_('Password is empty: '), last_name)
        if not email:
            raise ValueError(_('Email is empty: '), email)
        user = self.model(first_name=first_name,
                          last_name=last_name,
                          staff=True,
                          admin=True)
        user.set_password(password)
        user.email = self.normalize_email(email)
        user.save(using=self._db)


class User(AbstractBaseUser):
    email = models.EmailField(blank=False, null=True, unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    active = models.BooleanField(default=True)
    staff = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)
    is_manager = models.BooleanField(default=False)
    is_employee = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name','last_name']
    objects = UserManager()

    @property
    def full_name(self):
        return "{} {}".format(self.first_name, self.last_name)

    @property
    def is_active(self):
        return self.active

    @property
    def is_staff(self):
        return self.staff

    @property
    def is_admin(self):
        return self.admin

    @property
    def is_superuser(self):
        return self.admin

    def has_perm(self, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    def clean(self):
        super().clean()
        if self.is_employee and self.is_manager:
            raise ValidationError(_("User cannot be manager and employee at the same time..."))

    def save(self, *args, **kwargs):
        super().save(*args,**kwargs)
        if self.is_manager:
            if not hasattr(self,'manager'):
                self.manager = Manager.objects.create(user=self)
        elif self.is_employee:
            if not hasattr(self, 'employee'):
                self.employee = Employee.objects.create(user=self)

    def __str__(self):
        return self.full_name


class Manager(models.Model):

    user = models.OneToOneField('api.User', on_delete=models.CASCADE, blank=False)

    def __str__(self):
        return "{} {}".format(self.__class__.__name__, str(self.user))


class Employee(models.Model):

    user = models.OneToOneField('api.User', on_delete=models.CASCADE, blank=False)

    def __str__(self):
        return "{} {}".format(self.__class__.__name__, str(self.user))


class CaseType(models.Model):
    name = models.CharField(max_length=30)
    case_script = models.FileField(upload_to="scripts/")

    def __str__(self):
        return self.name


class Checkpoint(models.Model):

    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class Case(models.Model):

    NA = 0
    ACCEPTED = 1
    DECLINED = 2

    choices = (
        (NA,"Not reviewed"),
        (ACCEPTED,"Accepted"),
        (DECLINED,"Declined"),
    )

    identifier = models.CharField(max_length=30, unique=True)
    passcode = models.CharField(max_length=20)
    submition_datetime = models.DateTimeField()
    description = models.CharField(max_length=500)
    status = models.IntegerField(choices=choices, default=NA)
    checkpoint = models.ForeignKey('api.Checkpoint', on_delete=models.PROTECT, null=True)
    type = models.ForeignKey("api.CaseType", on_delete=models.PROTECT)
    executor = models.ForeignKey("api.Employee", on_delete=models.PROTECT,
                                 blank=True,
                                 null=True)


    @staticmethod
    def generate_unique(length):
        return get_random_string(length)

    def clean(self):
        super().clean()
        if self.executor:
            if not (self.status == self.ACCEPTED):
                raise ValidationError({'executor':"Cannot allocate case to employee until case is not accepted."})

    def save(self, *args, **kwargs):
        if not self.id:
            self.identifier = Case.generate_unique(30)
            self.passcode = Case.generate_unique(20)
        super().save(*args,**kwargs)

    def __str__(self):
        return "ID: {}".format(self.identifier)


class DocumentType(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class Document(models.Model):
    name = models.CharField(max_length=50)
    type = models.ForeignKey("api.DocumentType", on_delete=models.PROTECT)
    case = models.ForeignKey("api.Case", on_delete=models.CASCADE)

    class Meta:
        abstract = True

    def __str__(self):
        return "{} {} {}".format(self.name,self.type.name,str(self.case))


class PaperDocument(Document):
    locker = models.ForeignKey("api.Locker", on_delete=models.PROTECT)


class EDocument(Document):
    file = models.FileField(upload_to="documents/")


class Locker(models.Model):
    identifier = models.IntegerField()
    location = models.ForeignKey("api.Location", on_delete=models.PROTECT, blank=False)

    def __str__(self):
        return "{} {}".format(self.identifier, str(self.location))

    def get_location(self):
        return self.__str__()


class Location(models.Model):
    ARCHIVE = "ARCHIVE"
    OFFICE = "OFFICE"

    types = (
        (ARCHIVE, "Archive"),
        (OFFICE, "Office"),
    )

    type = models.CharField(max_length=20, choices=types, blank=False)

    def __str__(self):
        return self.get_type_display()
