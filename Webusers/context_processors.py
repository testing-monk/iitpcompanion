from django.shortcuts import get_object_or_404
from Webusers.models import Users, UserProfile

def users_context(request):
    user_id = request.session.get('user_id')
    webuser = None
    profile = None

    if user_id:
        try:
            webuser = Users.objects.get(id=user_id)
            profile, created = UserProfile.objects.get_or_create(user=webuser)
        except Users.DoesNotExist:
            pass

    return {
        'webuser': webuser,
        'profile': profile
    }
