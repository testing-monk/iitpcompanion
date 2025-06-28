from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from Webusers.models import Users, UserProfile
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
from contacts.models import ContactMessage ,Subscription
from datetime import date
from notifications.models import Notification
from django.views.decorators.csrf import csrf_exempt
from Maps.models import Map
from Orderfood.models import Canteen, MenuItem, Cart, OrderDetails
from Transportation.models import Bus, Train, BusSchedule
from functools import wraps
from Assignments.models import Assignment
from datetime import datetime, timedelta
import re

from django.utils import timezone
from datetime import timedelta

from django.contrib.auth.hashers import check_password, make_password



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
                from Webusers.models import UserProfile
                UserProfile.objects.get_or_create(user=user)
                return redirect('home')
            else:
                messages.error(request, "Invalid password")
        except Users.DoesNotExist:
            messages.error(request, "User not found")
    return render(request, 'user/login.html')


def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')

        if Users.objects.filter(email=email).exists():
            return render(request, 'user/sign-up.html', {'error': 'Email already exists.'})

        try:
            user = Users(username=username, email=email)
            user.set_password(password)
            user.save()
            UserProfile.objects.get_or_create(user=user)

            request.session['user_id'] = user.id

            return redirect('home')
        except ValidationError as ve:
            return render(request, 'user/sign-up.html', {'error': f'Validation error: {ve}'} )
        except Exception as e:
            return render(request, 'user/sign-up.html', {'error': f'An error occurred: {e}'} )
    return render(request, 'user/sign-up.html')
def logout(request):
    request.session.flush()
    return redirect('home')

def assignment(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    now = timezone.now()


    Assignment.objects.filter(due_end__lt=now - timedelta(days=2)).delete()

    assignments = Assignment.objects.all().order_by('due_start')

    processed_assignments = []
    for a in assignments:
        time_remaining = a.due_end - now
        days_remaining = time_remaining.days

        if days_remaining < 0:
            priority = 'overdue'
            status_text = 'Date Over'
        elif days_remaining <= 2:
            priority = 'high'
            status_text = f'Due in {days_remaining} day{"s" if days_remaining != 1 else ""}'
        elif days_remaining <= 4:
            priority = 'medium'
            status_text = f'Due in {days_remaining} days'
        else:
            priority = 'low'
            status_text = f'Due in {days_remaining} days'

        a.priority_status = priority
        a.status_text = status_text
        processed_assignments.append(a)

    context = {
        'assignments': processed_assignments,
        'total': len(assignments),
        'completed': assignments.filter(status='completed').count(),
        'pending': assignments.filter(status='pending').count(),
    }

    return render(request, 'Assignment.html', context)


@csrf_exempt
def toggle_assignment_status(request):
    if request.method == 'POST':
        assignment_id = request.POST.get('assignment_id')
        assignment = get_object_or_404(Assignment, id=assignment_id)


        if assignment.status == 'pending':
            assignment.status = 'completed'
        else:
            assignment.status = 'pending'

        assignment.save()

    return redirect('assignment')



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

    return render(request, 'user/admin_page.html', {
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
    user_id = request.session.get('user_id')

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




    context = {
        'cart': cart,
        'all_items': all_items,
        'total_price': total_price,
        'total_item': total_item,
        'canteen': canteen,
        'canteens': canteens,
    }

    return render(request, 'order.html', context)

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

@require_login
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
        return JsonResponse({'message': f'One more {food.name} added to your cart!'})
    else:
        Cart.objects.create(
            cart_user=user,
            item_title=food.name,
            item_price=food.price,
            item_slug=food.slug,
            item_quantity=1
        )
        return JsonResponse({'message': f'{food.name} added to your cart!'})

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




def tracker_view(request):
    now = datetime.now()


    bus_start_time = now - timedelta(minutes=30)
    bus_end_time = now + timedelta(hours=3)

    train_start_time = now - timedelta(hours=2)
    train_end_time = now + timedelta(hours=5)

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
        obj.type = obj_type
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

@require_login
def subscribe(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        user_id = request.session.get('user_id')
        name = get_object_or_404(Users, id=user_id)
        if name and email:
            if not Subscription.objects.filter(email=email).exists():
                Subscription.objects.create(name=name, email=email)
                messages.success(request, "Subscribed successfully!")
            else:
                messages.info(request, "This email is already subscribed.")

        return redirect(request.META.get('HTTP_REFERER', '/'))



@require_login
def profile_view(request):
    user_id = request.session.get('user_id')
    user = get_object_or_404(Users, id=user_id)
    profile, created = UserProfile.objects.get_or_create(user=user)

    cart = []
    total_price = 0
    total_item = 0
    all_items = []

    cart = Cart.objects.filter(cart_user=user)
    asgm = Assignment.objects.filter()
    assignments = [item.subject for item in asgm]

    all_items = [item.item_title for item in cart]
    if request.method == 'POST' and request.FILES.get('profile_image'):
        profile.profile_image = request.FILES['profile_image']
        profile.save()
        return redirect('profile')



    # joined_clubs = Club.objects.filter(president=user)
    # registered_events = Event.objects.filter(participants=user)

    return render(request, 'user/profile.html', {
        'user': user,
        'profile': profile,
        'cart' : cart,
        'all_items' : all_items,
        'assignments': assignments
        # 'clubs': joined_clubs,
        # 'events': registered_events,
    })

@require_login
def edit_profile(request):
    user_id = request.session.get('user_id')
    user = get_object_or_404(Users, id=user_id)
    profile, created = UserProfile.objects.get_or_create(user=user)

    if request.method == "POST":
        user.username = request.POST.get("username", user.username)
        profile.roll_number = request.POST.get("roll_number", profile.roll_number)
        profile.department = request.POST.get("department", profile.department)
        profile.year = request.POST.get("year", profile.year)
        profile.mobile_number = request.POST.get("mobile_number", profile.mobile_number)

        if request.FILES.get("profile_image"):
            profile.profile_image = request.FILES["user/profile_image"]

        user.save()
        profile.save()
        # messages.success(request, "Profile updated successfully.")
        return redirect('profile')

    return render(request, 'user/edit_profile.html', {'user': user, 'profile': profile})

@require_login
def leave_club(request, club_id):
    user_id = request.session.get('user_id')
    user = get_object_or_404(Users, id=user_id)
    club = get_object_or_404(Club, id=club_id)
    if club.president == user:  # change if member logic is added
        messages.error(request, "You cannot leave your own club.")
    else:
        club.members.remove(user)  # only if a many-to-many relationship exists
    return redirect('profile')


@require_login
def register_event(request, event_id):
    user_id = request.session.get('user_id')
    user = get_object_or_404(Users, id=user_id)
    event = get_object_or_404(Event, id=event_id)
    event.participants.add(user)
    return redirect('profile')

def errorpage(request,path):
    return render(request,'404_error.html')
def errorpage2(request,path,err):
    path=None
    err=None
    return render(request,'404_error.html')
def errorpage3(request,path,err,errr):
    path=None
    err=None
    return render(request,'404_error.html')


@require_login
def confirm_order(request):
    if request.method == "POST":
        user_id = request.session.get("user_id")
        user = get_object_or_404(Users, id=user_id)

        order_type = request.POST.get("order_type")
        address = request.POST.get("address")
        mobile_number = request.POST.get("mobile")
        items = request.POST.get("food_title")
        total_price = request.POST.get("price")
        quantity = request.POST.get("quantity")
        payment_type = request.POST.get("payment")


        if not all([order_type, address, mobile_number, items, total_price, quantity, payment_type]):
            return redirect("order")

        OrderDetails.objects.create(
            user=user,
            mobile_number=mobile_number,
            items=items,
            total_price=total_price,
            quantity=quantity,
            address=address,
            order_type=order_type,
            payment_type=payment_type,
            order_status="Pending"
        )

        cart = Cart.objects.filter(cart_user=user)
        slugs = [item.item_slug for item in cart]
        menu_items_qs = MenuItem.objects.filter(slug__in=slugs)
        menu_items = {item.slug: item for item in menu_items_qs}


        total_price_cart = sum(item.item_price * item.item_quantity for item in cart)

        latest_order = OrderDetails.objects.filter(user=user).order_by('-ordered_at').first()
        order_date = latest_order.ordered_at.strftime("%B %d, %Y at %I:%M %p") if latest_order else None
        order_number = latest_order.order_number if latest_order else "N/A"


        def parse_minutes(time_str):
            match = re.search(r'(\d+)', time_str)
            return int(match.group(1)) if match else 0

        delivery_times = [
            parse_minutes(menu_items[item.item_slug].delivery_time)
            for item in cart if item.item_slug in menu_items
        ]
        average_minutes = sum(delivery_times) // len(delivery_times) if delivery_times else 0
        average_delivery = f"{average_minutes} min" if average_minutes else "N/A"

        return render(request, 'confirm_order.html', {
            'user': user,
            'cart': cart,
            'menu_items': menu_items,
            'total_price': total_price_cart,
            'order_date': order_date,
            'order_number': order_number,
            'average_delivery': average_delivery
        })

    return redirect("order")

@require_login
def track_order(request):
    user_id = request.session.get("user_id")
    user = get_object_or_404(Users, id=user_id)

    cart = Cart.objects.filter(cart_user=user)
    slugs = [item.item_slug for item in cart]
    menu_items_qs = MenuItem.objects.filter(slug__in=slugs)
    menu_items = {item.slug: item for item in menu_items_qs}

    total_price_cart = sum(item.item_price * item.item_quantity for item in cart)

    latest_order = OrderDetails.objects.filter(user=user).order_by('-ordered_at').first()

    order_date = latest_order.ordered_at.strftime("%B %d, %Y at %I:%M %p") if latest_order else None
    order_number = latest_order.order_number if latest_order else "N/A"
    order_status = latest_order.order_status if latest_order else "Pending"

    def parse_minutes(time_str):
        match = re.search(r'(\d+)', time_str)
        return int(match.group(1)) if match else 0

    delivery_times = [
        parse_minutes(menu_items[item.item_slug].delivery_time)
        for item in cart if item.item_slug in menu_items
    ]
    average_minutes = sum(delivery_times) // len(delivery_times) if delivery_times else 0
    average_delivery = f"{average_minutes} min" if average_minutes else "N/A"

    context = {
        'user': user,
        'cart': cart,
        'menu_items': menu_items,
        'total_price': total_price_cart,
        'order_date': order_date,
        'order_number': order_number,
        'average_delivery': average_delivery,
        'order_status': order_status,
    }

    return render(request, 'user/trackorder.html', context)

def restaurant(request):
    return render(request, 'Restaurant/order_admin.html')

@require_login
def change_password(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "You must be logged in to change your password.")
        return redirect('login')

    user = get_object_or_404(Users, id=user_id)

    if request.method == 'POST':
        current_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password1')
        confirm_password = request.POST.get('new_password2')


        if not check_password(current_password, user.password):
            messages.error(request, "❌ Current password is incorrect.")
            return redirect('change_password')


        if new_password != confirm_password:
            messages.error(request, "❌ New passwords do not match.")
            return redirect('change_password')


        user.password = make_password(new_password)
        user.save()
        messages.success(request, "✅ Password updated successfully.")
        return redirect('profile')

    return render(request, 'user/change_password.html')