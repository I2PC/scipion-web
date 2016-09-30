from django.conf.urls import url
from pyworkflow.web.webtools import views_webtools
from pyworkflow.web.webtools.myfirstmap.views import MYFIRSTMAP_SERVICE_URL
from pyworkflow.web.app.views_util import ownRedirect

urls = [
    url(r'^'+ MYFIRSTMAP_SERVICE_URL +'$', views_webtools.service_projects),
    url(r'^create_service_project/$', views_webtools.create_service_project),
    url(r'^get_testdata/$', views_webtools.get_testdata),
    url(r'^my_form/$', views_webtools.myfirstmap_form),
    url(r'^content', views_webtools.service_content),
    url(r'^content/$', ownRedirect, {'url': '../content', 'permanent': False}),
]
