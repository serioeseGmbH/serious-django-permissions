from django.http import HttpResponse
from django.contrib.auth.decorators import permission_required

from .permissions import RestrictedModelPermission, GlobalPermission

@permission_required(RestrictedModelPermission)
def restricted_model_view(request):
    return HttpResponse("You've accessed restricted_model_view")

@permission_required(GlobalPermission)
def restricted_global_view(request):
    return HttpResponse("You've accessed restricted_global_view")
