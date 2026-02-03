from django.shortcuts import render
from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404, redirect
from admin_panel.models import Language,Genre,Movie
from admin_panel.models import WebSeries , Season ,Episode
from .models import CustomerRegister
from django.http import JsonResponse
from django.contrib import messages
from .models import CustomerRegister,SubscriptionPlan, CustomerSubscription,Notification
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST
import razorpay
from django.conf import settings

def has_active_subscription(customer):
    return CustomerSubscription.objects.filter(
        customer=customer,
        is_active=True,
        end_date__gte=timezone.now()
    ).exists()



def customer_register_page(request):
    if request.method == "POST":
       
        fname = request.POST.get('customer_first_name')
        lname = request.POST.get('customer_last_name')
        u_email = request.POST.get('customer_email')
        u_username = request.POST.get('customer_username') 
        u_mobileno = request.POST.get('customer_mobileno')
        u_pwd = request.POST.get('customer_password')
        u_pic = request.FILES.get('customer_profile_pic')
        nickname = request.POST.get('nickname')
        school_name = request.POST.get('school_name')

        #  Save it to the Database
        new_customer = CustomerRegister(
            customer_first_name=fname,
            customer_last_name=lname,
            customer_email=u_email,
            customer_username=u_username, # SAVE THE USERNAME HERE
            customer_mobileno=u_mobileno,
            customer_password=u_pwd,
            customer_profile_pic=u_pic,
            nickname=nickname,
            school_name=school_name
        )
        try:
           new_customer.save()
        except IntegrityError:
          # Handle the error, e.g., redirect back with a message
         print("Email already exists!")

        # After saving, send them to the login page
        return redirect('/customer_panel/customer_login_page/')
    
    return render(request, 'customer_panel/Internship28-octOR.html')


def customer_login_page(request):
    if request.method == "POST":
        username_entered = request.POST.get('customer_entered_username')
        password_entered = request.POST.get('customer_entered_password')

        try:
            customer = CustomerRegister.objects.get(
                customer_username=username_entered,
                customer_password=password_entered
            )
            request.session['customer_id'] = customer.id
            return redirect('/customer_panel/customer_dashboard_page/')
        except CustomerRegister.DoesNotExist:
            return render(
                request,
                'customer_panel/Internship28-octOL.html',
                {'error': 'Invalid Credentials'}
            )

    return render(request, 'customer_panel/Internship28-octOL.html')



def forgot_password(request):
    if request.method == "POST":
        username = request.POST.get('username')
        nickname = request.POST.get('nickname')
        school = request.POST.get('school_name')

        try:
            customer = CustomerRegister.objects.get(
                customer_username=username.strip(),
                nickname=nickname.strip(),
                school_name=school.strip()
            )

            request.session['reset_customer_id'] = customer.id

            return render(
                request,
                'customer_panel/Internship28-octOL.html',
                {'open_reset_modal': True}
            )

        except CustomerRegister.DoesNotExist:
            return render(
                request,
                'customer_panel/Internship28-octOL.html',
                {
                    'forgot_error': 'Verification failed',
                    'open_forgot_modal': True
                }
            )

    return redirect('/customer_panel/customer_login_page/')

def reset_password(request):
    customer_id = request.session.get('reset_customer_id')
    if not customer_id:
        return redirect('/customer_panel/customer_login_page/')

    customer = CustomerRegister.objects.get(id=customer_id)

    if request.method == "POST":
        new_pw = request.POST.get('new_password')
        confirm_pw = request.POST.get('confirm_password')

        if new_pw != confirm_pw:
            messages.error(request, "Passwords do not match")
            return redirect('/customer_panel/customer_login_page/?reset=1')

        customer.customer_password = new_pw
        customer.save()

        # cleanup
        request.session.pop('reset_customer_id', None)

        messages.success(request, "Password updated successfully")
        return redirect('/customer_panel/customer_login_page/')

    return redirect('/customer_panel/customer_login_page/')



def customer_dashboard_page(request):

    customer_id = request.session.get('customer_id')
    customer = CustomerRegister.objects.get(id=customer_id)

    languages = Language.objects.all()

    # ✅ THIS LINE IS CRITICAL
    selected_lang = request.GET.get('language')

    movies = Movie.objects.all()
    web_series = WebSeries.objects.all()

    if selected_lang:
        movies = movies.filter(movie_language__id=selected_lang)
        web_series = web_series.filter(series_language__id=selected_lang)

    return render(request, 'customer_panel/Internship4-octOD.html', {
        'customer': customer,
        'languages': languages,
        'movies': movies,
        'web_series': web_series,
        'selected_lang': selected_lang
    })


def customer_update_profile(request):
    if request.method == "POST":

        customer_id = request.session.get('customer_id')
        customer = CustomerRegister.objects.get(id=customer_id)

        # Update text fields
        customer.customer_first_name = request.POST.get('customer_modal_first_name')
        customer.customer_last_name = request.POST.get('customer_modal_last_name')
        customer.customer_email = request.POST.get('customer_modal_email')
        
        # SAVE THE USERNAME HERE
        customer.customer_username = request.POST.get('customer_modal_username')

        # SAFELY UPDATE PROFILE PIC
        new_pic = request.FILES.get('customer_profile_pic')
        if new_pic: # Only updates if you actually chose a new file
            customer.customer_profile_pic = new_pic

        customer.save()
        return redirect('/customer_panel/customer_dashboard_page/')
    


def customer_movie_page(request):
    customer_id = request.session.get('customer_id')
    customer = CustomerRegister.objects.get(id=customer_id)

    movies = Movie.objects.all().order_by('-id')
    languages = Language.objects.all()
    genres = Genre.objects.all()

    subscription_status = has_active_subscription(customer)
    notifications = Notification.objects.all().order_by('-created_at')

    return render(request, 'customer_panel/Internship13-novOM.html', {
        'customer': customer,
        'movies': movies,
        'languages': languages,
        'genres': genres,
        'has_subscription': subscription_status,
        'notifications':notifications
    })


from django.shortcuts import render, get_object_or_404
from admin_panel.models import Movie
from customer_panel.models import CustomerSubscription
from django.utils import timezone

def customer_movie_detail(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)

    # check subscription
    has_subscription = False
    if request.session.get('customer_id'):
        has_subscription = CustomerSubscription.objects.filter(
            customer_id=request.session['customer_id'],
            is_active=True,
            end_date__gte=timezone.now()
        ).exists()

    return render(request, 'customer_movie_detail.html', {
        'movie': movie,
        'has_subscription': has_subscription
    })




# customer_panel/views.py

def customer_web_series_page(request):
    customer_id = request.session.get('customer_id')
    customer = CustomerRegister.objects.get(id=customer_id)
    
    # 1. Get filter IDs from the URL
    lang_id = request.GET.get('language')
    genre_id = request.GET.get('genre')

    # 2. Start with all web series
    series_list = WebSeries.objects.all().order_by('-created_at')

    # 3. Apply filters using the CORRECT field names from your error message
    if lang_id:
        # Changed 'language_id' to 'series_language_id'
        series_list = series_list.filter(series_language_id=lang_id)
        
    if genre_id:
        # Changed 'genre_id' to 'series_genre_id'
        series_list = series_list.filter(series_genre_id=genre_id)

    # 4. Fetch all records for the dropdowns
    languages = Language.objects.all()
    genres = Genre.objects.all()
    subscription_status = has_active_subscription(customer)
    notifications = Notification.objects.all().order_by('-created_at')

    

    return render(request, 'customer_panel/Internship6-decOW.html', {
        'all_series': series_list,
        'customer': customer,
        'languages': languages,
        'genres': genres,
        'selected_lang': lang_id,
        'selected_genre': genre_id,
        'has_subscription': subscription_status,
        'notifications':notifications

    })


# customer_panel/views.py

def get_episodes_for_edit(request):
    series_id = request.GET.get('series_id')
    season_id = request.GET.get('season_id')  # 1. Add this line to capture season_id
    
    # 2. Update filter to use BOTH series_id and season_id
    if season_id:
        episodes = Episode.objects.filter(series_id=series_id, season_id=season_id)
    else:
        episodes = Episode.objects.filter(series_id=series_id)
    
    episode_list = []
    for ep in episodes:
        episode_list.append({
            'title': ep.episode_title,
            'url': ep.video_url,
            'image': ep.episode_banner.url if ep.episode_banner else None,  # Add banner URL
            'season_name': ep.season.season_name if ep.season else "S1"
        })
    return JsonResponse({'episodes': episode_list})


def Customerchange_password(request):
    if request.method == "POST":
        customer_id = request.session.get('customer_id')
        if not customer_id:
            return redirect('/customer_panel/customer_login_page/')

        customer = CustomerRegister.objects.get(id=customer_id)

        current_pw = request.POST.get('current_password')
        new_pw = request.POST.get('new_password')
        confirm_pw = request.POST.get('confirm_password')

        if not current_pw or not new_pw or not confirm_pw:
            messages.error(request, "All fields are required.")
            return redirect('/customer_panel/customer_profile_settings_page/')

        if new_pw != confirm_pw:
            messages.error(request, "New passwords do not match!")
            return redirect('/customer_panel/customer_profile_settings_page/')

        if customer.customer_password != current_pw:
            messages.error(request, "Current password is incorrect.")
            return redirect('/customer_panel/customer_profile_settings_page/')

        # ✅ UPDATE PASSWORD
        customer.customer_password = new_pw
        customer.save()

        messages.success(request, "Password updated successfully!")

    return redirect('/customer_panel/customer_profile_settings_page/')

from django.shortcuts import render, get_object_or_404


def Video_player_view(request, movie_id):
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return redirect('/customer_panel/customer_login_page/')

    customer = CustomerRegister.objects.get(id=customer_id)

    if not has_active_subscription(customer):
        return redirect(
            f"/customer_panel/subscription_plans/?c_type=movie&c_id={movie_id}"
        )

    movie = get_object_or_404(Movie, id=movie_id)
    return render(request, 'customer_panel/internshio31-decVideoplayer.html', {
        'movie': movie,
        'customer': customer
    })



# customer_panel/views.py line 254
def web_series_player_view(request, series_id):

    customer_id = request.session.get('customer_id')
    if not customer_id:
        return redirect('/customer_panel/customer_login_page/')

    customer = CustomerRegister.objects.get(id=customer_id)

    has_active_subscription = CustomerSubscription.objects.filter(
        customer=customer,
        is_active=True,
        end_date__gte=timezone.now()
    ).exists()

    if not has_active_subscription:
        return redirect(
            f"/customer_panel/subscription_plans/?c_type=series&c_id={series_id}"
        )

    series = get_object_or_404(WebSeries, id=series_id)
    seasons = Season.objects.filter(series=series)

    return render(request, 'customer_panel/internship01-janweb_series_page.html', {
        'series': series,
        'seasons': seasons,
        'customer': customer
    })



def subscription_plans_page(request):
    customer_id = request.session.get('customer_id')
    customer = get_object_or_404(CustomerRegister, id=customer_id)
    
    c_type = request.GET.get('c_type', 'movie')
    c_id = request.GET.get('c_id', 0)
    
    # ✅ ORDER BY display_order (Option A)
    plans = SubscriptionPlan.objects.order_by('display_order')

    active_plan_id = None
    active_sub = CustomerSubscription.objects.filter(
        customer=customer,
        is_active=True
    ).first()
    
    if active_sub:
        active_plan_id = active_sub.plan.id
    
    return render(request, 'customer_panel/internship03-jansubscription.html', {
        'customer': customer,
        'plans': plans,
        'c_type': c_type,
        'c_id': c_id,
        'active_plan_id': active_plan_id
    })







# customer_panel/views.py

def process_subscription(request, plan_id, c_type, c_id):
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return redirect('customer_login')

    plan = get_object_or_404(SubscriptionPlan, id=plan_id)
    
    # Store c_type and c_id in session if you need them after payment callback
    request.session['pending_c_type'] = c_type
    request.session['pending_c_id'] = c_id

    # ... Your Razorpay / Payment Logic here ...
    
    context = {
        'plan': plan,
        'c_type': c_type,
        'c_id': c_id,
        # 'razorpay_order_id': order['id'], etc.
    }
    return render(request, 'customer_panel/process_subscription.html', context)



from .models import SubscriptionPlan # Ensure you have a SubscriptionPlan model

def subscription_page(request):
    plans = SubscriptionPlan.objects.order_by('display_order')
    c_type = request.GET.get('c_type')
    c_id = request.GET.get('c_id')
    return render(request, 'your_template_name.html', {'plans': plans, 'c_type': c_type, 'c_id': c_id})



def toggle_notifications(request):
    if request.method != "POST":
        return redirect('/customer_panel/customer_profile_settings_page/')
        
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return redirect('/customer_panel/customer_login_page/')
    
    # Retrieve the customer and toggle the boolean field defined in models.py
    customer = CustomerRegister.objects.get(id=customer_id)
    # Toggles between True and False
    customer.notifications_enabled = not customer.notifications_enabled 
    customer.save()
    
    # Optional: Add a success message to provide user feedback
    messages.success(request, f"Notifications {'enabled' if customer.notifications_enabled else 'disabled'}.")
    
    return redirect('/customer_panel/customer_profile_settings_page/')



@require_POST
def clear_notifications(request):
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return redirect('/customer_panel/customer_login_page/')
        
    # This will now work without NameError
    Notification.objects.all().delete() 
    
    referer = request.META.get('HTTP_REFERER', '/customer_panel/customer_dashboard_page/')
    return redirect(referer)




def customer_profile_settings_page(request):
    customer_id = request.session.get('customer_id')
    customer = CustomerRegister.objects.get(id=customer_id)

    notifications = Notification.objects.all().order_by('-created_at')
    
    return render(request, 'customer_panel/Internship5-decOP.html', {
        'customer': customer,  # Pass the customer object here
        'notifications': notifications
    })


# customer_panel/views.py
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

# Initialize Razorpay Client
razorpay_client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))

def process_subscription(request, plan_id, c_type, c_id):
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return redirect('customer_login')

    customer = get_object_or_404(CustomerRegister, id=customer_id)
    plan = get_object_or_404(SubscriptionPlan, id=plan_id)

    # Convert price to paise (e.g., 199.00 -> 19900)
    amount = int(plan.price * 100)

    # Create Razorpay order
    data = { "amount": amount, "currency": "INR", "receipt": f"rcpt_{customer_id}_{plan_id}" }
    razorpay_order = razorpay_client.order.create(data=data)

    # Store redirect info in session
    request.session['pending_plan_id'] = plan_id
    request.session['pending_c_type'] = c_type
    request.session['pending_c_id'] = c_id

    context = {
        'customer': customer,
        'razorpay_key_id': settings.RAZOR_KEY_ID,
        'razorpay_order_id': razorpay_order['id'],
        'amount': amount,
        'currency': 'INR',
        'plan_type': plan.plan_name, # Used in Payment_page.html
        'duration': plan.duration_days // 30, # Estimated months for description
        'customer_name': f"{customer.customer_first_name} {customer.customer_last_name}",
        'customer_email': customer.customer_email,
        'customer_phone': customer.customer_mobileno,
    }
    return render(request, 'customer_panel/Payment_page.html', context)

@csrf_exempt
def payment_callback(request):
    customer_id = request.session.get('customer_id')
    customer = get_object_or_404(CustomerRegister, id=customer_id)
    
    plan_id = request.session.get('pending_plan_id')
    c_type = request.session.get('pending_c_type')
    c_id = request.session.get('pending_c_id')
    
    plan = get_object_or_404(SubscriptionPlan, id=plan_id)

    # 1. Deactivate old subscriptions
    CustomerSubscription.objects.filter(customer=customer, is_active=True).update(is_active=False)
    
    # 2. Activate new subscription
    # The end_date is handled by your Model's save() method
    CustomerSubscription.objects.create(
        customer=customer,
        plan=plan,
        is_active=True
    )

    messages.success(request, f"Successfully subscribed to {plan.plan_name}!")

    # 3. Smart Redirect: Go back to the movie/series the user wanted to watch
    if c_type == 'movie' and str(c_id) != '0':
        return redirect('video_player_view', movie_id=c_id)
    elif c_type == 'series' and str(c_id) != '0':
        return redirect('web_series_player', series_id=c_id)
    
    return redirect('customer_dashboard')

def payment_failed(request):
    messages.error(request, "Payment failed or cancelled. Please try again.")
    return redirect('subscription_plans')


