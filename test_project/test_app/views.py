from django.http import HttpResponse
from django.contrib.auth.decorators import permission_required

from .permissions import RestrictedModelPermission, GlobalPermission,\
    ExplicitReferenceToRestrictedModelPermission

@permission_required(RestrictedModelPermission)
def restricted_model_view(request):
    return HttpResponse("You've accessed restricted_model_view")

@permission_required(ExplicitReferenceToRestrictedModelPermission)
def restricted_model_with_explicit_reference_view(request):
    return HttpResponse("You've accessed restricted_model_with_explicit_reference_view")

@permission_required(GlobalPermission)
def restricted_global_view(request):
    return HttpResponse("You've accessed restricted_global_view")
