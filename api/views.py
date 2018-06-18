from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.views import LoginView
from django.db.models import Q
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView, CreateView, UpdateView

from api.forms import LoginForm, CaseAddForm, CaseForm
from api.models import Case


class LoginAuthView(LoginView):

    template_name = 'login.html'
    form_class = LoginForm

    def form_invalid(self,form):
        response = super(LoginView, self).form_invalid(form)
        messages.error(self.request, _('Email or password invalid. Please try again'))
        return response


class DashboardPage(LoginRequiredMixin, UserPassesTestMixin, TemplateView):

    template_name = 'dashboard.html'

    def test_func(self):
        test_result = self.request.user.is_manager or self.request.user.is_employee
        if not test_result:
            messages.info(self.request,_("Permission denied!"))
        return test_result

    def get(self, request, *args, **kwargs):
        cases = Case.objects.all()
        unreviwed = cases.filter(status=Case.NA).all()
        reviewed = cases.filter(Q(status=Case.ACCEPTED)|Q(status=Case.DECLINED)).all()
        return render(request, self.template_name,{'unreviewed':unreviwed,"reviewed":reviewed})


class CaseCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):

    model = Case
    form_class = CaseAddForm
    template_name = 'create_case.html'
    success_url = reverse_lazy('dashboard')

    def test_func(self):
        test_result = self.request.user.is_manager
        if not test_result:
            messages.error(self.request, _("Permission denied!"))
        return test_result


class CaseUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):

    model = Case
    form_class = CaseForm
    template_name = 'update_case.html'
    success_url = reverse_lazy('dashboard')

    def test_func(self):
        test_result = self.request.user.is_manager
        if not test_result:
            messages.error(self.request, _("Permission denied!"))
        return test_result




