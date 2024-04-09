from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from kardiograf.models import kardiografUser, HeartRateData
from django.http import JsonResponse, HttpResponse
import json, logging, time, random
from kardiograf.publish import run as publish_run
from kardiograf.subscribe import run as subscribe_run
from paho.mqtt import client as mqtt_client
from .models import EKGData, Perhitungan

broker = 'broker.emqx.io'
port = 1883
topic = "ekg/ajik"

# Create your views here.
@login_required(login_url='/error')
def home(request):
    return render(request, 'kardiograf/index.html')

class kardiograf:
    @login_required(login_url='/error')
    def countBerth(request):
        return render(request, 'kardiograf/berthCount.html', {'user': request.user})
    def rekamMedik(request):
        return render(request, 'kardiograf/rekamMedik.html', {'user': request.user})
    def profile(request):
        if request.user.is_authenticated:
            user_kardiograf = request.user.kardiografuser.first()
            # check if the logged-in user is an admin
            is_admin = user_kardiograf.role == 'admin'

            # retrive all users if the logged-in user is an admin
            all_users = kardiografUser.objects.all() if is_admin else None
            return render(request, 'kardiograf/profile.html', {'user': request.user, 'user_kardiograf': user_kardiograf, 'all_users': all_users, 'is_admin': is_admin})    
        
    def get_heart_rate_data_by_user_id(request, user_id):
        if request.method == 'GET':
            try:
                user = User.objects.get(pk=user_id)
                heart_rate_data = HeartRateData.objects.filter(user=user).order_by('-created_at')  # Order by most recent first
                data = [
                    {
                        'date_time': item.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                        'labels': item.labels,
                        'heart_rate_data': item.data
                    }
                    for item in heart_rate_data
                ]
                return JsonResponse({'data': data})
            except User.DoesNotExist:
                return JsonResponse({'error': 'User not found'}, status=404)
            except Exception as e:
                print(f"Error getting heart rate data: {e}")
                return JsonResponse({'error': str(e)}, status=500)
        else:
            return HttpResponse(status=405)  # Allow only GET requests    
    def detailLead(request):
        return render(request, 'kardiograf/detailLead.html', {'user': request.user})
    
    def ajikk(request):
        return render(request, 'kardiograf/ajikk.html', {'user': request.user})
    
    def publish_mqtt(request):
        client_id = f'publish-{random.randint(0, 100)}'
        client = mqtt_client.Client(client_id)
        client.connect(broker, port)

        while True:
            message = f"{random.uniform(90, 120)},{random.uniform(90, 120)},{random.uniform(90, 120)}"
            result = client.publish(topic, message)
            print(f"Message '{message}' published to topic '{topic}'")
            time.sleep(2)

        return JsonResponse({'status': 'success'})

    logger = logging.getLogger(__name__)

    def save_ekg_data(request):
        if request.method == 'POST':
            data = request.POST
            # Assuming user ID is sent along with the request
            user_id = data.get('data_user')
            # Retrieve the User instance based on the user ID
            user = get_object_or_404(User, pk=user_id)

            # Create KardiografPerhitungan instance
            perhitungan = Perhitungan.objects.create(user=user)

            # Extract data from the POST request
            data_lead1 = map(float, request.POST.getlist('data_lead1'))
            data_lead2 = map(float, request.POST.getlist('data_lead2'))
            data_lead3 = map(float, request.POST.getlist('data_lead3'))
            data_leadAVR = map(float, request.POST.getlist('data_leadAVR'))
            data_leadAVL = map(float, request.POST.getlist('data_leadAVL'))
            data_leadAVF = map(float, request.POST.getlist('data_leadAVF'))
            bpm = float(request.POST.get('bpm', 0))  # Default to 0 if bpm is not provided

            # Create and save the EKGData instances for each data point
            for lead1, lead2, lead3, leadAVR, leadAVL, leadAVF in zip(data_lead1, data_lead2, data_lead3, data_leadAVR, data_leadAVL, data_leadAVF):
                ekg_data = EKGData.objects.create(
                    data_lead1=lead1,
                    data_lead2=lead2,
                    data_lead3=lead3,
                    data_leadAVR=leadAVR,
                    data_leadAVL=leadAVL,
                    data_leadAVF=leadAVF,
                    bpm=bpm,
                    perhitungan=perhitungan,
                    data_user=user  # Assign the User instance, not just the ID
                )

            return JsonResponse({'message': 'Data saved successfully'}, status=200)
        else:
            return JsonResponse({'error': 'Invalid request method'}, status=400)

        # else:
        #     return render(request, 'ekg_form.html')  # Render a form template (if needed)


class errorPage:
    def needLogin(request):
        return render(request, 'authentication/pageError.html')
    

class listUsers:
    def get_all_users(request):
        users = kardiografUser.objects.all()
        data = [{
            "username": user.username, 
            "role": user.role, 
            "address": user.address, 
            "birthdate": user.birthdate, 
            "email": user.username, 
            "numberPhone": user.numberPhone
            } for user in users]
        return data
    def delete_user(request, user_id):
        try:
            # Assuming you are using the default User model
            user = User.objects.get(id=user_id)
            user.delete()
            return JsonResponse({'success': True})
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'User not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
def save_heart_rate(request):
    if request.method == 'POST':
        user = request.user.kardiografuser.first()

        try:
            # Parse JSON data
            data = json.loads(request.body.decode('utf-8'))
            labels = data.get('labels', '')
            heart_rate_data = data.get('data', '')

            if labels and heart_rate_data:
                # Save heart rate data
                user.save_heart_rate_data(labels, heart_rate_data)
                return HttpResponse(status=200)
            else:
                return HttpResponse(status=400)

        except json.JSONDecodeError:
            return HttpResponse(status=400)

    else:
        return HttpResponse(status=405)

class mqtt:
    def mqtt_publish(request):
        publish_run()
        return render(request, 'kardiograf/mqtt_publish.html')

    def mqtt_subscribe(request):
        subscribe_run()
        return render(request, 'kardiograf/mqtt_subscribe.html')

