from django.http import HttpResponse
from django.contrib.auth.decorators import permission_required

from .permissions import RestrictedModelPermission, GlobalPermission

@permission_required(RestrictedModelPermission)
def restricted_view(request):
    return HttpResponse("You've accessed a restricted_view")
