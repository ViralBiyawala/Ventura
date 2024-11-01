# trading_app/urls.py
from django.urls import path
from .views import RegisterView, LoginView, InvestmentSettingsView, TradeLogView, PortfolioView, StartTradingView, UserProfileView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('investment-settings/', InvestmentSettingsView.as_view(), name='investment-settings'),
    path('trade-log/', TradeLogView.as_view(), name='trade-log'),
    path('portfolio/', PortfolioView.as_view(), name='portfolio'),
    path('start-trading/', StartTradingView.as_view(), name='start-trading'),
    path('profile/', UserProfileView.as_view(), name='profile'),  # New URL for user profile
]
