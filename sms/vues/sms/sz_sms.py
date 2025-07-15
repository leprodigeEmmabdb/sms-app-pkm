# appbroadcastSMS/vues/SMS/sz_SMS.py

import re
from rest_framework import serializers
from sms.models import SMS



class SimpleSMSSerializer(serializers.ModelSerializer):
    class Meta:
        model = SMS
        fields = ["id", "contenu"]

class SMSSerializer(serializers.ModelSerializer):
    class Meta:
        model = SMS
        fields = '__all__'

class AddSMSSerializer(serializers.ModelSerializer):
    class Meta:
        model = SMS
        exclude = ['is_active']

class UpdateSMSSerializer(serializers.ModelSerializer):
    class Meta:
        model = SMS
        fields = ['id', 'contenu', 'is_active']


