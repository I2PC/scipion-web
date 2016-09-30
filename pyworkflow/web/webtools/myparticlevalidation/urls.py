from django.conf.urls import url
from pyworkflow.web.webtools.myparticlevalidation import views
from pyworkflow.web.webtools.myparticlevalidation.views import MYPVAL_SERVICE, MYPVAL_FORM_URL

urls = [
    url('^' + MYPVAL_SERVICE + '$', views.particleValidation_projects),
    url(r'^create_pval_project/$', views.create_particleValidation_project),
    url('^' + MYPVAL_FORM_URL + '/$', views.particleValidation_form),
    url(r'^p_content$', views.particleValidation_content)
]


