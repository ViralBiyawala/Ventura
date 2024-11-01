# trading_app/serializers.py
from rest_framework import serializers
from .models import UserProfile, InvestmentSettings, Trade, Portfolio
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        user_profile = UserProfile.objects.create(user=user)
        Portfolio.objects.create(user_profile=user_profile, market_value=0)  # Create portfolio on user registration
        return user

class InvestmentSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvestmentSettings
        fields = '__all__'

class TradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trade
        fields = '__all__'

class PortfolioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Portfolio
        fields = '__all__'
