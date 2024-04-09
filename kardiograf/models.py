from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class medicalRecords(models.Model):
    herthRate = models.IntegerField()
    namaPasien = models.TextField()
    location = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)

class HeartRateData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    labels = models.TextField()
    data = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Perhitungan(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class EKGData(models.Model):
    data_lead1 = models.FloatField()
    data_lead2 = models.FloatField()
    data_lead3 = models.FloatField()
    data_leadAVR = models.FloatField()
    data_leadAVL = models.FloatField()
    data_leadAVF = models.FloatField()
    bpm = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    data_user = models.ForeignKey(User, on_delete=models.CASCADE)
    perhitungan = models.ForeignKey(Perhitungan, on_delete=models.CASCADE)

    def __str__(self):
        return f'EKGData - {self.timestamp}'


class kardiografUser(models.Model):
    ROLES = [
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
        ('admin', 'Admin'),
    ]

    username = models.ForeignKey(User, on_delete=models.CASCADE, related_name='kardiografuser')
    address = models.TextField()
    role = models.CharField(max_length=10, choices=ROLES, default='patient')
    birthdate = models.DateField(null=True)
    numberPhone = models.TextField(blank=True, null=True)
    imageUser = models.ImageField(upload_to='profile_images/', blank=True, null=True)

    def save_heart_rate_data(self, labels, data):
        # Save heart rate data for the user
        heart_rate_data = HeartRateData.objects.create(
            user=self.username,
            labels=labels,
            data=data,
        )
        heart_rate_data.save() #to save the instance
        return heart_rate_data

    