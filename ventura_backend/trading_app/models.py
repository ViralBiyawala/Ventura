# trading_app/models.py
from django.contrib.auth.models import User
from django.db import models

# UserProfile will store additional information about the user.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

# InvestmentSettings will store the user's investment preferences and settings.
class InvestmentSettings(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    symbol = models.CharField(max_length=20)
    amount = models.FloatField()
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
    current_price = models.FloatField()
    quantity = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Trade {self.trade_type} for {self.symbol}"

# Portfolio will store the user's portfolio information and its market value.
class Portfolio(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    market_value = models.FloatField(default=0.0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user_profile.user.username}'s Portfolio"

    def update_market_value(self, new_value):
        self.market_value += new_value
        self.save()
