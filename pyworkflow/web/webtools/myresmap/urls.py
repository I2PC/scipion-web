import os
from django.conf.urls import url
from django.conf.urls.static import static

import pyworkflow as pw
from pyworkflow.web.app.views_util import ownRedirect
from pyworkflow.web.webtools.myresmap import views

MEDIA_MYRESMAP = os.path.join(pw.HOME, 'web', 'webtools', 'myresmap', 'resources')

urls = [
    # (r'^resources_myresmap/(?P<path>.*)$',
    #     'django.views.static.serve',
    #     {'document_root': MEDIA_MYRESMAP}
    # ),
    #
    url(r'^myresmap$', views.resmap_projects),
    url(r'^create_resmap_project/$', views.create_resmap_project),
    url(r'^r_form/$', views.resmap_form),
    url(r'^r_content$', views.resmap_content),
    url(r'^r_content/$', ownRedirect, {'url': '../r_content', 'permanent': False}),

]

urls += static('^resources_myresmap/(?P<path>.*)$', document_root=MEDIA_MYRESMAP)