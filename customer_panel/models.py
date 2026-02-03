from django.db import models
from datetime import timedelta
from django.utils import timezone


# Create your models here.

class CustomerRegister(models.Model):
    customer_first_name = models.CharField(max_length=100)
    customer_last_name = models.CharField(max_length=100)
    customer_email = models.EmailField(unique=True)
    customer_mobileno = models.CharField(max_length=15)
    customer_password = models.CharField(max_length=128) # Use hashing in production
    customer_profile_pic = models.ImageField(upload_to='customer_profiles/', null=True, blank=True)
    customer_username = models.CharField(max_length=100, null=True, blank=True)
    nickname = models.CharField(max_length=100, default="unknown")
    school_name = models.CharField(max_length=150, default="unknown")
 

from django.db import models
from django.utils import timezone
from datetime import timedelta



# ... (Keep CustomerRegister as is) ...

class SubscriptionPlan(models.Model):
    plan_name = models.CharField(max_length=50) 
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_days = models.IntegerField() 
    description = models.TextField(null=True, blank=True)
    display_order = models.IntegerField(default=0)

    def __str__(self):
        return self.plan_name

#......Customer subscription model

class CustomerSubscription(models.Model):
    customer = models.ForeignKey(CustomerRegister, on_delete=models.CASCADE)
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        # Calculate end_date automatically when creating a subscription
        if not self.id:
            self.end_date = timezone.now() + timedelta(days=self.plan.duration_days)
        super().save(*args, **kwargs)
    

class WatchHistory(models.Model):
    user = models.ForeignKey(CustomerRegister, on_delete=models.CASCADE)
    content_type = models.CharField(max_length=20)  # movie / webseries
    content_id = models.IntegerField()
    content_title = models.CharField(max_length=255)
    watched_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.content_title}"
    


class Notification(models.Model):
    # Added null and blank so Django doesn't ask for a default in the terminal
    customer = models.ForeignKey(CustomerRegister, on_delete=models.CASCADE, null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.customer.customer_first_name if self.customer else 'System'}"