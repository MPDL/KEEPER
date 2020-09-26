from django.shortcuts import render

from seahub.auth.decorators import login_required

@login_required
def project_catalog(request):
    """
    Get project catalog, first call
    """
    template = 'project_catalog_react.html'

    return render(request, template, {
            'current_page': 1,
            'per_page': 25,
            })