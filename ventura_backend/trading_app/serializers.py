# trading_app/serializers.py
from rest_framework import serializers
from .models import UserProfile, InvestmentSettings, Trade, Portfolio
from django.contrib.auth.models import User
from .data.data_fetcher import fetch_real_time_data

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

    def create(self, validated_data):
        symbol = validated_data.get('symbol')
        real_time_data = fetch_real_time_data(symbol)
        if (real_time_data):
            validated_data['initial_price'] = real_time_data['price']
        else:
            validated_data['initial_price'] = 0.00
            # raise serializers.ValidationError(f"Symbol {symbol} does not exist or failed to fetch data.")
        return super().create(validated_data)

class TradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trade
        fields = '__all__'

class PortfolioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Portfolio
        fields = '__all__'
