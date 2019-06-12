from django.urls import resolve, Resolver404


def appname(request):
    try:
        app_label = resolve(request.path).app_name
    except Resolver404:
        app_label = None
    return {'appname': app_label}