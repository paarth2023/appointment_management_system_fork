from rest_framework.test import APIRequestFactory, force_authenticate

factory = APIRequestFactory()


def internal_get(view, path, user, **kwargs):
    request = factory.get(path)
    force_authenticate(request, user=user)
    return view(request, **kwargs)


def internal_post(view, path, user, data=None, **kwargs):
    request = factory.post(path, data=data or {}, format="json")
    force_authenticate(request, user=user)
    return view(request, **kwargs)
