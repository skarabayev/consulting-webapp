from django.conf.urls import url
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns=[
    url(r"^login/$", views.LoginAuthView.as_view(), name='login'),
    url(r"^dashboard/$", views.DashboardPage.as_view(), name='dashboard'),
    url(r'^cases/create/$',views.CaseCreateView.as_view(), name="create"),
    url(r'cases/(?P<pk>\d+)/update/$',views.CaseUpdateView.as_view(), name='update'),
    url(r"^logout/$", LogoutView.as_view(), name='logout'),
]
