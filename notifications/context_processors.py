from Webusers.models import Users
from notifications.models import Notification


def notification_context(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return {'notifications': []}

    try:
        user = Users.objects.get(id=user_id)
        notes = Notification.objects.filter(user=user).order_by('-created_at')[:5]
        return {'notifications': notes, 'webuser': user}
    except Users.DoesNotExist:
        return {'notifications': []}
