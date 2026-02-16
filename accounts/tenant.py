def get_request_tenant(request):
    
    user = request.user
    if not user.is_authenticated:
        return None
    if getattr(user, "role", None) == "ADMIN":
        return None
    return getattr(user, "tenant", None)
