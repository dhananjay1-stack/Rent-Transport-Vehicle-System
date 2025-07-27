
def is_host(request):
    if request.user.is_authenticated:
        return {'is_host': request.user.groups.filter(name='Host').exists()}
    return {'is_host': False}
