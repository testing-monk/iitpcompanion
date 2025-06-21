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
from Orderfood.models import Canteen, MenuItem, Cart
from Transportation.models import Bus, Train, BusSchedule
from functools import wraps
from django.views.decorators.http import require_POST
from collections import defaultdict

from datetime import datetime, timedelta





def require_login(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        user_id = request.session.get('user_id')
        if not user_id:
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

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

def assignment(request):
    return render(request, 'Assignment.html')


def search(request):
    return render(request, 'search.html')

def progress(request):
    return render(request, 'page_in_progress.html')

def test(request):
    return render(request, 'test.html')

@require_login
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

@require_login
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

@require_login
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


@require_login
def admin_dashboard(request):
    from Webusers.models import Users
    from notifications.models import Notification

    user = Users.objects.get(id=request.session['user_id'])  # fetch actual instance
    notifications = Notification.objects.filter(user=user).order_by('-created_at')

    return render(request, 'admin_page.html', {
        'webuser': user,
        'notifications': notifications,
    })

@require_login
def mark_notifications_read(request):
    user_id = request.session.get('user_id')
    if user_id:
        user = Users.objects.get(id=user_id)
        Notification.objects.filter(user=user, is_read=False).update(is_read=True)
    return redirect('home')

@require_login
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


def canteen(request):
    canteens = Canteen.objects.all()
    return render(request, 'order.html', {'canteens': canteens})

def menu_page(request, slug):
    user_id = request.session.get('user_id')
    canteen = get_object_or_404(Canteen, slug=slug)
    items = MenuItem.objects.filter(canteen=canteen)

    cart = []
    total_price = 0
    total_item = 0
    all_items = []

    if user_id:
        try:
            user = Users.objects.get(id=user_id)
            cart = Cart.objects.filter(cart_user=user)

            total_price = sum(item.item_price * item.item_quantity for item in cart)
            total_item = sum(item.item_quantity for item in cart)
            all_items = [item.item_title for item in cart]

        except Users.DoesNotExist:
            user = None
        except Exception as e:
            print(f"Cart fetch error: {e}")


    categorized_items = {}
    for item in items:
        category = item.category or "Others"
        categorized_items.setdefault(category, []).append(item)

    context = {
        'cart': cart,
        'all_items': all_items,
        'total_price': total_price,
        'total_item': total_item,
        'canteen': canteen,
        'categorized_items': categorized_items
    }

    return render(request, 'menu.html', context)

def addtocart(request, slug, item_id):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    user = get_object_or_404(Users, id=user_id)
    food = get_object_or_404(MenuItem, id=item_id)

    cart_item = Cart.objects.filter(cart_user=user, item_slug=food.slug).first()

    if cart_item:
        cart_item.item_quantity += 1
        cart_item.save()
        return JsonResponse({'message': f'One more {food.name} added to your plate!'})
    else:
        Cart.objects.create(
            cart_user=user,
            item_title=food.name,
            item_price=food.price,
            item_slug=food.slug,
            item_quantity=1
        )
        return JsonResponse({'message': f'{food.name} added to your plate!'})

@require_login
def remove_from_cart(request, slug, item_id):
    user_id = request.session.get('user_id')
    if not user_id:
        return JsonResponse({'error': 'User not logged in'}, status=403)

    user = get_object_or_404(Users, id=user_id)
    cart_item = get_object_or_404(Cart, id=item_id, cart_user=user)

    cart_item.delete()
    return JsonResponse({'message': f"{cart_item.item_title} removed from your plate."})

def about_us(request):
    return render(request,'about_us.html')

def restaurant(request):
    return render(request,'restaurant_dashboard.html')



def tracker_view(request):
    now = datetime.now()

    # Time windows
    bus_start_time = now - timedelta(minutes=10)
    bus_end_time = now + timedelta(hours=2)

    train_start_time = now - timedelta(hours=2)
    train_end_time = now + timedelta(hours=24)

    # Filter Buses
    buses = []
    for bus in Bus.objects.all():
        try:
            dep_time = datetime.strptime(bus.departure_time, "%H:%M")
            bus_time_today = now.replace(hour=dep_time.hour, minute=dep_time.minute, second=0, microsecond=0)
            if bus_start_time <= bus_time_today <= bus_end_time:
                buses.append(bus)
        except Exception as e:
            print(f"❌ Skipping bus '{bus.name}' due to error: {e}")
            continue

    # Filter Trains
    trains = []
    for train in Train.objects.all():
        try:
            dep_time = datetime.strptime(train.departure_time, "%H:%M")
            train_time_today = now.replace(hour=dep_time.hour, minute=dep_time.minute, second=0, microsecond=0)
            if train_start_time <= train_time_today <= train_end_time:
                trains.append(train)
        except Exception as e:
            print(f"❌ Skipping train '{train.name}' due to error: {e}")
            continue

    schedules = BusSchedule.objects.all()

    context = {
        'buses': buses,
        'trains': trains,
        'schedules': schedules,
    }
    return render(request, 'tracker.html', context)



def search_view(request):
    query = request.GET.get('q', '')
    transport_type = request.GET.get('type', '')
    status = request.GET.get('status', '')
    from_location = request.GET.get('from_location', '')
    to_location = request.GET.get('to_location', '')
    departure_in = request.GET.get('departure_in', '')  # in minutes

    results = []

    def matches_filters(obj, obj_type):
        if query and query.lower() not in obj.name.lower():
            return False
        if status and obj.status != status:
            return False
        if from_location and (not obj.from_location or from_location.lower() not in obj.from_location.lower()):
            return False
        if to_location and (not obj.to_location or to_location.lower() not in obj.to_location.lower()):
            return False
        if departure_in:
            try:
                dep_time = datetime.strptime(obj.departure_time, "%H:%M")
                now = datetime.now().replace(second=0, microsecond=0)
                dep_datetime = now.replace(hour=dep_time.hour, minute=dep_time.minute)
                if dep_datetime < now or (dep_datetime - now).total_seconds() / 60 > int(departure_in):
                    return False
            except:
                return False
        obj.type = obj_type  # add type info
        return True

    if transport_type in ['', 'Bus']:
        for bus in Bus.objects.all():
            if matches_filters(bus, 'Bus'):
                results.append(bus)

    if transport_type in ['', 'Train']:
        for train in Train.objects.all():
            if matches_filters(train, 'Train'):
                results.append(train)

    return render(request, 'search.html', {'results': results})

