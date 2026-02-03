from django.contrib import admin
from .models import SubscriptionPlan, CustomerSubscription

admin.site.register(SubscriptionPlan)
admin.site.register(CustomerSubscription)
