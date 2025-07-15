# appbroadcastClient/vues/Client/sz_Client.py

import re
from rest_framework import serializers
from sms.models import Client


class SimpleClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ["id", "numero"]

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'

class AddClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        exclude = ['is_active']

class UpdateClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['id', 'numero', 'is_active']


