from django.contrib import admin

from sms.models import SMS, Client, SMSDelivery

# Register your models here.
admin.site.register(Client)
admin.site.register(SMS)
admin.site.register(SMSDelivery)

