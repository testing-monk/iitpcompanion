from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from Webusers.models import Users
from django.core.exceptions import ValidationError
from Clubs.models import Club
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from Event_calendar.models import Event
import json
from datetime import datetime
from django.shortcuts import render
from django.core.mail import send_mail
from django.conf import settings
from contacts.models import ContactMessage
from datetime import date
from notifications.models import Notification
from django.views.decorators.csrf import csrf_exempt
from Maps.models import Map

def home(request):
    return render(request, 'index.html')

def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        try:
            user = Users.objects.get(email=email)
            if user.check_password(password):
                request.session['user_id'] = user.id
                return redirect('home')
            else:
                messages.error(request, "Invalid password")
        except Users.DoesNotExist:
            messages.error(request, "User not found")
    return render(request, 'login.html')

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')

        if Users.objects.filter(email=email).exists():
            return render(request, 'sign-up.html', {'error': 'Email already exists.'})

        try:
            user = Users(username=username, email=email)
            user.set_password(password)
            user.save()
            return redirect('login')
        except ValidationError as ve:
            return render(request, 'sign-up.html', {'error': f'Validation error: {ve}'})
        except Exception as e:
            return render(request, 'sign-up.html', {'error': f'An error occurred: {e}'})
    return render(request, 'sign-up.html')

def logout(request):
    request.session.flush()
    return redirect('home')

def Assignment(request):
    return render(request, 'Assigment.html')

def order(request):
    return render(request, 'order.html')

def search(request):
    return render(request, 'search.html')

def tracker(request):
    return render(request, 'tracker.html')


def progress(request):
    return render(request, 'page_in_progress.html')

def test(request):
    return render(request, 'test.html')

def feedback(request):
    return render(request, 'feedback.html')

def maps(request):
    maps = Map.objects.all()
    return render(request, 'maps.html',{'maps': maps})

def events(request):
    return render(request, 'event_calendar.html')

def student_clubs(request):
    clubs = Club.objects.all()
    return render(request, 'student_clubs.html', {'clubs': clubs})

def club_detail(request, slug):
    club = get_object_or_404(Club, slug=slug)
    return render(request, 'club-detail.html', {'club': club})


@csrf_exempt  # Only if CSRF token is an issue in testing (not recommended in production)
def save_event(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            date_str = data.get('date')
            title = data.get('title')
            event_date = datetime.strptime(date_str, '%Y-%m-%d').date()

            user_id = request.session.get('user_id')
            if not user_id:
                return JsonResponse({'status': 'error', 'message': 'User not authenticated'}, status=403)

            from Webusers.models import Users  # ensure you import Users if not already
            user = Users.objects.get(id=user_id)

            from Event_calendar.models import Event
            from notifications.models import Notification

            Event.objects.create(
                user=user,
                title=title,
                date=event_date,
                event_type='user'
            )

            Notification.objects.create(
                user=user,
                message="Your event was successfully added!"
            )

            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)



def get_events(request):
    user_id = request.session.get('user_id')

    if not user_id:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    try:
        user = Users.objects.get(id=user_id)
    except Users.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)

    # Get user events and admin/global events if needed
    events = Event.objects.filter(user=user) | Event.objects.filter(event_type='admin')
    events = events.distinct()

    events_data = [
        {
            'title': e.title,
            'date': e.date.strftime('%Y-%m-%d'),
            'event_type': e.event_type,
            'owner': e.user.username if e.user else 'admin'
        }
        for e in events
    ]

    return JsonResponse(events_data, safe=False)


def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        print(name,email,subject,message)

        ContactMessage.objects.create(
            name=name,
            email=email,
            subject=subject,
            message=message
        )
        messages.success(request, 'Your message has been sent successfully!')
        return redirect('contact')
    messages.success(request, 'something went wrong')
    return render(request, 'contacts.html')


@login_required
def admin_dashboard(request):
    from Webusers.models import Users
    from notifications.models import Notification

    user = Users.objects.get(id=request.session['user_id'])  # fetch actual instance
    notifications = Notification.objects.filter(user=user).order_by('-created_at')

    return render(request, 'admin_page.html', {
        'webuser': user,
        'notifications': notifications,
    })

def mark_notifications_read(request):
    user_id = request.session.get('user_id')
    if user_id:
        user = Users.objects.get(id=user_id)
        Notification.objects.filter(user=user, is_read=False).update(is_read=True)
    return redirect('home')

@csrf_exempt
def delete_event(request, event_id):
    if request.method == "DELETE":
        user_id = request.session.get("user_id")
        try:
            from Event_calendar.models import Event
            from Webusers.models import Users
            user = Users.objects.get(id=user_id)
            event = Event.objects.get(id=event_id, user=user)
            event.delete()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

