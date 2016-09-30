from django.conf.urls import url
from pyworkflow.web.webtools.movies import views
from pyworkflow.web.webtools.movies.views import MOVIES_SERVICE_URL
from pyworkflow.web.app.views_util import ownRedirect


urls = [
    url(r'^' + MOVIES_SERVICE_URL + '$', views.service_movies),
    url(r'^create_movies_project/$', views.create_movies_project),
    url(r'^mov_form/$', views.movies_form),
    url(r'^m_content$', views.movies_content, name='movies'),
    url(r'^m_content/$', ownRedirect, {'url': '../m_content', 'permanent': False}),
]

