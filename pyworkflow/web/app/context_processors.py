from pyworkflow.web.app.views_util import getAbsoluteURL


def app(request):
    return {
        'abs_url': getAbsoluteURL()
    }