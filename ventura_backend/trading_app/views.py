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
from .src.main import main as start_trading  # Adjusted import path
from datetime import datetime

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
        investment = InvestmentSettings.objects.filter(user_profile__user=request.user).first()
        serializer = InvestmentSettingsSerializer(investment)
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
        try:
            portfolio = Portfolio.objects.get(user_profile__user=request.user)
            serializer = PortfolioSerializer(portfolio)
            return Response(serializer.data)
        except Portfolio.DoesNotExist:
            return Response({"error": "Portfolio does not exist"}, status=status.HTTP_404_NOT_FOUND)

class StartTradingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data_file = request.data.get("data_file", "../Data/APPLE_DATA.csv")
        total_timesteps = int(request.data.get("total_timesteps", 1000))
        initial_balance = float(request.data.get("initial_balance", 100000))
        trade_fraction = float(request.data.get("trade_fraction", 0.7))
        symbol = request.data.get("symbol", "RELIANCE.BSE")
        window_size = int(request.data.get("window_size", 14))
        sptd = int(request.data.get("sptd", 390))

        # Store the investment settings in the database
        user_profile = request.user.userprofile
        investment_settings = InvestmentSettings.objects.create(
            user_profile=user_profile,
            amount=initial_balance,
            live_trading_percentage=trade_fraction,
            long_term_percentage=1 - trade_fraction,
            duration_days=total_timesteps,
            start_date=datetime.now()
        )

        # Start the trading process
        start_trading(data_file, total_timesteps, initial_balance, trade_fraction, symbol, window_size, sptd, user_profile=user_profile)

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
