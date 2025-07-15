# appbroadcastSMSDelivery/vues/SMSDelivery/sz_SMSDelivery.py

import re
from rest_framework import serializers
from sms.models import SMSDelivery
from sms.vues.client.sz_client import SimpleClientSerializer
from sms.vues.sms.sz_sms import SimpleSMSSerializer

class SimpleSMSDeliverySerializer(serializers.ModelSerializer):
    sms=SimpleSMSSerializer()
    client=SimpleClientSerializer()
    class Meta:
        model = SMSDelivery
        fields = ["id", "sms", "client", "statut"]



class SimpleSMSDeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = SMSDelivery
        fields = ["id", "message"]

class SMSDeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = SMSDelivery
        fields = '__all__'

class AddSMSDeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = SMSDelivery
        exclude = ['is_active']

class UpdateSMSDeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = SMSDelivery
        fields = ['id', 'message', 'is_active']

# Serializer pour un seul destinataire
class SendSingleSMSDeliverySerializer(serializers.Serializer):
    numero = serializers.CharField()
    message = serializers.CharField()

# Serializer pour plusieurs destinataires
class SendBroadcastSMSDeliverySerializer(serializers.Serializer):
    phone_numbers = serializers.ListField(child=serializers.CharField())
    message = serializers.CharField()

