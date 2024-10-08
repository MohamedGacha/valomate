from rest_framework import generics
from django.contrib.auth.models import User
from .serializers import ChangePasswordSerializer, ChangeUsernameSerializer, UserProfileSerializer, UserSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import EmailVerification
from .serializers import UserRegisterSerializer
from django.contrib.sites.shortcuts import get_current_site
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from .utils import send_verification_email 
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from rest_framework import status
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.http import urlsafe_base64_decode

class UserRegisterView(APIView):

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Create email verification token
            token = EmailVerification.objects.create(user=user)
            token.save()
            
            current_site = get_current_site(request)
            verification_link = f"http://{current_site}/api/verify-email/?token={token.token}"
            send_mail(
                'Verify your email',
                f'Click the link to verify your email: {verification_link}',
                'from@example.com',
                [user.email],
                fail_silently=False,
            )
            return Response({'message': 'Registration successful. Please check your email for verification.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        # Safely get the username from the request data
        username = request.data.get('username')
        
        if not username:
            return Response({"detail": "Username is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Call the parent class's post method to authenticate the user
        response = super().post(request, *args, **kwargs)

        # Get the user associated with the token
        user = get_user_model().objects.filter(username=username).first()

        # Check if the user is verified
        if user and not user.is_active:
            return Response({"detail": "Email verification is required."}, status=status.HTTP_403_FORBIDDEN)

        return response
    
class ForgotPasswordView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        if not email:
            return Response({"detail": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user with this email exists
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)

        # Generate password reset token
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        # Generate password reset link
        reset_url = reverse('password-reset-confirm', kwargs={'uidb64': uid, 'token': token})
        reset_link = f"http://127.0.0.1:8000{reset_url}"  # Change to your domain in production

        # Send reset password email
        subject = "Reset your password"
        message = render_to_string('reset_password_email.html', {
            'reset_link': reset_link,
            'user': user,
        })
        send_mail(subject, message, 'noreply@valomate.com', [email])

        return Response({"detail": "Password reset link has been sent to your email."}, status=status.HTTP_200_OK)

class PasswordResetConfirmView(APIView):
    def post(self, request, uidb64, token, *args, **kwargs):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError, OverflowError):
            return Response({"detail": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check token validity
        if not default_token_generator.check_token(user, token):
            return Response({"detail": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)

        # Reset password
        password = request.data.get('password')
        if not password:
            return Response({"detail": "Password is required."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(password)
        user.save()

        # Send confirmation email after password reset
        send_mail(
            "Your password has been changed",
            "This is to inform you that your password has been successfully changed.",
            'noreply@valomate.com',
            [user.email],
        )

        return Response({"detail": "Password reset successfully."}, status=status.HTTP_200_OK)

class DeleteAccountView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]  # Require authentication

    def get_object(self):
        return self.request.user  # Get the current user

    def destroy(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()  # Delete the user account
        return Response({"detail": "Account deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

class ResendVerificationEmailView(generics.GenericAPIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        user = get_user_model().objects.filter(email=email).first()

        if not user:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        # Check if the user is already active
        if user.is_active:
            return Response({"detail": "User is already verified."}, status=status.HTTP_400_BAD_REQUEST)

        # Get the existing verification record
        try:
            verification = EmailVerification.objects.get(user=user)
            
            # Check if the existing link is still valid
            if verification.is_valid():
                return Response({"detail": "A verification email has already been sent. Please wait for 5 minutes."},
                                status=status.HTTP_400_BAD_REQUEST)

            # Invalidate the old verification link
            verification.delete()

        except EmailVerification.DoesNotExist:
            pass  # No need to invalidate if it doesn't exist

        # Create a new verification link
        new_verification = EmailVerification.objects.create(user=user)
        send_verification_email(user.email, new_verification.token)  # Implement this function to send email

        return Response({"detail": "A new verification email has been sent."}, status=status.HTTP_200_OK)

class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]  # Require authentication

    def get_object(self):
        return self.request.user  # Get the current user

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Change the password
        self.object.set_password(serializer.validated_data['new_password'])
        self.object.save()
        return Response({"detail": "Password changed successfully."}, status=status.HTTP_200_OK)

class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]  # Require authentication

    def get_object(self):
        return self.request.user  # Get the current user

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Change the password
        self.object.set_password(serializer.validated_data['new_password'])
        self.object.save()

        # Send email notification
        send_mail(
            "Your password has been changed",
            "This is to inform you that your password has been successfully changed.",
            'noreply@valomate.com',  # From email
            [self.object.email],  # To email
        )

        return Response({"detail": "Password changed successfully."}, status=status.HTTP_200_OK)

class ChangeUsernameView(generics.UpdateAPIView):
    serializer_class = ChangeUsernameSerializer
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.update(user, serializer.validated_data)
            return Response({"detail": "Username updated successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyEmailView(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        token = request.query_params.get('token')  # Get the token from query parameters
        if not token:
            return Response({"detail": "Token is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Retrieve the EmailVerification object using the token
            verification = EmailVerification.objects.get(token=token)

            # Activate the user associated with the verification token
            verification.user.is_active = True
            verification.user.save()

            # Delete the verification record after successful verification
            verification.delete()

            return Response({"detail": "Email verified successfully."}, status=status.HTTP_200_OK)
        except EmailVerification.DoesNotExist:
            return Response({"detail": "Invalid verification token."}, status=status.HTTP_400_BAD_REQUEST)
        
class UserMeView(generics.RetrieveAPIView):
    """
    API view to retrieve the current logged-in user's profile data.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer

    def get_queryset(self):
        # Ensure only the logged-in user's data is returned
        return get_user_model().objects.filter(id=self.request.user.id)

    def get(self, request, *args, **kwargs):
        # Retrieve the user profile for the logged-in user
        user = self.request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data)