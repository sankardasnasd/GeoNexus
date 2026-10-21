from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Camp_coordinator_table(models.Model):
    LOGIN = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    email = models.CharField(max_length=150)
    place = models.CharField(max_length=150)
    post = models.CharField(max_length=150)
    district = models.CharField(max_length=150)
    pin = models.IntegerField()
    gender = models.CharField(max_length=150)
    phone = models.BigIntegerField()
    dob = models.DateField()
    photo = models.FileField()
    status = models.CharField(max_length=150, default='pending')


class Volunteer_table(models.Model):
    LOGIN = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    email = models.CharField(max_length=150)
    place = models.CharField(max_length=150)
    post = models.CharField(max_length=150)
    district = models.CharField(max_length=150)
    pin = models.IntegerField()
    gender = models.CharField(max_length=150)
    phone = models.BigIntegerField()
    dob = models.DateField()
    photo = models.FileField()
    status = models.CharField(max_length=150, default='pending')


class User_table(models.Model):
    LOGIN = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    email = models.CharField(max_length=150)
    place = models.CharField(max_length=150)
    post = models.CharField(max_length=150)
    district = models.CharField(max_length=150)
    pin = models.IntegerField()
    gender = models.CharField(max_length=150)
    phone = models.BigIntegerField()
    dob = models.DateField()
    photo = models.FileField()


class ERT_table(models.Model):
    LOGIN = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    email = models.CharField(max_length=150)
    place = models.CharField(max_length=150)
    post = models.CharField(max_length=150)
    district = models.CharField(max_length=150)
    pin = models.IntegerField()
    gender = models.CharField(max_length=150)
    phone = models.BigIntegerField()
    dob = models.DateField()
    photo = models.FileField()


class Guidelines_table(models.Model):
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=150)
    description = models.TextField()
    precautions = models.TextField()
    emergency_steps = models.TextField()
    date = models.DateField(auto_now_add=True)


class Complaints_table(models.Model):
    complaint = models.CharField(max_length=150)
    reply = models.CharField(max_length=150)
    date = models.DateField()
    USER = models.ForeignKey(User_table, on_delete=models.CASCADE)


class Feedbak_table(models.Model):
    feedback = models.CharField(max_length=150)
    rating = models.FloatField()
    date = models.DateField()
    USER = models.ForeignKey(User_table, on_delete=models.CASCADE)


class Notification_table(models.Model):
    title = models.CharField(max_length=150)
    date = models.DateField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    place = models.CharField(max_length=150)
    description=models.CharField(max_length=100)
    district = models.CharField(max_length=150)


class Relief_camp_table(models.Model):
    date = models.DateField()
    campname = models.CharField(max_length=150)
    capacity = models.CharField(max_length=150)
    place = models.CharField(max_length=150)
    district = models.CharField(max_length=150)
    details = models.CharField(max_length=150)
    COORDINATOR = models.ForeignKey(Camp_coordinator_table, on_delete=models.CASCADE)
    latitude = models.FloatField()
    longitude = models.FloatField()


class Disaster_victim_table(models.Model):
    name = models.CharField(max_length=150)
    email = models.CharField(max_length=150)
    gender = models.CharField(max_length=150)
    place = models.CharField(max_length=150)
    district = models.CharField(max_length=150)
    disasterdetails = models.CharField(max_length=200)
    COORDINATOR = models.ForeignKey(Camp_coordinator_table, on_delete=models.CASCADE)
    dob = models.DateField()
    phone = models.BigIntegerField()
    photo = models.FileField()
    latitude = models.FloatField()
    longitude = models.FloatField()


class Requirements_table(models.Model):
    date = models.DateField()
    title = models.CharField(max_length=150)
    needquantity = models.CharField(max_length=150)
    details = models.CharField(max_length=150)
    CAMP = models.ForeignKey(Relief_camp_table, on_delete=models.CASCADE)


class Chat_table(models.Model):
    date = models.DateField()
    message = models.CharField(max_length=150)
    FROMID = models.ForeignKey(User, on_delete=models.CASCADE, related_name="fuser")
    TOID = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tuser")


class Inventory_table(models.Model):
    name = models.CharField(max_length=150)
    quantity = models.CharField(max_length=150)
    details = models.CharField(max_length=150)
    CAMP = models.ForeignKey(Relief_camp_table, on_delete=models.CASCADE)
    date = models.DateField()


class Location(models.Model):
    date = models.DateField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    LOGIN = models.ForeignKey(User, on_delete=models.CASCADE)


class Donate_money(models.Model):
    date = models.DateField()
    REQUIREMENTS = models.ForeignKey(Requirements_table, on_delete=models.CASCADE)
    LOGIN = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=150)
    amount = models.FloatField()

class Donate_goods(models.Model):
    date = models.DateField()
    REQUIREMENTS = models.ForeignKey(Requirements_table, on_delete=models.CASCADE)
    LOGIN = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=150)
    quantity = models.CharField(max_length=150)


class Assign_table(models.Model):
    date = models.DateField()
    CAMP = models.ForeignKey(Relief_camp_table, on_delete=models.CASCADE)
    VOLUNTEER = models.ForeignKey(Volunteer_table, on_delete=models.CASCADE)
    status = models.CharField(max_length=150)


class Donations_Assign_table(models.Model):
    date = models.DateField()
    DONATE = models.ForeignKey(Donate_goods, on_delete=models.CASCADE)
    VOLUNTEER = models.ForeignKey(Volunteer_table, on_delete=models.CASCADE)
    status = models.CharField(max_length=150)


class Dialy_activity_report(models.Model):
    VOLUNTEER = models.ForeignKey(Volunteer_table, on_delete=models.CASCADE)
    date = models.DateField()
    notes = models.CharField(max_length=150)


class Prediction(models.Model):
    date = models.DateField()
    value = models.CharField(max_length=150)
    risk = models.CharField(max_length=150)
    river = models.CharField(max_length=150)
    soil_type = models.CharField(max_length=150)
    slope = models.CharField(max_length=150)
    altitude = models.CharField(max_length=150)
    rainfall = models.CharField(max_length=150)
    humidity = models.CharField(max_length=150)
    temperature = models.CharField(max_length=150)
    weather_data = models.CharField(max_length=150)
    latitude = models.FloatField()
    longitude = models.FloatField()
    LOGIN = models.ForeignKey(User, on_delete=models.CASCADE)



class Emergency_Notification_table(models.Model):
    USER = models.ForeignKey(User_table, on_delete=models.CASCADE)
    notification = models.CharField(max_length=500)
    date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=50, default="unread")


class SeenNotification(models.Model):
    LOGIN = models.ForeignKey(User, on_delete=models.CASCADE)
    NOTIFICATION = models.ForeignKey(Notification_table, on_delete=models.CASCADE)


class EmergencySOS(models.Model):
    USER = models.ForeignKey(User_table, on_delete=models.CASCADE, null=True, blank=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    status = models.CharField(max_length=50, default="Emergency")
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)


class PasswordResetOTP(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

