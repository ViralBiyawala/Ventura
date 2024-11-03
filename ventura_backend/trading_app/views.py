# trading_app/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import UserProfile, InvestmentSettings, Trade, Portfolio
from .serializers import UserSerializer, InvestmentSettingsSerializer, TradeSerializer, PortfolioSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.http import JsonResponse
# from .tasks import start_trading_task  # Ensure this import is correct
from .src.main import main as start_trading
from datetime import datetime, timedelta
from .logs.logging_config import logger
from celery import current_app
from django.shortcuts import render

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True, "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = User.objects.filter(username=username).first()
        if user and user.check_password(password):
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            })
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

class InvestmentSettingsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        investment_settings = InvestmentSettings.objects.filter(user_profile__user=request.user)
        serializer = InvestmentSettingsSerializer(investment_settings, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = InvestmentSettingsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user_profile=request.user.userprofile)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TradeLogView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        trades = Trade.objects.filter(user_profile__user=request.user)
        serializer = TradeSerializer(trades, many=True)
        return Response(serializer.data)

class PortfolioView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        portfolio = Portfolio.objects.filter(user_profile__user=request.user)
        serializer = PortfolioSerializer(portfolio, many=True)
        return Response(serializer.data)

class StartTradingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data_file = request.data.get("data_file", "APPLE_DATA.csv")
        total_timesteps = int(request.data.get("total_timesteps", 1000))
        initial_balance = float(request.data.get("amount"))
        trade_fraction = float(request.data.get("trade_fraction"))
        symbol = request.data.get("symbol")
        window_size = int(request.data.get("window_size", 14))
        sptd = int(request.data.get("sptd", 390))
        duration_days = int(request.data.get("duration_days"))

        # Store the investment settings in the database
        user_profile = request.user.userprofile
        investment_settings = InvestmentSettings.objects.create(
            user_profile=user_profile,
            symbol=symbol,
            amount=initial_balance,
            live_trading_percentage=trade_fraction,
            long_term_percentage=1 - trade_fraction,
            duration_days=duration_days,
            start_date=datetime.now()
        )

        # Start the trading process asynchronously
        logger.info("Starting trading process asynchronously.")
        # start_trading_task.delay(data_file, total_timesteps, initial_balance, trade_fraction, symbol, window_size, sptd, user_profile.id)
        start_trading(data_file, total_timesteps, initial_balance, trade_fraction, symbol, window_size, sptd, user_profile)
        logger.info("Task has been scheduled.")

        return JsonResponse({"status": "Trading started successfully"})

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_profile = UserProfile.objects.get(user=request.user)
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def delete(self, request):
        user = request.user
        user.delete()
        return Response({"success": True, "message": "User profile deleted successfully"}, status=status.HTTP_200_OK)

class DailyBalanceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_profile = request.user.userprofile
        portfolios = Portfolio.objects.filter(user_profile=user_profile).order_by('updated_at')
        data = [{"date": portfolio.updated_at.date(), "balance": portfolio.market_value} for portfolio in portfolios]
        return Response(data)

class LiveTradeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_profile = request.user.userprofile
        trades = Trade.objects.filter(user_profile=user_profile).order_by('-timestamp')
        data = [{"id": trade.id, "symbol": trade.symbol, "trade_type": trade.trade_type, "price": trade.current_price, "quantity": trade.quantity, "timestamp": trade.timestamp} for trade in trades]
        return Response(data)

class TradeListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        trades = Trade.objects.filter(user_profile__user=request.user)
        serializer = TradeSerializer(trades, many=True)
        return Response(serializer.data)

# New view for the index page to load the frontend

class IndexView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return render(request, 'index.html')