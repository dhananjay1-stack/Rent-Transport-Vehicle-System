from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

# Custom user model
class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email

class Host(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='host_profile')
    name = models.CharField(max_length=100)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    pin_code = models.CharField(max_length=10)
    phone_number = models.CharField(max_length=15)

    def __str__(self):
        return self.user.email


class Customer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='customer_profile')
    name = models.CharField(max_length=100)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    pin_code = models.CharField(max_length=10)
    phone_number = models.CharField(max_length=15)

    def __str__(self):
        return self.user.email


class GoodsCarrier(models.Model):
    host = models.ForeignKey(Host, on_delete=models.CASCADE, related_name='carriers')
    name = models.CharField(max_length=100)
    carrier_number = models.CharField(max_length=50, unique=True)  # Ensure carrier numbers are unique
    owner_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    rate_per_hour = models.DecimalField(max_digits=10, decimal_places=2)
    photo = models.ImageField(upload_to='carriers/', null=True, blank=True)
    availability_status = models.BooleanField(default=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    
    location = models.CharField(max_length=255,null=True, blank=True)  # Current location of the carrier
    available = models.BooleanField(default=True)  # Is the carrier available?

    def __str__(self):
        return self.name


class Booking(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='bookings')
    goods_carrier = models.ForeignKey(GoodsCarrier, on_delete=models.CASCADE, related_name='bookings')
    pickup_location = models.CharField(max_length=255)
    dropoff_location = models.CharField(max_length=255, default='Unknown Location')
    date = models.DateField(default=timezone.now)
    time = models.TimeField()
    booking_date = models.DateTimeField(auto_now_add=True)
    total_hours = models.IntegerField(default='00')
    total_cost = models.DecimalField(max_digits=10, decimal_places=2,default='000')
    payment_status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Paid', 'Paid')], default='Pending')
    payment_method = models.CharField(max_length=10, choices=[('Cash', 'Cash'), ('Online', 'Online')], default='Cash')
    


    def __str__(self):
        return f"Booking by {self.customer.user.email} for {self.goods_carrier.name}"

class Feedback(models.Model):
    goods_carrier = models.ForeignKey('GoodsCarrier', on_delete=models.CASCADE)
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default="Null")
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comments = models.TextField(default="No comments")
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Feedback from {self.customer.username} for {self.goods_carrier.name}'

class Location(models.Model):
    goods_carrier = models.ForeignKey(GoodsCarrier, on_delete=models.CASCADE, related_name='locations')
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Location of {self.goods_carrier.name} at {self.timestamp}"


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Use settings.AUTH_USER_MODEL
    is_host = models.BooleanField(default=False)
    is_customer = models.BooleanField(default=True)

    def __str__(self):
        return self.user.username


