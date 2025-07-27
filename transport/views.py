from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, UpdateView, DeleteView, ListView
from django.http import JsonResponse, HttpResponse
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Host, Customer, GoodsCarrier, Booking, Feedback, Profile, Location
from .forms import BookingForm, FeedbackForm
from django.shortcuts import render, get_object_or_404
from .models import GoodsCarrier
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
import qrcode
from django.http import HttpResponse
from io import BytesIO
from django.urls import reverse

User = get_user_model()


def home_view(request):
    return render(request, 'home.html')

def about_us(request):
    return render(request, 'about_us.html')

def register(request):
    if request.method == 'POST':
        role = request.POST.get('role')
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        country = request.POST.get('country')
        pin_code = request.POST.get('pin_code')
        phone_number = request.POST.get('phone_number')

        
        user = User.objects.create_user(email=email, password=password, first_name=name)

    
        if role == 'host':
            Host.objects.create(user=user, name=name, address=address, city=city, state=state, country=country, pin_code=pin_code, phone_number=phone_number)
        elif role == 'customer':
            Customer.objects.create(user=user, name=name, address=address, city=city, state=state, country=country, pin_code=pin_code, phone_number=phone_number)

        messages.success(request, 'Account created successfully!')
        return redirect('login')

    return render(request, 'register.html')


def LoginView(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)

            
            profile = Profile.objects.get(user=user)

            if profile.is_host:
                return redirect('host_dashboard')  
            elif profile.is_customer:
                return redirect('customer_dashboard')  
        else:
            
            return render(request, 'registration/login.html', {'error': 'Invalid username or password'})
    
    return render(request, 'registration/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def host_dashboard(request):
    
    if not hasattr(request.user, 'host_profile'):
        return redirect('customer_dashboard')

    
    host_profile = request.user.host_profile
    
    
    goods_carriers = GoodsCarrier.objects.filter(host=host_profile)
    bookings = Booking.objects.filter(goods_carrier__host=host_profile).values()
    feedbacks = Feedback.objects.filter(goods_carrier__host=host_profile)

    
    context = {
        'user': request.user,
        'goods_carriers': goods_carriers,  
        'bookings': bookings,
        'feedbacks': feedbacks,
    }
    
    return render(request, 'host_dashboard.html', context)

@login_required
def host_dashboard(request):
    
    if not hasattr(request.user, 'host_profile'):
        return redirect('customer_dashboard')

    
    host_profile = request.user.host_profile
    
    goods_carriers = GoodsCarrier.objects.filter(host=host_profile)
    bookings = Booking.objects.filter(goods_carrier__host=host_profile).values()
    feedbacks = Feedback.objects.filter(goods_carrier__host=host_profile)

    context = {
        'user': request.user,
        'host_profile': host_profile,  #
        'goods_carriers': goods_carriers,  
        'bookings': bookings,
        'feedbacks': feedbacks,  
    }
    
    return render(request, 'host_dashboard.html', context)


@login_required
def customer_dashboard(request):
    user = request.user

    
    try:
        customer = user.customer_profile  
    except Customer.DoesNotExist:
        
        return HttpResponse("Customer profile not found.", status=404)

    
    bookings = Booking.objects.filter(customer=customer)

    
    goods_carriers = GoodsCarrier.objects.filter(available=True)

    
    if request.method == 'POST':
        carrier_id = request.POST.get('carrier_id')
        total_hours = int(request.POST.get('total_hours'))
        pickup_location = request.POST.get('pickup_location')
        dropoff_location = request.POST.get('dropoff_location', 'Unknown Location')
        payment_method = request.POST.get('payment_method')

        carrier = get_object_or_404(GoodsCarrier, id=carrier_id)
        total_cost = carrier.rate_per_hour * total_hours

        
        booking = Booking.objects.create(
            customer=customer,
            goods_carrier=carrier,
            pickup_location=pickup_location,
            dropoff_location=dropoff_location,
            total_hours=total_hours,
            total_cost=total_cost,
            payment_method=payment_method,
            payment_status='Pending' if payment_method == 'Cash' else 'Paid'
        )

        
        if payment_method == 'Online':
           return redirect(reverse('upi_payment', args=[booking.id]))
        else:
    
            return redirect(reverse('complete_booking', args=[carrier.id]))  


    context = {
        'user': user,
        'bookings': bookings,
        'goods_carriers': goods_carriers,
    }

    return render(request, 'customer_dashboard.html', context)




@login_required
def create_goods_carrier(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        carrier_number = request.POST.get('carrier_number')
        owner_name = request.POST.get('owner_name')
        phone_number = request.POST.get('phone_number')
        rate_per_hour = request.POST.get('rate_per_hour')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        
        # Handling the uploaded photo file
        photo = request.FILES.get('photo')  
        
        location = request.POST.get('location')  

        if hasattr(request.user, 'host_profile'):
            host = request.user.host_profile  

            
            GoodsCarrier.objects.create(
                name=name,
                carrier_number=carrier_number,
                owner_name=owner_name,
                phone_number=phone_number,
                rate_per_hour=rate_per_hour,
                latitude=latitude,
                longitude=longitude,
                photo=photo,  
                location=location,  
                host=host
            )

            messages.success(request, 'Goods Carrier created successfully!')
            return redirect('host_dashboard')
        else:
            messages.error(request, 'You are not authorized to create a goods carrier.')
            return redirect('some_error_page')  # Redirect to an appropriate error page

    return render(request, 'create_goods_carrier.html')

@login_required
def update_goods_carrier(request, carrier_id):
    goods_carrier = get_object_or_404(GoodsCarrier, id=carrier_id)
    if request.method == 'POST':
        goods_carrier.name = request.POST.get('name')
        goods_carrier.carrier_number = request.POST.get('carrier_number')
        goods_carrier.owner_name = request.POST.get('owner_name')
        goods_carrier.phone_number = request.POST.get('phone_number')
        goods_carrier.rate_per_hour = request.POST.get('rate_per_hour')
        goods_carrier.latitude = request.POST.get('latitude')
        goods_carrier.longitude = request.POST.get('longitude')
        goods_carrier.save()

        messages.success(request, 'Goods Carrier updated successfully!')
        return redirect('host_dashboard')

    return render(request, 'update_goods_carrier.html', {'goods_carrier': goods_carrier})

@login_required
def delete_goods_carrier(request, carrier_id):
    goods_carrier = get_object_or_404(GoodsCarrier, id=carrier_id)
    if request.method == 'POST':
        goods_carrier.delete()
        messages.success(request, 'Goods Carrier deleted successfully!')
        return redirect('host_dashboard')
    
    return render(request, 'delete_goods_carrier.html', {'goods_carrier': goods_carrier})

# Booking Views
@login_required
def available_carriers(request):
    goods_carriers = GoodsCarrier.objects.all()  
    return render(request, 'available_carriers.html', {'goods_carriers': goods_carriers})

@login_required
def book_carrier(request, carrier_id):
    carrier = get_object_or_404(GoodsCarrier, pk=carrier_id)
    
    
    try:
        customer = request.user.customer_profile  
    except Customer.DoesNotExist:
        return HttpResponse("Customer profile not found.", status=404)
    
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            
            booking.customer = customer
            booking.goods_carrier = carrier
            booking.save()
            
            carrier.available = False
            carrier.save()
            return redirect('booking_success')
    else:
        form = BookingForm()

    return render(request, 'book_carrier.html', {'form': form, 'carrier': carrier})

@login_required
def booking_success(request):
    return render(request, 'booking_success.html')

# Feedback Views
@login_required
def leave_feedback(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.booking = booking
            feedback.customer = request.user
            feedback.save()
            messages.success(request, 'Thank you for your feedback!')
            return redirect('customer_dashboard')
    else:
        form = FeedbackForm()

    return render(request, 'feedback.html', {'form': form, 'booking': booking})

@login_required
def view_feedbacks(request, carrier_id):
    goods_carrier = get_object_or_404(GoodsCarrier, id=carrier_id)
    feedbacks = Feedback.objects.filter(goods_carrier=goods_carrier)
    return render(request, 'view_feedbacks.html', {'feedbacks': feedbacks, 'goods_carrier': goods_carrier})

@login_required
def update_location(request, carrier_id):
    goods_carrier = get_object_or_404(GoodsCarrier, id=carrier_id)
    latitude = request.POST.get('latitude')
    longitude = request.POST.get('longitude')

    if latitude and longitude:
        Location.objects.create(goods_carrier=goods_carrier, latitude=latitude, longitude=longitude)
        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'failed', 'reason': 'Missing latitude or longitude'})

from django.http import JsonResponse

@login_required
def track_carrier(request, carrier_id):
    goods_carrier = get_object_or_404(GoodsCarrier, id=carrier_id)

    
    if request.user != goods_carrier.host.user:
        return HttpResponseForbidden("You do not have permission to track this carrier's location.")

    
    latest_location = goods_carrier.locations.latest('timestamp')

    
    return JsonResponse({
        'latitude': float(latest_location.latitude),
        'longitude': float(latest_location.longitude)
    })


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()


@login_required
def feedback_page(request):
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comments = request.POST.get('comments')
        carrier_id = request.POST.get('carrier')  
        customer = request.user

        
        goods_carrier = get_object_or_404(GoodsCarrier, id=carrier_id)

        
        Feedback.objects.create(
            goods_carrier=goods_carrier,
            customer=customer,
            rating=rating,
            comments=comments
        )

        messages.success(request, 'Thank you for your feedback!')

        
        if hasattr(customer, 'host_profile'):  
            return redirect('host_dashboard')
        else:
            return redirect('customer_dashboard')

    
    carriers = GoodsCarrier.objects.filter(available=True)  
    return render(request, 'feedback.html', {'carriers': carriers})



def carrier_location_update(request, carrier_id):
    goods_carrier = get_object_or_404(GoodsCarrier, id=carrier_id)

    
    if request.user != goods_carrier.host.user:
        return HttpResponseForbidden("You do not have permission to update this carrier's location.")

    context = {
        'goods_carrier': goods_carrier,
    }
    return render(request, 'carrier_location_update.html', context)

def about_us(request):
    return render(request, 'about_us.html')





def complete_booking(request, carrier_id):
    carrier = get_object_or_404(GoodsCarrier, id=carrier_id)

    if request.method == 'POST':
        
        total_hours = int(request.POST.get('total_hours'))
        time = request.POST.get('time')  
        
        
        total_cost = carrier.rate_per_hour * total_hours
        
        
        booking = Booking.objects.create(
            customer=request.user.customer_profile,
            goods_carrier=carrier,
            pickup_location=request.POST.get('pickup_location'),
            dropoff_location=request.POST.get('dropoff_location', 'Unknown Location'),
            total_hours=total_hours,
            total_cost=total_cost,
            time=time,  
            payment_method=request.POST.get('payment_method'),
            payment_status='Pending' if request.POST.get('payment_method') == 'Cash' else 'Paid'
        )

        
        if booking.payment_method == 'Online':
            upi_id = "9699457193@ibl" 
            payee_name = "Goods Transportation System"
            transaction_note = f"Payment for booking {booking.id}"
            amount = booking.total_cost

            
            upi_payment_url = f"upi://pay?pa={upi_id}&pn={payee_name}&am={amount}&cu=INR&tn={transaction_note}"

            
            request.session['upi_payment_url'] = upi_payment_url

        
            return render(request, 'upi_payment.html', {
                'upi_url': upi_payment_url,
                'booking': booking
            })

        
        return redirect('booking_confirmation', booking_id=booking.id)

    return render(request, 'booking_form.html', {'carrier': carrier})



def generate_upi_qr(request):
    
    upi_url = request.session.get('upi_payment_url')

    if not upi_url:
        return HttpResponse("UPI URL not found", status=404)

    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(upi_url)
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='white')

    
    response = HttpResponse(content_type="image/png")
    img.save(response, "PNG")
    return response


def confirm_upi_payment(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    
    booking.payment_status = 'Paid'
    booking.save()

    
    if 'upi_payment_url' in request.session:
        del request.session['upi_payment_url']

    return redirect('booking_confirmation', booking_id=booking.id)


def booking_confirmation(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    return render(request, 'booking_confirmation.html', {'booking': booking})
