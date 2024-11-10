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
from .tasks import start_trading_task  # Ensure this import is correct
# from .src.main import main as start_trading
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

        # Prepare the data for the serializer
        long_term_percentage = round(1 - trade_fraction, 2)  # Round to 2 decimal places
        investment_data = {
            "user_profile": request.user.userprofile.id,
            "symbol": symbol,
            "amount": initial_balance,
            "live_trading_percentage": trade_fraction,
            "long_term_percentage": long_term_percentage,
            "duration_days": duration_days,
            "start_date": datetime.now()
        }

        # Log the request data
        logger.info(f"Investment data: {investment_data}")
        # Start the trading process asynchronously
        logger.info("Starting trading process asynchronously.")
        start_trading_task.delay(data_file, total_timesteps, initial_balance, trade_fraction, symbol, window_size, sptd, request.user.userprofile.id)
        # start_trading(data_file, total_timesteps, initial_balance, trade_fraction, symbol, window_size, sptd, request.user.userprofile)
        logger.info("Task has been scheduled.")
        
        # Use the serializer to create the investment settings
        serializer = InvestmentSettingsSerializer(data=investment_data)
        if serializer.is_valid():
            investment_settings = serializer.save()
        else:
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
        symbol = request.query_params.get('symbol')
        print(user_profile, symbol)
        trades = Trade.objects.filter(user_profile=user_profile, symbol=symbol).order_by('-timestamp')
        data = [{"id": trade.id, "symbol": trade.symbol, "trade_type": trade.trade_type, "price": trade.current_price, "quantity": trade.quantity, "timestamp": trade.timestamp} for trade in trades]
        return Response(data[:390])

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

class WatchlistView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_profile = request.user.userprofile
        trades = Trade.objects.filter(user_profile=user_profile).order_by('symbol', '-timestamp')
        watchlist = []
        seen_symbols = set()
        for trade in trades:
            if trade.symbol not in seen_symbols:
                seen_symbols.add(trade.symbol)
                last_trade = Trade.objects.filter(user_profile=user_profile, symbol=trade.symbol).order_by('-timestamp').first()
                initial_price = Trade.objects.filter(user_profile=user_profile, symbol=trade.symbol).order_by('-timestamp').last()
                percentage_change = ((last_trade.current_price - initial_price.current_price) / trade.current_price) * 100
                watchlist.append({
                    "symbol": trade.symbol,
                    "initial_price": initial_price.current_price,
                    "current_price": last_trade.current_price,
                    "percentage_change": percentage_change
                })
        return Response(watchlist)

class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_profile = request.user.userprofile
        investment_settings = InvestmentSettings.objects.filter(user_profile=user_profile)

        total_investment = sum(float(setting.amount) for setting in investment_settings)
        active_trades = investment_settings.count()
        total_profit = sum((float(setting.amount) * float(setting.live_trading_percentage)) for setting in investment_settings)  # Convert both to float

        data = {
            "total_investment": total_investment,
            "active_trades": active_trades,
            "total_profit": total_profit,
        }
        return Response(data)