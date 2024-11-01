# trading_app/models.py
from django.contrib.auth.models import User
from django.db import models

# Ensure that the app is included in INSTALLED_APPS in settings.py

# UserProfile will store additional information about the user.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    # initial_investment = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

# InvestmentSettings will store the user's investment preferences and settings.
class InvestmentSettings(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    symbol = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    live_trading_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    long_term_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    duration_days = models.IntegerField()
    start_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_profile.user.username}'s Investment Settings"

# Trade will store information about individual trades made by the user.
class Trade(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    symbol = models.CharField(max_length=20)
    trade_type = models.CharField(max_length=10)  # 'buy' or 'sell'
    current_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Trade {self.trade_type} for {self.symbol}"

# Portfolio will store the user's portfolio information and its market value.
class Portfolio(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    market_value = models.DecimalField(max_digits=10, decimal_places=2)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user_profile.user.username}'s Portfolio"
