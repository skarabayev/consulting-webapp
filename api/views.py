from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.views import LoginView
from django.db.models import Q
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_http_methods
from django.views.generic import TemplateView, CreateView, UpdateView, DetailView, DeleteView
from rest_framework import viewsets

from api.forms import LoginForm, CaseAddForm, CaseForm, PaperDocumentForm, EDocumentForm, CaseCheckpointForm, \
    CaseStatusForm
from api.models import Case, PaperDocument, EDocument, CaseType
from api.serializers import CaseSerializer


class LoginAuthView(LoginView):

    template_name = 'login.html'
    form_class = LoginForm

    def form_invalid(self,form):
        response = super(LoginView, self).form_invalid(form)
        messages.error(self.request, _('Email or password invalid. Please try again'))
        return response


class DashboardPage(LoginRequiredMixin, UserPassesTestMixin, TemplateView):

    template_name = 'dashboard/dashboard.html'

    def test_func(self):
        test_result = self.request.user.is_manager or self.request.user.is_employee
        if not test_result:
            messages.info(self.request,_("Permission denied!"))
        return test_result

    def get(self, request, *args, **kwargs):
        cases = Case.objects.all()
        if request.user.is_manager:
            unreviwed = cases.filter(status=Case.NA).all()
            reviewed = cases.filter(Q(status=Case.ACCEPTED)|Q(status=Case.DECLINED)).all()
            return render(request, self.template_name,{'unreviewed':unreviwed,"reviewed":reviewed})
        else:
            accepted = cases.filter(executor=request.user.employee).all()
            return render(request, self.template_name, {'accepted':accepted})


class CaseCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):

    model = Case
    form_class = CaseAddForm
    template_name = 'case/create_case.html'
    success_url = reverse_lazy('dashboard')

    def test_func(self):
        test_result = self.request.user.is_manager
        if not test_result:
            messages.error(self.request, _("Permission denied!"))
        return test_result


class CaseUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):

    model = Case
    form_class = CaseForm
    template_name = 'case/update_case.html'
    success_url = reverse_lazy('dashboard')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['id'] = int(self.kwargs.get('pk'))
        return data

    def test_func(self):
        test_result = self.request.user.is_manager
        if not test_result:
            messages.error(self.request, _("Permission denied!"))
        return test_result


class CaseFilesEditView(LoginRequiredMixin, UserPassesTestMixin, DetailView):

    model = Case
    template_name = 'case/files_edit_case.html'

    def test_func(self):
        test_result = self.request.user.is_employee
        if not test_result:
            messages.error(self.request, _("Permission denied!"))
        return test_result


class CaseCheckpointView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):

    model = Case
    form_class = CaseCheckpointForm
    template_name = 'case/checkpoint_case.html'
    success_url = reverse_lazy('dashboard')

    def test_func(self):
        test_result = self.request.user.is_employee
        if not test_result:
            messages.error(self.request, _("Permission denied!"))
        return test_result

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['title'] = 'Update paper document'
        data['cid'] = int(self.kwargs.get('pk'))
        return data

    def get_success_url(self):
        case_id = int(self.kwargs.get('pk'))
        case = Case.objects.get(id=case_id)
        return reverse_lazy('edit', kwargs={'pk':case.pk})


class CaseDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):

    model = Case
    template_name = 'case/delete_case.html'

    def test_func(self):
        test_result = self.request.user.is_manager
        if not test_result:
            messages.error(self.request, _("Permission denied!"))
        return test_result

    def get_success_url(self):
        return reverse_lazy('dashboard')


class PaperDocumentCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):

    model = PaperDocument
    form_class = PaperDocumentForm
    template_name = 'documents/paperdocument.html'

    def test_func(self):
        if not self.request.user.is_employee:
            return False
        case_id = int(self.kwargs.get('cid'))
        case = Case.objects.get(id=case_id)
        test_result = case.executor_id == self.request.user.employee.id
        if not test_result:
            messages.error(self.request, _("Permission denied!"))
        return test_result

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['title'] = 'Create paper document'
        data['cid'] = int(self.kwargs.get('cid'))
        return data

    def get_success_url(self):
        return reverse_lazy('edit', kwargs={'pk':int(self.kwargs.get('cid'))})

    def get_form_kwargs(self):
        kwargs = super(PaperDocumentCreateView, self).get_form_kwargs()
        kwargs['case_id'] = int(self.kwargs.get('cid'))
        return kwargs


class PaperDocumentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = PaperDocument
    form_class = PaperDocumentForm
    template_name = 'documents/paperdocument.html'

    def test_func(self):
        if not self.request.user.is_employee:
            return False
        document_id = int(self.kwargs.get('pk'))
        document = PaperDocument.objects.get(id=document_id)
        test_result = document.case.executor_id == self.request.user.employee.id
        if not test_result:
            messages.error(self.request, _("Permission denied!"))
        return test_result

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['title'] = 'Update paper document'
        document_id = int(self.kwargs.get('pk'))
        document = PaperDocument.objects.get(id=document_id)
        data['cid'] = document.case_id
        return data

    def get_success_url(self):
        document_id = int(self.kwargs.get('pk'))
        document = PaperDocument.objects.get(id=document_id)
        return reverse_lazy('edit', kwargs={'pk':document.case_id})

    def get_form_kwargs(self):
        kwargs = super(PaperDocumentUpdateView, self).get_form_kwargs()
        document_id = int(self.kwargs.get('pk'))
        document = PaperDocument.objects.get(id=document_id)
        kwargs['case_id'] = document.case_id
        return kwargs


class PaperDocumentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):

    model = PaperDocument
    template_name = 'documents/delete_document.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['title'] = 'Delete "{}"'.format(self.object.name)
        document_id = int(self.kwargs.get('pk'))
        document = self.model.objects.get(id=document_id)
        data['cid'] = document.case_id
        return data

    def test_func(self):
        if not self.request.user.is_employee:
            return False
        document_id = int(self.kwargs.get('pk'))
        document = self.model.objects.get(id=document_id)
        test_result = document.case.executor_id == self.request.user.employee.id
        if not test_result:
            messages.error(self.request, _("Permission denied!"))
        return test_result

    def get_success_url(self):
        document_id = int(self.kwargs.get('pk'))
        document = self.model.objects.get(id=document_id)
        return reverse_lazy('edit', kwargs={'pk': document.case_id})

class EDocumentCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):

    model = EDocument
    form_class = EDocumentForm
    template_name = 'documents/edocument.html'

    def test_func(self):
        if not self.request.user.is_employee:
            return False
        case_id = int(self.kwargs.get('cid'))
        case = Case.objects.get(id=case_id)
        test_result = case.executor_id == self.request.user.employee.id
        if not test_result:
            messages.error(self.request, _("Permission denied!"))
        return test_result

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['title'] = 'Create E-document'
        data['cid'] = int(self.kwargs.get('cid'))
        return data

    def get_success_url(self):
        return reverse_lazy('edit', kwargs={'pk':int(self.kwargs.get('cid'))})

    def get_form_kwargs(self):
        kwargs = super(EDocumentCreateView, self).get_form_kwargs()
        kwargs['case_id'] = int(self.kwargs.get('cid'))
        return kwargs


class EDocumentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):

    model = EDocument
    form_class = EDocumentForm
    template_name = 'documents/edocument.html'

    def test_func(self):
        if not self.request.user.is_employee:
            return False
        document_id = int(self.kwargs.get('pk'))
        document = EDocument.objects.get(id=document_id)
        test_result = document.case.executor_id == self.request.user.employee.id
        if not test_result:
            messages.error(self.request, _("Permission denied!"))
        return test_result

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['title'] = 'Update E-document'
        document_id = int(self.kwargs.get('pk'))
        document = EDocument.objects.get(id=document_id)
        data['cid'] = document.case_id
        return data

    def get_success_url(self):
        document_id = int(self.kwargs.get('pk'))
        document = EDocument.objects.get(id=document_id)
        return reverse_lazy('edit', kwargs={'pk': document.case_id})

    def get_form_kwargs(self):
        kwargs = super(EDocumentUpdateView, self).get_form_kwargs()
        document_id = int(self.kwargs.get('pk'))
        document = EDocument.objects.get(id=document_id)
        kwargs['case_id'] = document.case_id
        return kwargs


class EDocumentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):

    model = EDocument
    template_name = 'documents/delete_document.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['title'] = 'Delete "{}"'.format(self.object.name)
        document_id = int(self.kwargs.get('pk'))
        document = EDocument.objects.get(id=document_id)
        data['cid'] = document.case_id
        return data

    def test_func(self):
        if not self.request.user.is_employee:
            return False
        document_id = int(self.kwargs.get('pk'))
        document = EDocument.objects.get(id=document_id)
        test_result = document.case.executor_id == self.request.user.employee.id
        if not test_result:
            messages.error(self.request, _("Permission denied!"))
        return test_result

    def get_success_url(self):
        document_id = int(self.kwargs.get('pk'))
        document = EDocument.objects.get(id=document_id)
        return reverse_lazy('edit', kwargs={'pk': document.case_id})


class CaseViewSet(viewsets.ModelViewSet):
    queryset = Case.objects.all()
    serializer_class = CaseSerializer


@require_http_methods(['GET','POST'])
def check_status(request, *args, **kwargs):
    if request.method == 'POST':
        form = CaseStatusForm(request.POST)
        if form.is_valid():
            case = Case.objects.get(identifier=form.cleaned_data['identifier'])
            return render(request, 'case/status_case.html', {"case":case})
        messages.error(request, "Wrong indentifier or passcode!")
    else:
        form = CaseStatusForm()
    return render(request, 'case/status_form.html', {"form":form})

@require_http_methods("GET")
@user_passes_test(lambda user: user.is_manager or user.is_employee)
@login_required
def download_script(request, *agrs, **kwargs):
    script_id = int(kwargs.get('pk'))
    script = CaseType.objects.get(id=script_id)
    filename = script.case_script.name.split('/')[-1]
    response = HttpResponse(script.case_script, content_type='application/octet-stream')
    response['Content-Disposition'] = 'attachment; filename={}'.format(filename)
    return response

@require_http_methods("GET")
@user_passes_test(lambda user: user.is_employee)
@login_required
def download_edocument(request, *args, **kwargs):
    document_id = int(kwargs.get('pk'))
    document = EDocument.objects.get(id=document_id)
    if document.case.executor_id == request.user.employee.id:
        filename = document.file.name.split('/')[-1]
        response = HttpResponse(document.file, content_type='application/octet-stream')
        response['Content-Disposition'] = 'attachment; filename={}'.format(filename)
        return response
    return HttpResponseForbidden()



