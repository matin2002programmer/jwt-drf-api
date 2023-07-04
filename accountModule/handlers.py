from corsheaders.signals import check_request_enabled

from accountModule.models import User


def cors_allow_mysites(sender, request, **kwargs):
    print(request)
    return User.objects.filter(host=request.headers["Origin"]).exists()


print(check_request_enabled.connect(cors_allow_mysites))
