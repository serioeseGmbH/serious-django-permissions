from django.http import HttpResponse
from django.contrib.auth.decorators import permission_required


@permission_required('test_app.restricted_model')
def restricted_view(request):
    return HttpResponse("You've accessed a restricted_view")
