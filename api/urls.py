from django.conf.urls import url
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns=[
    url(r"^login/$", views.LoginAuthView.as_view(), name='login'),
    url(r"^dashboard/$", views.DashboardPage.as_view(), name='dashboard'),
    url(r'^cases/create/$',views.CaseCreateView.as_view(), name="create"),
    url(r'^cases/update/(?P<pk>\d+)$',views.CaseUpdateView.as_view(), name='update'),
    url(r'^cases/edit/(?P<pk>\d+)$', views.CaseFilesEditView.as_view(), name='edit'),
    url(r'^cases/delete/(?P<pk>\d+)$', views.CaseDeleteView.as_view(), name='delete'),
    url(r'^documents/create/(?P<cid>\d+)$',views.PaperDocumentCreateView.as_view(),name='new_paper'),
    url(r'^documents/update/(?P<pk>\d+)$',views.PaperDocumentUpdateView.as_view(),name='update_paper'),
    url(r'^documents/delete/(?P<pk>\d+)$', views.PaperDocumentDeleteView.as_view(), name='delete_pdoc'),
    url(r'^edocuments/create/(?P<cid>\d+)$',views.EDocumentCreateView.as_view(),name='new_edoc'),
    url(r'^edocuments/update/(?P<pk>\d+)$',views.EDocumentUpdateView.as_view(),name='update_edoc'),
    url(r'^edocuments/download/(?P<pk>\d+)$', views.download_edocument, name='download'),
    url(r'^edocuments/delete/(?P<pk>\d+)$', views.EDocumentDeleteView.as_view(), name='delete_edoc'),
    url(r'^scripts/(?P<pk>\d+)$', views.download_script, name="download_script"),
    url(r"^logout/$", LogoutView.as_view(), name='logout'),
]
