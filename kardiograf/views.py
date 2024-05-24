from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from kardiograf.models import kardiografUser, HeartRateData
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.urls import reverse
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

    def delete_perhitungan(request, pk):
        perhitungan = get_object_or_404(Perhitungan, pk=pk)
        perhitungan.delete()
        # return JsonResponse({'message': 'Perhitungan deleted successfully'})
        return redirect('rekamMedik')

    def heart_rate_history(request):
        perhitungan_data = Perhitungan.objects.all()
        data = []
        for perhitungan in perhitungan_data:
            user_name = perhitungan.user.username if perhitungan.user else "Unknown"
            delete_url = reverse('delete_perhitungan', kwargs={'pk': perhitungan.id})

            action_html = (
                f'<a href="{delete_url}" class="delete-btn"><i class="fa-regular fa-trash-can" style="color: #f50a0a; padding: 15px;"></i></a> '
                f'<a href="#" class="info-btn" data-id="{perhitungan.id}"><i class="fa-solid fa-info" style="color: #74C0FC; padding: 15px;"></i></a>'
            )

            local_timestamp = timezone.localtime(perhitungan.timestamp)
            timestamp_formatted = local_timestamp.strftime('%A, %d %B %Y - %H:%M:%S')

            data.append({
                'id': perhitungan.id,  # Include the ID field
                'timestamp': timestamp_formatted,
                'user_id': perhitungan.user_id,
                'user_name': user_name,
                'action': action_html
            })
        return JsonResponse({'data': data})


    def get_ekg_data(request, perhitungan_id):
        ekg_data = EKGData.objects.filter(perhitungan_id=perhitungan_id)
        data = {
            'lead1': [data.data_lead1 for data in ekg_data],
            'lead2': [data.data_lead2 for data in ekg_data],
            'lead3': [data.data_lead3 for data in ekg_data],
            'leadAVR': [data.data_leadAVR for data in ekg_data],
            'leadAVL': [data.data_leadAVL for data in ekg_data],
            'leadAVF': [data.data_leadAVF for data in ekg_data],
        }
        return JsonResponse(data)
    
    def get_last_150_data(request):
        if request.method == 'GET':
            last_150_data = EKGData.objects.order_by('-id')[:150]
            data = [
                {
                    'data_lead1': ekg.data_lead1,
                    'data_lead2': ekg.data_lead2,
                    'data_lead3': ekg.data_lead3,
                    'data_leadAVR': ekg.data_leadAVR,
                    'data_leadAVL': ekg.data_leadAVL,
                    'data_leadAVF': ekg.data_leadAVF,
                    'bpm': ekg.bpm,
                    'timestamp': ekg.timestamp,
                }
                for ekg in last_150_data
            ]
            return JsonResponse(data, safe=False)
        else:
            return JsonResponse({'error': 'Invalid request method'}, status=400)


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

