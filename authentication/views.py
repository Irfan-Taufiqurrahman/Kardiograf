from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages, auth
from django.contrib.auth import authenticate, login, logout
from django.views import View
from django.http import JsonResponse
import json
from django.contrib.auth.models import User
from kardiograf.models import kardiografUser
from kardiograf.forms import EditProfileForm

# Create your views here.

class UsernameValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        username = data['username']
        if not username.replace(' ', '').isalnum():
            return JsonResponse({'username_error': 'username should only contain alphanumeric characters'},status=400)
        if User.objects.filter(username=username).exists():
            return JsonResponse({'username_error': 'Sorry this username has already used.'}, status=409)
        return JsonResponse({'username_valid': True})

class EmailValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data['email']
        if User.objects.filter(email=email).exists():
            return JsonResponse({'email_error': 'Sorry this email has already used.'}, status=409)
        return JsonResponse({'email_valid': True})

class signupView(View):
    def get(self, request):
        return render(request, 'authentication/signup.html')
    def post(self, request):
        if request.method == "POST":
            username = request.POST['username']
            address = request.POST['address']
            birthdate = request.POST['birthdate']
            email = request.POST['email']
            password = request.POST['pass1']

            if not User.objects.filter(username=username).exists():
                if not User.objects.filter(email=email).exists():
                    user = User.objects.create_user(username=username, email=email)
                    user.set_password(password)
                    user.save()

                    user_kardiograf = kardiografUser.objects.create(username=user, address=address, birthdate=birthdate)
                    user_kardiograf.save()
                    messages.success(request, 'Account successfully created.')

                    # Set default role to "patient"
                    user_kardiograf.role = 'patient'
                    user_kardiograf.save()

                    return render(request, 'authentication/login.html')

            else:
                messages.info(request, 'password do not match', status=403)
                return redirect('/signup')
                

class LoginView(View):
    def get(self, request):
        return render(request, 'authentication/login.html')

    def post(self, request):
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            if username and password:
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    if user.is_active:
                        auth.login(request, user)
                        messages.success(request, f'Welcome, {user.username}. You are now logged in.')


                        # Create or retrieve the kardiografUser instance
                        kardiograf_user, created = kardiografUser.objects.get_or_create(username=user)
                        
                        # Set default role to "patient" if it's a new instance
                        if created:
                            kardiograf_user.role = 'patient'
                            kardiograf_user.save()

                        # Redirect based on user role
                        if kardiograf_user.role == 'admin':
                            return redirect('countBerth')
                        elif kardiograf_user.role == 'doctor':
                            return redirect('countBerth')
                        else:
                            return redirect('countBerth')
                    else:
                        messages.error(request, 'Your account is not active.')
                else:
                    messages.error(request, 'Invalid username or password. Please try again.')
            else:
                messages.error(request, 'Please fill in all fields.')

        # If any errors occur or the method is not POST, render the login template
        return render(request, 'authentication/login.html')

class EditProfileView(View):
    def get(self, request):
        # retrive the current information user's information
        user_kardiograf = kardiografUser.objects.get_or_create(username=request.user)
        form = EditProfileForm(instance=user_kardiograf)

        # render the form the current information
        return render(request, 'authentication/edit_profile.html', {'form': form, 'user_kardiograf': user_kardiograf})
    def post(self, request):
        # retrive the current user's information
        user_kardiograf = kardiografUser.objects.get(username=request.user)
        form = EditProfileForm(request.POST, request.FILES, instance=user_kardiograf)

        if form.is_valid():
            form.save()
            messages.success(request, 'Profile update sucessfully.')
            return redirect('profile')
        else:
            errors = form.errors.as_json()
            return JsonResponse({'success': False, 'errors': errors}, status=400)

class LogoutView(View):
    def get(self, request):
        logout(request)  # Use the logout function
        messages.success(request, 'You have been logged out successfully.')
        return redirect('login')  # Redirect to the login page or any other desired page after logout