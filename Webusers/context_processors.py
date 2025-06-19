from Webusers.models import Users

def users_context(request):
    user_id = request.session.get('user_id')
    webuser = None
    if user_id:
        try:
            webuser = Users.objects.get(id=user_id)
        except Users.DoesNotExist:
            pass
    return {'webuser': webuser}
