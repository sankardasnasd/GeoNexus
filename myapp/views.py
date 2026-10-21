from datetime import datetime
import json
import pickle
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.contrib import messages
from django.contrib.auth import logout, authenticate, login
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User, Group
import requests
from myapp.models import *

import random
from django.core.mail import send_mail


# Create your views here.

def fun_logout(request):
    logout(request)
    return redirect('/myapp/login/')


def login_get(request):
    return render(request, 'login.html')


def login_post(request):
    username = request.POST['username']
    password = request.POST['password']

    ob = authenticate(request, username=username, password=password)

    if ob is not None:

        if ob.groups.filter(name="Admin").exists():
            login(request, ob)
            return redirect('/myapp/admin_home/')

        elif ob.groups.filter(name="Camp_coordinator").exists():

            coordinator = Camp_coordinator_table.objects.filter(
                LOGIN=ob,
                status="Verified"
            ).first()

            if coordinator:
                login(request, ob)
                print(request.user.id)

                return redirect('/myapp/camp_coordinator_home')

            else:
                pending = Camp_coordinator_table.objects.filter(
                    LOGIN=ob,
                    status="pending"
                ).exists()

                if pending:
                    messages.warning(
                        request,
                        'Waiting For Admin Approval'
                    )
                else:
                    messages.warning(
                        request,
                        'Your account is not verified by Admin'
                    )

                return redirect('/myapp/login/')

        else:
            messages.warning(
                request,
                'Invalid Username and password'
            )
            return redirect('/myapp/login/')

    messages.warning(
        request,
        'Invalid Person'
    )
    return redirect('/myapp/login/')


@login_required(login_url='/myapp/login/')
def admin_home(request):
    ert = ERT_table.objects.count()
    cord = Camp_coordinator_table.objects.filter(status="Verified").count()
    vol = Volunteer_table.objects.count()
    req = EmergencySOS.objects.count()

    return render(request, 'admin/admin home.html', {
        'ert': ert,
        'vol': vol,
        'req': req,
        'camp': cord
    })


@login_required(login_url='/myapp/login/')
def camp_coordinator_home(request):
    victim = Disaster_victim_table.objects.filter(COORDINATOR__LOGIN_id=request.user.id).count()
    cord = Relief_camp_table.objects.filter(COORDINATOR__LOGIN_id=request.user.id).count()
    vol = Volunteer_table.objects.count()
    item = Inventory_table.objects.filter(CAMP__COORDINATOR__LOGIN_id=request.user.id).count()
    return render(request, 'camp coordinator/home.html', {
        'victim': victim,
        'vol': vol,
        'item': item,
        'camp': cord
    })


def registration(request):
    return render(request, 'camp coordinator/signup.html')


@login_required(login_url='/myapp/login/')
def admin_add_ert(request):
    return render(request, 'admin/add ert.html')


@login_required(login_url='/myapp/login/')
def admin_add_ert_post(request):
    name = request.POST['textfield']
    gender = request.POST['radiobutton']
    place = request.POST['textfield2']
    dob = request.POST['dob']
    post = request.POST['textfield3']
    pin = request.POST['textfield4']
    district = request.POST['district']
    phone = request.POST['textfield8']
    email = request.POST['textfield9']
    username = request.POST['username']
    password = request.POST['password']
    photo = request.FILES['photo']
    if User.objects.filter(username=username).exists():
        messages.warning(request, 'Username is already existed')
        return redirect('/myapp/admin_add_ert/')
    if User.objects.filter(email=email).exists():
        messages.warning(request, 'Email is already existed')
        return redirect('/myapp/admin_add_ert/')
    user = User.objects.create_user(
        username=username,
        password=password,
        email=email
    )
    group = Group.objects.get(name="ERT")
    user.groups.add(group)
    ert = ERT_table()
    ert.LOGIN = user
    ert.name = name
    ert.gender = gender
    ert.place = place
    ert.post = post
    ert.pin = pin
    ert.district = district
    ert.dob = dob
    ert.phone = phone
    ert.email = email
    ert.photo = photo
    ert.save()
    return redirect('/myapp/admin_view_ert/')


@login_required(login_url='/myapp/login/')
def admin_view_ert(request):
    ert_list = ERT_table.objects.all().order_by('-id')
    return render(request, 'admin/view ert.html', {'ert_list': ert_list})


@login_required(login_url='/myapp/login/')
def admin_edit_ert(request, id):
    ert = ERT_table.objects.get(id=id)
    request.session['ert_id'] = id
    return render(request, 'admin/edit ert.html', {'ert': ert})


@login_required(login_url='/myapp/login/')
def admin_ert_edit_post(request):
    ert = ERT_table.objects.get(id=request.session['ert_id'])
    ert.name = request.POST.get('name')
    ert.email = request.POST.get('email')
    ert.place = request.POST.get('place')
    ert.post = request.POST.get('post')
    ert.district = request.POST.get('district')
    ert.pin = request.POST.get('pin')
    ert.gender = request.POST.get('gender')
    ert.phone = request.POST.get('phone')
    ert.dob = request.POST.get('dob')
    if request.FILES.get('photo'):
        ert.photo = request.FILES.get('photo')
    ert.save()
    return redirect('/myapp/admin_view_ert/')


@login_required(login_url='/myapp/login/')
def admin_delete_ert(request, id):
    ert = ERT_table.objects.get(LOGIN=id)
    ert.delete()
    User.objects.get(id=id).delete()
    return redirect('/myapp/admin_view_ert/')


@login_required(login_url='/myapp/login/')
def verify_camp_coordinator(request):
    res = Camp_coordinator_table.objects.all()
    return render(request, 'admin/verify camp coordinator.html', {'data': res})


@login_required(login_url='/myapp/login/')
def approve_camp_coordinator(request, id):
    Camp_coordinator_table.objects.filter(LOGIN=id).update(status="Verified")
    return redirect('/myapp/verify_camp_coordinator/')


@login_required(login_url='/myapp/login/')
def reject_camp_coordinator(request, id):
    Camp_coordinator_table.objects.filter(LOGIN=id).update(status="Rejected")
    return redirect('/myapp/verify_camp_coordinator/')


def registration_post(request):
    name = request.POST['textfield']
    gender = request.POST['radiobutton']
    place = request.POST['textfield2']
    dob = request.POST['dob']
    post = request.POST['textfield3']
    pin = request.POST['textfield4']
    district = request.POST['district']
    phone = request.POST['textfield8']
    email = request.POST['textfield9']
    username = request.POST['username']
    password = request.POST['password']
    photo = request.FILES['photo']
    if User.objects.filter(username=username).exists():
        messages.warning(request, 'Username is already existed')
        return redirect('/myapp/registration/')

    if User.objects.filter(email=email).exists():
        messages.warning(request, 'Email is already existed')
        return redirect('/myapp/registration/')
    user = User.objects.create_user(
        username=username,
        password=password,
        email=email
    )
    group = Group.objects.get(name="Camp_coordinator")
    user.groups.add(group)
    ert = Camp_coordinator_table()
    ert.LOGIN = user
    ert.name = name
    ert.gender = gender
    ert.place = place
    ert.post = post
    ert.pin = pin
    ert.district = district
    ert.dob = dob
    ert.phone = phone
    ert.email = email
    ert.photo = photo
    ert.save()
    return redirect('/myapp/login/')


@login_required(login_url='/myapp/login/')
def camp_coordinator_viewprofile(request):
    res = Camp_coordinator_table.objects.get(LOGIN=request.user.id)
    return render(request, 'camp coordinator/view profile.html', {'data': res})


@login_required(login_url='/myapp/login/')
def camp_coordinator_editprofile(request):
    res = Camp_coordinator_table.objects.get(LOGIN=request.user.id)
    return render(request, 'camp coordinator/edit profile.html', {'data': res})


@login_required(login_url='/myapp/login/')
def camp_coordinator_editprofile_post(request):
    name = request.POST['textfield']
    gender = request.POST['radiobutton']
    place = request.POST['textfield2']
    dob = request.POST['dob']
    post = request.POST['textfield3']
    pin = request.POST['textfield4']
    district = request.POST['district']
    phone = request.POST['textfield8']
    email = request.POST['textfield9']
    ert = Camp_coordinator_table.objects.get(LOGIN=request.user.id)
    ert.name = name
    ert.gender = gender
    ert.place = place
    ert.post = post
    ert.pin = pin
    ert.district = district
    ert.dob = dob
    ert.phone = phone
    ert.email = email

    if 'photo' in request.FILES:
        photo = request.FILES['photo']
        ert.photo = photo

    ert.save()
    return redirect('/myapp/camp_coordinator_viewprofile/')


# ==========================================================
# VIEW RELIEF CAMPS
# ==========================================================

@login_required(login_url='/myapp/login/')
def manage_relief_camp(request):
    coordinator = Camp_coordinator_table.objects.get(LOGIN=request.user.id)
    camps = Relief_camp_table.objects.filter(COORDINATOR=coordinator).order_by('-date')
    return render(request, 'camp coordinator/view relief camp.html', {'data': camps})


# ==========================================================
# ADD RELIEF CAMP - PAGE
# ==========================================================

@login_required(login_url='/myapp/login/')
def add_relief_camp(request):
    return render(request, 'camp coordinator/manage relief camp.html')


# ==========================================================
# ADD RELIEF CAMP - POST
# ==========================================================

@login_required(login_url='/myapp/login/')
def add_relief_camp_post(request):
    coordinator = Camp_coordinator_table.objects.get(LOGIN=request.user.id)
    date = request.POST['date']
    campname = request.POST['campname']
    capacity = request.POST['capacity']
    place = request.POST['place']
    district = request.POST['district']
    details = request.POST['details']
    latitude = request.POST['latitude']
    longitude = request.POST['longitude']
    Relief_camp_table.objects.create(
        date=date,
        campname=campname,
        capacity=capacity,
        place=place,
        district=district,
        details=details,
        latitude=latitude,
        longitude=longitude,
        COORDINATOR=coordinator)
    return redirect('/myapp/manage_relief_camp/')


# ==========================================================
# EDIT RELIEF CAMP - PAGE
# ==========================================================
@login_required(login_url='/myapp/login/')
def edit_relief_camp(request, id):
    camp = Relief_camp_table.objects.get(id=id)
    request.session['camp_id'] = id
    return render(request, 'camp coordinator/edit relief camp.html', {'data': camp})


# ==========================================================
# EDIT RELIEF CAMP - POST
# ==========================================================

@login_required(login_url='/myapp/login/')
def edit_relief_camp_post(request, id):
    camp = Relief_camp_table.objects.get(id=request.session['camp_id'])
    camp.date = request.POST['date']
    camp.campname = request.POST['campname']
    camp.capacity = request.POST['capacity']
    camp.place = request.POST['place']
    camp.district = request.POST['district']
    camp.details = request.POST['details']
    camp.latitude = request.POST['latitude']
    camp.longitude = request.POST['longitude']
    camp.save()
    return redirect('/myapp/manage_relief_camp/')


@login_required(login_url='/myapp/login/')
def delete_camp(request, id):
    Relief_camp_table.objects.get(id=id).delete()
    return redirect('/myapp/manage_relief_camp/')


# =========================================================
# ADD REQUIREMENT PAGE
# =========================================================

@login_required(login_url='/myapp/login/')
def add_requirements(request, id):
    camp = Relief_camp_table.objects.get(id=id)
    request.session['rid'] = id
    return render(request, 'camp coordinator/add camp requirements.html', {'camp': camp})


# =========================================================
# ADD REQUIREMENT POST
# =========================================================

@login_required(login_url='/myapp/login/')
def add_requirements_post(request):
    needdate = request.POST.get('needdate')
    title = request.POST.get('title')
    needquantity = request.POST.get('needquantity')
    details = request.POST.get('details')
    Requirements_table.objects.create(
        date=needdate,
        title=title,
        needquantity=needquantity,
        details=details,
        CAMP_id=request.session['rid']
    )
    return redirect('/myapp/manage_relief_camp/')


# =========================================================
# VIEW REQUIREMENTS
# =========================================================

@login_required(login_url='/myapp/login/')
def view_requirements(request):
    requirements = Requirements_table.objects.filter(CAMP__COORDINATOR__LOGIN_id=request.user.id).order_by('-date')
    return render(request, 'camp coordinator/view camp requirements.html', {'data': requirements})


# =========================================================
# EDIT REQUIREMENT
# =========================================================

@login_required(login_url='/myapp/login/')
def edit_requirement(request, id):
    requirement = Requirements_table.objects.get(id=id)
    request.session['req_id'] = id
    return render(request, 'camp coordinator/edit requirement.html', {'data': requirement, })


# =========================================================
# EDIT REQUIREMENT POST
# =========================================================

@login_required(login_url='/myapp/login/')
def edit_requirement_post(request):
    requirement = Requirements_table.objects.get(id=request.session['req_id'])

    requirement.date = request.POST.get('needdate')
    requirement.title = request.POST.get('title')
    requirement.needquantity = request.POST.get('needquantity')
    requirement.details = request.POST.get('details')

    requirement.save()

    return redirect('/myapp/view_requirements/')


# =========================================================
# DELETE REQUIREMENT
# =========================================================

@login_required(login_url='/myapp/login/')
def delete_requirement(request, id):
    requirement = Requirements_table.objects.get(id=id).delete()
    return redirect('/myapp/view_requirements/')


# =========================================================
# ADD INVENTORY PAGE
# =========================================================

@login_required(login_url='/myapp/login/')
def add_inventory(request, id):
    camp = Relief_camp_table.objects.get(id=id)
    request.session['rid'] = id
    return render(request, 'camp coordinator/add inventory.html', {'camp': camp})


# =========================================================
# ADD INVENTORY POST
# =========================================================

@login_required(login_url='/myapp/login/')
def add_inventory_post(request):
    enterdate = datetime.now().today()
    title = request.POST.get('name')
    needquantity = request.POST.get('quantity')
    details = request.POST.get('details')
    Inventory_table.objects.create(
        date=enterdate,
        name=title,
        quantity=needquantity,
        details=details,
        CAMP_id=request.session['rid']
    )
    return redirect('/myapp/manage_relief_camp/')


# =========================================================
# VIEW INVENTORY
# =========================================================

@login_required(login_url='/myapp/login/')
def view_inventory(request):
    requirements = Inventory_table.objects.filter(CAMP__COORDINATOR__LOGIN_id=request.user.id).order_by('-date')
    return render(request, 'camp coordinator/view inventory.html', {'data': requirements})


# =========================================================
# EDIT INVENTORY
# =========================================================

@login_required(login_url='/myapp/login/')
def edit_inventory(request, id):
    requirement = Inventory_table.objects.get(id=id)
    request.session['invt_id'] = id
    return render(request, 'camp coordinator/edit inventory.html', {'data': requirement, })


# =========================================================
# EDIT INVENTORY POST
# =========================================================

@login_required(login_url='/myapp/login/')
def edit_inventory_post(request):
    requirement = Inventory_table.objects.get(id=request.session['invt_id'])

    requirement.date = datetime.now().today()
    requirement.name = request.POST.get('name')
    requirement.quantity = request.POST.get('quantity')
    requirement.details = request.POST.get('details')

    requirement.save()

    return redirect('/myapp/view_inventory/')


# =========================================================
# DELETE REQUIREMENT
# =========================================================

@login_required(login_url='/myapp/login/')
def delete_inventory(request, id):
    requirement = Inventory_table.objects.get(id=id).delete()
    return redirect('/myapp/view_inventory/')


# =========================================================
# VIEW / MANAGE DISASTER VICTIMS
# =========================================================

@login_required(login_url='/myapp/login/')
def manage_disaster_victim(request):
    coordinator = Camp_coordinator_table.objects.get(
        LOGIN=request.user.id
    )

    victims = Disaster_victim_table.objects.filter(
        COORDINATOR=coordinator
    ).order_by('-id')

    return render(
        request,
        'camp coordinator/view disaster victims.html',
        {
            'data': victims
        }
    )


# =========================================================
# ADD DISASTER VICTIM - PAGE
# =========================================================

@login_required(login_url='/myapp/login/')
def add_disaster_victim(request):
    return render(
        request,
        'camp coordinator/add disaster victims.html'
    )


# =========================================================
# ADD DISASTER VICTIM - POST
# =========================================================

@login_required(login_url='/myapp/login/')
def add_disaster_victim_post(request):
    coordinator = Camp_coordinator_table.objects.get(
        LOGIN=request.user.id
    )

    name = request.POST.get('name')
    email = request.POST.get('email')
    gender = request.POST.get('gender')
    place = request.POST.get('place')
    district = request.POST.get('district')
    disasterdetails = request.POST.get('disasterdetails')
    dob = request.POST.get('dob')
    phone = request.POST.get('phone')
    latitude = request.POST.get('latitude')
    longitude = request.POST.get('longitude')
    photo = request.FILES.get('photo')

    Disaster_victim_table.objects.create(

        name=name,

        email=email,

        gender=gender,

        place=place,

        district=district,

        disasterdetails=disasterdetails,

        COORDINATOR=coordinator,

        dob=dob,

        phone=phone,

        photo=photo,
        longitude=longitude,
        latitude=latitude,
    )

    return redirect('/myapp/manage_disaster_victim/')


# =========================================================
# EDIT DISASTER VICTIM - PAGE
# =========================================================

@login_required(login_url='/myapp/login/')
def edit_disaster_victim(request, id):
    victim = Disaster_victim_table.objects.get(id=id)

    return render(
        request,
        'camp coordinator/edit disaster victim.html',
        {
            'data': victim
        }
    )


# =========================================================
# EDIT DISASTER VICTIM - POST
# =========================================================

@login_required(login_url='/myapp/login/')
def edit_disaster_victim_post(request, id):
    victim = Disaster_victim_table.objects.get(id=id)

    victim.name = request.POST.get('name')
    victim.email = request.POST.get('email')
    victim.gender = request.POST.get('gender')
    victim.place = request.POST.get('place')
    victim.district = request.POST.get('district')
    victim.disasterdetails = request.POST.get('disasterdetails')
    victim.dob = request.POST.get('dob')
    victim.phone = request.POST.get('phone')

    # Update photo only if a new photo is selected
    if request.FILES.get('photo'):
        victim.photo = request.FILES.get('photo')

    victim.save()

    return redirect('/myapp/manage_disaster_victim/')


# =========================================================
# DELETE DISASTER VICTIM
# =========================================================

@login_required(login_url='/myapp/login/')
def delete_disaster_victim(request, id):
    Disaster_victim_table.objects.get(
        id=id
    ).delete()

    return redirect('/myapp/manage_disaster_victim/')


# =========================================================
# VIEW GUIDELINES
# =========================================================

@login_required(login_url='/myapp/login/')
def admin_view_preparedness_guidelines(request):
    data = Guidelines_table.objects.all().order_by('-date')
    return render(request, 'admin/view disaster prepardness guidence.html', {'data': data})


# =========================================================
# ADD GUIDELINE PAGE
# =========================================================

@login_required(login_url='/myapp/login/')
def admin_add_preparedness_guideline(request):
    return render(request, 'admin/upload disaster prepardness guidence.html')


# =========================================================
# ADD GUIDELINE POST
# =========================================================

@login_required(login_url='/myapp/login/')
def admin_add_preparedness_guideline_post(request):
    title = request.POST.get('title')
    category = request.POST.get('category')
    description = request.POST.get('description')
    precautions = request.POST.get('precautions')
    emergency_steps = request.POST.get('emergency_steps')
    Guidelines_table.objects.create(
        title=title,
        category=category,
        description=description,
        precautions=precautions,
        emergency_steps=emergency_steps,
        date=datetime.now().date()
    )
    return redirect('/myapp/admin_view_preparedness_guidelines/')


# =========================================================
# EDIT GUIDELINE PAGE
# =========================================================

@login_required(login_url='/myapp/login/')
def admin_edit_preparedness_guideline(request, id):
    data = Guidelines_table.objects.get(id=id)
    request.session['pid'] = id
    return render(request, 'admin/edit preparedness guideline.html', {'data': data})


# =========================================================
# EDIT GUIDELINE POST
# =========================================================

@login_required(login_url='/myapp/login/')
def admin_edit_preparedness_guideline_post(request):
    guideline = Guidelines_table.objects.get(id=request.session['pid'])
    guideline.title = request.POST.get('title')
    guideline.category = request.POST.get('category')
    guideline.description = request.POST.get('description')
    guideline.precautions = request.POST.get('precautions')
    guideline.emergency_steps = request.POST.get('emergency_steps')
    guideline.save()
    return redirect('/myapp/admin_view_preparedness_guidelines/')


# =========================================================
# DELETE GUIDELINE
# =========================================================

@login_required(login_url='/myapp/login/')
def admin_delete_preparedness_guideline(request, id):
    guideline = Guidelines_table.objects.get(id=id)
    guideline.delete()
    return redirect('/myapp/admin_view_preparedness_guidelines/')


# =========================================================
# VIEW EARLY WARNING NOTIFICATIONS
# =========================================================

@login_required(login_url='/myapp/login/')
def admin_view_notifications(request):
    notifications = Notification_table.objects.all().order_by('-date', '-id')
    return render(request, 'admin/view notification.html', {'data': notifications})


# =========================================================
# ADD EARLY WARNING NOTIFICATION - PAGE
# =========================================================

from django.shortcuts import render, redirect
from .models import Notification_table


# =========================================================
# ADD EARLY WARNING NOTIFICATION - GET
# =========================================================

@login_required(login_url='/myapp/login/')
def admin_add_notification(request):
    return render(
        request,
        'admin/add early warning.html'
    )


# =========================================================
# ADD EARLY WARNING NOTIFICATION - POST
# =========================================================

@login_required(login_url='/myapp/login/')
def admin_add_notification_post(request):
    if request.method == "POST":
        title = request.POST.get('title')
        description = request.POST.get('description')
        notification_date = request.POST.get('date')

        place = request.POST.get('place')
        district = request.POST.get('district')

        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')

        # -------------------------------------------------
        # CREATE NOTIFICATION
        # -------------------------------------------------

        Notification_table.objects.create(

            title=title,

            description=description,

            date=notification_date,

            latitude=float(latitude),

            longitude=float(longitude),

            place=place,

            district=district
        )

        return redirect(
            '/myapp/admin_view_notifications/'
        )

    return redirect(
        '/myapp/admin_add_notification/'
    )


# =========================================================
# EDIT EARLY WARNING NOTIFICATION - PAGE
# =========================================================

@login_required(login_url='/myapp/login/')
def admin_edit_notification(request, id):
    notification = Notification_table.objects.get(id=id)
    request.session['nid'] = id
    return render(request, 'admin/edit early warning.html', {'data': notification})


# =========================================================
# EDIT EARLY WARNING NOTIFICATION - POST
# =========================================================

@login_required(login_url='/myapp/login/')
def admin_edit_notification_post(request):
    notification = Notification_table.objects.get(id=request.session['nid'])
    notification.title = request.POST.get('title')
    notification.description = request.POST.get('description')
    notification.date = request.POST.get('date')
    notification.save()
    return redirect('/myapp/admin_view_notifications/')


# =========================================================
# DELETE EARLY WARNING NOTIFICATION
# =========================================================

@login_required(login_url='/myapp/login/')
def admin_delete_notification(request, id):
    notification = Notification_table.objects.get(id=id)
    notification.delete()
    return redirect('/myapp/admin_view_notifications/')


@login_required(login_url
                ='/myapp/login/')
def admin_view_complaints(request):
    comp = Complaints_table.objects.all().order_by('-date', '-id')
    return render(request, 'admin/view complaints.html', {'data': comp})


@login_required(login_url='/myapp/login/')
def send_reply(request, id):
    request.session['com_id'] = id
    return render(request, 'admin/send reply.html')


@login_required(login_url='/myapp/login/')
def send_reply_post(request):
    reply = request.POST['reply']
    obj = Complaints_table.objects.get(id=request.session['com_id'])
    obj.reply = reply
    obj.save()
    return redirect('/myapp/admin_view_complaints/')


@login_required(login_url='/myapp/login/')
def admin_view_feedback(request):
    comp = Feedbak_table.objects.all().order_by('-date', '-id')
    return render(request, 'admin/view feedback.html', {'data': comp})


@login_required(login_url='/myapp/login/')
def admin_assign_volunteer(request, id):
    request.session['vid'] = id
    camp = Relief_camp_table.objects.all()
    return render(request, 'admin/assign volunteer.html', {'camps': camp})


@login_required(login_url='/myapp/login/')
def admin_assign_volunteer_post(request):
    camp = request.POST['camp']
    obj = Assign_table()
    obj.date = datetime.now().today()
    obj.VOLUNTEER_id = request.session['vid']
    obj.CAMP_id = camp
    obj.status = 'Assigned'
    obj.save()
    return redirect('/myapp/admin_verify_volunteers/')


@login_required(login_url='/myapp/login/')
def verify_volunteers(request):
    res = Volunteer_table.objects.all()
    return render(request, 'admin/verify volunteers.html', {'data': res})


@login_required(login_url='/myapp/login/')
def approve_volunteers(request, id):
    Volunteer_table.objects.filter(LOGIN=id).update(status="Verified")
    return redirect('/myapp/admin_verify_volunteers/')


@login_required(login_url='/myapp/login/')
def reject_volunteers(request, id):
    Volunteer_table.objects.filter(LOGIN=id).update(status="Rejected")
    return redirect('/myapp/admin_verify_volunteers/')


@login_required(login_url='/myapp/login/')
def admin_view_assigned_volunteers(request):
    data = Assign_table.objects.select_related(
        'VOLUNTEER',
        'CAMP'
    ).order_by('-date', '-id')

    return render(
        request,
        'admin/view assign volunteer.html',
        {'data': data}
    )


@login_required(login_url='/myapp/login/')
def admin_delete_assigned_volunteer(request, id):
    Assign_table.objects.filter(id=id).delete()

    return redirect('/myapp/admin_view_assigned_volunteers/')


@login_required(login_url='/myapp/login/')
def coordinator_view_ert(request):
    res = ERT_table.objects.all()
    return render(request, 'camp coordinator/view ert.html', {'data': res})


@login_required(login_url='/myapp/login/')
def coordinator_view_volunteers(request):
    data = Assign_table.objects.filter(CAMP__COORDINATOR__LOGIN_id=request.user)
    return render(request, 'camp coordinator/view volunteers.html', {'data': data})


####################################################flutter

def user_register(request):
    name = request.POST['textfield']
    gender = request.POST['radiobutton']
    place = request.POST['textfield2']
    dob = request.POST['dob']
    post = request.POST['textfield3']
    pin = request.POST['textfield4']
    district = request.POST['district']
    phone = request.POST['textfield8']
    email = request.POST['textfield9']
    username = request.POST['username']
    password = request.POST['password']
    photo = request.FILES['photo']

    if User.objects.filter(username=username).exists():
        return JsonResponse({'status': 'no'})

    if User.objects.filter(email=email).exists():
        return JsonResponse({'status': 'no'})

    user = User.objects.create_user(
        username=username,
        password=password,
        email=email
    )
    group = Group.objects.get(name="User")
    user.groups.add(group)
    ert = User_table()
    ert.LOGIN = user
    ert.name = name
    ert.gender = gender
    ert.place = place
    ert.post = post
    ert.pin = pin
    ert.district = district
    ert.dob = dob
    ert.phone = phone
    ert.email = email
    ert.photo = photo
    ert.save()
    return JsonResponse({'status': 'ok'})


def volunteer_register(request):
    name = request.POST['textfield']
    gender = request.POST['radiobutton']
    place = request.POST['textfield2']
    dob = request.POST['dob']
    post = request.POST['textfield3']
    pin = request.POST['textfield4']
    district = request.POST['district']
    phone = request.POST['textfield8']
    email = request.POST['textfield9']
    username = request.POST['username']
    password = request.POST['password']
    photo = request.FILES['photo']
    if User.objects.filter(username=username).exists():
        return JsonResponse({'status': 'no'})

    if User.objects.filter(email=email).exists():
        return JsonResponse({'status': 'no'})

    user = User.objects.create_user(
        username=username,
        password=password,
        email=email
    )
    group = Group.objects.get(name="Volunteer")
    user.groups.add(group)
    ert = Volunteer_table()
    ert.LOGIN = user
    ert.name = name
    ert.gender = gender
    ert.place = place
    ert.post = post
    ert.pin = pin
    ert.district = district
    ert.dob = dob
    ert.phone = phone
    ert.email = email
    ert.photo = photo
    ert.save()
    return JsonResponse({'status': 'ok'})


def app_changepassword(request):
    id = request.POST['lid']
    current_password = request.POST['current_password']
    new_password = request.POST['new_password']
    confirm_password = request.POST['confirm_password']
    res = User.objects.get(id=id)
    if res.check_password(current_password):
        if new_password == confirm_password:
            res.set_password(new_password)
            res.save()
            return JsonResponse({'status': 'ok'})
        else:
            return JsonResponse({'status': 'no'})
    else:
        return JsonResponse({'status': 'no'})


def app_login(request):
    if request.method != "POST":
        return JsonResponse({
            'status': 'error',
            'message': 'POST method required'
        })

    username = request.POST.get('username', '').strip()
    password = request.POST.get('password', '').strip()

    if not username or not password:
        return JsonResponse({
            'status': 'error',
            'message': 'Username and password required'
        })

    user = authenticate(
        request,
        username=username,
        password=password
    )

    if user is None:
        return JsonResponse({
            'status': 'no',
            'message': 'Invalid username or password'
        })

    volunteer = Volunteer_table.objects.filter(
        LOGIN_id=user.id
    ).first()

    if volunteer:

        if volunteer.status == "pending":
            return JsonResponse({
                'status': 'not',
                'message': 'Waiting For Admin Approval'
            })

        if volunteer.status == "Rejected":
            return JsonResponse({
                'status': 'rejected',
                'message': 'Your volunteer application was rejected'
            })

        if volunteer.status == "Verified":
            login(request, user)

            return JsonResponse({
                'status': 'ok',
                'lid': str(user.id),
                'type': 'Volunteer'
            })

    if user.groups.filter(name="User").exists():

        login(request, user)

        return JsonResponse({
            'status': 'ok',
            'lid': str(user.id),
            'type': 'User'
        })


    elif user.groups.filter(name="ERT").exists():

        login(request, user)

        return JsonResponse({
            'status': 'ok',
            'lid': str(user.id),
            'type': 'ERT'
        })

    return JsonResponse({
        'status': 'no',
        'message': 'User type not recognized'
    })


def user_viewprofile(request):
    id = request.POST['lid']
    a = User_table.objects.get(LOGIN_id=id)
    return JsonResponse({
        'status': 'ok',
        'name': a.name,
        'gender': a.gender,
        'phone': a.phone,
        'email': a.email,
        'DOB': a.dob,
        'place': a.place,
        'post': a.post,
        'pincode': a.pin,
        'district': a.district,
        'photo': request.build_absolute_uri(a.photo.url) if a.photo else "",
    })


def user_edit_profile(request):
    name = request.POST['textfield']
    gender = request.POST['radiobutton']
    place = request.POST['textfield2']
    dob = request.POST['dob']
    post = request.POST['textfield3']
    pin = request.POST['textfield4']
    district = request.POST['district']
    phone = request.POST['textfield8']
    email = request.POST['textfield9']
    lid = request.POST['lid']
    ert = User_table.objects.get(LOGIN=lid)
    if 'photo' in request.FILES:
        photo = request.FILES['photo']
        ert.photo = photo
        ert.save()
    ert.name = name
    ert.gender = gender
    ert.place = place
    ert.post = post
    ert.pin = pin
    ert.district = district
    ert.dob = dob
    ert.phone = phone
    ert.email = email
    ert.save()
    return JsonResponse({'status': 'ok'})


def usersendcomplaint(request):
    complaint = request.POST['complaint']
    lid = request.POST['lid']
    lob = Complaints_table()
    lob.USER = User_table.objects.get(LOGIN__id=lid)
    lob.complaint = complaint
    lob.reply = 'pending'
    lob.date = datetime.now().today()
    lob.save()
    return JsonResponse({'task': 'ok'})


def userviewreply(request):
    lid = request.POST['lid']
    ob = Complaints_table.objects.filter(USER__LOGIN_id=lid)
    mdata = []
    for i in ob:
        mdata.append({
            'USER': i.USER.name, 'complaint': i.complaint, 'reply': i.reply,
            'date': str(i.date), 'id': str(i.id)

        })
    print(mdata)
    return JsonResponse({"status": "ok", "data": mdata})


def usersendfeedback(request):
    feedback = request.POST['feedback']
    rating = request.POST['rating']
    lid = request.POST['lid']
    lob = Feedbak_table()
    lob.USER = User_table.objects.get(LOGIN__id=lid)
    lob.feedback = feedback
    lob.rating = rating
    lob.date = datetime.now().today()
    lob.save()
    return JsonResponse({'status': 'ok'})


def userguidelines(request):
    ob = Guidelines_table.objects.all()
    mdata = []
    for i in ob:
        mdata.append({
            'title': i.title,
            'category': i.category,
            'description': i.description,
            'precautions': i.precautions,
            'emergency_steps': i.emergency_steps,
            'date': str(i.date),
            'id': str(i.id)

        })
    print(mdata)
    return JsonResponse({"status": "ok", "data": mdata})


def userviewnearbycamp(request):
    ob = Relief_camp_table.objects.all()
    mdata = []
    for i in ob:
        mdata.append({
            'campname': i.campname,
            'capacity': i.capacity,
            'place': i.place,
            'district': i.district,
            'details': i.details,
            'latitude': i.latitude,
            'longitude': i.longitude,
            'date': str(i.date),
            'coordinator_name': str(i.COORDINATOR.name),
            'coordinator_phone': str(i.COORDINATOR.phone),
            'coordinator_place': str(i.COORDINATOR.place),

            'id': str(i.id)

        })
    print(mdata)
    return JsonResponse({"status": "ok", "data": mdata})


from django.http import JsonResponse
from django.contrib.auth.models import User
from math import radians, sin, cos, sqrt, atan2


def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate distance between two latitude/longitude points.
    Returns distance in kilometers.
    """

    R = 6371.0  # Earth radius in KM

    lat1 = radians(float(lat1))
    lon1 = radians(float(lon1))
    lat2 = radians(float(lat2))
    lon2 = radians(float(lon2))

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        sin(dlat / 2) ** 2
        + cos(lat1)
        * cos(lat2)
        * sin(dlon / 2) ** 2
    )

    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c


def userviewnotification(request):
    try:

        # ---------------------------------------------------------
        # GET VOLUNTEER LOGIN ID
        # ---------------------------------------------------------

        lid = request.POST.get('lid')

        if not lid:
            return JsonResponse({
                "status": "no",
                "message": "Volunteer login ID is required"
            })

        # ---------------------------------------------------------
        # GET VOLUNTEER LATEST LOCATION
        # ---------------------------------------------------------

        location = Location.objects.filter(
            LOGIN_id=lid
        ).order_by('-date').first()

        if not location:
            return JsonResponse({
                "status": "no",
                "message": "Volunteer location not found",
                "data": []
            })

        volunteer_lat = float(location.latitude)
        volunteer_lon = float(location.longitude)

        print("Volunteer Latitude:", volunteer_lat)
        print("Volunteer Longitude:", volunteer_lon)

        # ---------------------------------------------------------
        # NOTIFICATION SEARCH RADIUS
        # ---------------------------------------------------------

        radius = 10.0  # 10 KM

        # ---------------------------------------------------------
        # GET ALL NOTIFICATIONS
        # ---------------------------------------------------------

        notifications = Notification_table.objects.all().order_by('-date')

        mdata = []

        for i in notifications:

            try:

                notification_lat = float(i.latitude)
                notification_lon = float(i.longitude)

                distance = calculate_distance(
                    volunteer_lat,
                    volunteer_lon,
                    notification_lat,
                    notification_lon
                )

                print(
                    "Notification:",
                    i.title,
                    "Distance:",
                    round(distance, 2),
                    "KM"
                )

                # -------------------------------------------------
                # ONLY NEARBY NOTIFICATIONS
                # -------------------------------------------------

                if distance <= radius:
                    mdata.append({

                        'id': str(i.id),

                        'title': i.title,

                        'description': i.description,

                        'date': str(i.date),

                        'latitude': str(i.latitude),

                        'longitude': str(i.longitude),

                        'place': i.place,

                        'district': i.district,

                        'distance': round(distance, 2),

                    })

            except Exception as e:

                print(
                    "Notification distance error:",
                    i.id,
                    e
                )

        # ---------------------------------------------------------
        # SORT BY NEAREST
        # ---------------------------------------------------------

        mdata.sort(
            key=lambda x: x['distance']
        )

        print("Nearby Notifications:")
        print(mdata)

        # ---------------------------------------------------------
        # RESPONSE
        # ---------------------------------------------------------

        return JsonResponse({

            "status": "ok",

            "message": "Nearby notifications loaded",

            "volunteer_location": {

                "latitude": volunteer_lat,

                "longitude": volunteer_lon,

            },

            "radius": radius,

            "data": mdata

        })

    except Exception as e:

        print("Notification API Error:", e)

        return JsonResponse({

            "status": "no",

            "message": str(e),

            "data": []

        })


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone


@csrf_exempt
def _update_location(request):
    if request.method != "POST":
        return JsonResponse({
            "status": "error",
            "message": "POST method required"
        }, status=405)

    try:
        lid = request.POST.get("lid")
        lat = request.POST.get("lat")
        lon = request.POST.get("lon")

        if not lid:
            return JsonResponse({
                "status": "error",
                "message": "Login ID missing"
            }, status=400)

        if not lat or not lon:
            return JsonResponse({
                "status": "error",
                "message": "Latitude or longitude missing"
            }, status=400)

        today = timezone.localdate()

        dobj, created = Location.objects.get_or_create(
            LOGIN_id=lid,
            defaults={
                "date": today,
                "latitude": float(lat),
                "longitude": float(lon),
            }
        )

        if not created:
            dobj.latitude = float(lat)
            dobj.longitude = float(lon)
            dobj.date = today
            dobj.save()

        return JsonResponse({
            "status": "ok",
            "message": "Location updated successfully",
            "latitude": lat,
            "longitude": lon
        })

    except Exception as e:

        print("Location update error:", e)

        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=500)


def userviewinventory(request):
    cid = request.POST['cid']
    ob = Inventory_table.objects.filter(CAMP_id=cid)
    mdata = []
    for i in ob:
        mdata.append({
            'name': i.name,
            'quantity': i.quantity,
            'details': i.details,
            'date': str(i.date),
            'id': str(i.id)

        })
    print(mdata)
    return JsonResponse({"status": "ok", "data": mdata})


def userviewrequirements(request):
    cid = request.POST['cid']
    ob = Requirements_table.objects.filter(CAMP_id=cid)
    mdata = []
    for i in ob:
        mdata.append({
            'title': i.title,
            'needquantity': i.needquantity,
            'details': i.details,
            'date': str(i.date),
            'id': str(i.id)

        })
    print(mdata)
    return JsonResponse({"status": "ok", "data": mdata})


def donate_relief_goods(request):
    reqid = request.POST['reqid']
    lid = request.POST['lid']
    quantity = request.POST['quantity']
    obj = Donate_goods()
    obj.date = datetime.now().today()
    obj.REQUIREMENTS_id = reqid
    obj.quantity = quantity
    obj.LOGIN = User.objects.get(id=lid)
    obj.status = "Donated"
    obj.save()
    return JsonResponse({'status': 'ok'})


def volunteer_viewprofile(request):
    id = request.POST['lid']
    a = Volunteer_table.objects.get(LOGIN_id=id)
    return JsonResponse({
        'status': 'ok',
        'name': a.name,
        'gender': a.gender,
        'phone': a.phone,
        'email': a.email,
        'DOB': a.dob,
        'place': a.place,
        'post': a.post,
        'pincode': a.pin,
        'district': a.district,
        'photo': request.build_absolute_uri(a.photo.url) if a.photo else "",
    })


def volunteer_edit_profile(request):
    name = request.POST['textfield']
    gender = request.POST['radiobutton']
    place = request.POST['textfield2']
    dob = request.POST['dob']
    post = request.POST['textfield3']
    pin = request.POST['textfield4']
    district = request.POST['district']
    phone = request.POST['textfield8']
    email = request.POST['textfield9']
    lid = request.POST['lid']
    ert = Volunteer_table.objects.get(LOGIN=lid)
    if 'photo' in request.FILES:
        photo = request.FILES['photo']
        ert.photo = photo
        ert.save()
    ert.name = name
    ert.gender = gender
    ert.place = place
    ert.post = post
    ert.pin = pin
    ert.district = district
    ert.dob = dob
    ert.phone = phone
    ert.email = email
    ert.save()
    return JsonResponse({'status': 'ok'})


def ert_viewprofile(request):
    id = request.POST['lid']
    a = ERT_table.objects.get(LOGIN_id=id)
    return JsonResponse({
        'status': 'ok',
        'name': a.name,
        'gender': a.gender,
        'phone': a.phone,
        'email': a.email,
        'DOB': a.dob,
        'place': a.place,
        'post': a.post,
        'pincode': a.pin,
        'district': a.district,
        'photo': request.build_absolute_uri(a.photo.url) if a.photo else "",
    })


############################################camp coordinator chat with ert
def chat1(request, id):
    request.session["userid"] = id
    cid = str(request.session["userid"])
    request.session["new"] = cid
    qry = ERT_table.objects.get(LOGIN=cid)
    return render(request, "camp coordinator/Chat.html",
                  {'photo': request.build_absolute_uri(qry.photo.url) if qry.photo else "", 'name': qry.name,
                   'toid': cid})


def chat_view(request):
    fromid = request.user.id
    toid = request.session["userid"]
    qry = ERT_table.objects.get(LOGIN=request.session["userid"])
    from django.db.models import Q
    res = Chat_table.objects.filter(Q(FROMID_id=fromid, TOID_id=toid) | Q(FROMID_id=toid, TOID_id=fromid))
    l = []
    for i in res:
        l.append({"id": i.id, "message": i.message, "to": i.TOID_id, "date": i.date, "from": i.FROMID_id})
    return JsonResponse(
        {'photo': request.build_absolute_uri(qry.photo.url) if qry.photo else "", "data": l, 'name': qry.name,
         'toid': request.session["userid"]})


def chat_send(request, msg):
    lid = request.user.id
    toid = request.session["userid"]
    message = msg
    import datetime
    d = datetime.datetime.now().date()
    chatobt = Chat_table()
    chatobt.message = message
    chatobt.TOID_id = toid
    chatobt.FROMID_id = lid
    chatobt.date = d
    chatobt.save()
    return JsonResponse({"status": "ok"})


##############################################################


# camp coordinator chat with volunteer


def chat2(request, id):
    request.session["userid"] = id
    cid = str(request.session["userid"])
    request.session["new"] = cid
    qry = Volunteer_table.objects.get(LOGIN=cid)
    return render(request, "camp coordinator/chat with volunteers.html",
                  {'photo': request.build_absolute_uri(qry.photo.url) if qry.photo else "", 'name': qry.name,
                   'toid': cid})


def chat_view2(request):
    fromid = request.user.id
    toid = request.session["userid"]
    qry = Volunteer_table.objects.get(LOGIN=request.session["userid"])
    from django.db.models import Q
    res = Chat_table.objects.filter(
        Q(FROMID_id=fromid, TOID_id=toid) |
        Q(FROMID_id=toid, TOID_id=fromid)).order_by('id')
    l = []
    for i in res:
        l.append({"id": i.id, "message": i.message, "to": i.TOID_id, "date": i.date, "from": i.FROMID_id})
    return JsonResponse(
        {'photo': request.build_absolute_uri(qry.photo.url) if qry.photo else "", "data": l, 'name': qry.name,
         'toid': request.session["userid"]})


def chat_send2(request, msg):
    lid = request.user.id
    toid = request.session["userid"]
    message = msg
    import datetime
    d = datetime.datetime.now().date()
    chatobt = Chat_table()
    chatobt.message = message
    chatobt.TOID_id = toid
    chatobt.FROMID_id = lid
    chatobt.date = d
    chatobt.save()
    return JsonResponse({"status": "ok"})


def volunteer_view_assigned_camp(request):
    lid = request.POST['lid']
    ob = Assign_table.objects.filter(VOLUNTEER__LOGIN_id=lid)
    mdata = []
    for i in ob:
        mdata.append({
            'campname': i.CAMP.campname,
            'place': i.CAMP.place,
            'district': i.CAMP.district,
            'login': i.CAMP.COORDINATOR.LOGIN.id,
            'coordinatorname': i.CAMP.COORDINATOR.name,
            'coordinatorphone': i.CAMP.COORDINATOR.phone,
            'status': i.status,
            'date': str(i.date),
            'id': str(i.id)

        })
    print(mdata)
    return JsonResponse({"status": "ok", "data": mdata})


##################blockchain

from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth.models import User
from myapp.models import Requirements_table, Donate_money


@csrf_exempt
@require_POST
def add_donation_bc_post(request):
    """
    Records a donation entry linked to a requirement and the logged-in user.
    """
    reqid = request.POST.get('reqid')
    amount = request.POST.get('amount')
    userid = request.POST.get('lid')
    payment_id = request.POST.get('payment_id', '')

    # 1. Validation
    if not reqid or not amount or not userid:
        return JsonResponse({
            'status': 'error',
            'message': 'Requirement ID, amount, and user ID are required'
        }, status=400)

    try:
        donation_amount = float(amount)
        if donation_amount <= 0:
            return JsonResponse({
                'status': 'error',
                'message': 'Donation amount must be greater than zero'
            }, status=400)
    except (ValueError, TypeError):
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid amount format'
        }, status=400)

    # 2. Get Requirement
    try:
        req_obj = Requirements_table.objects.get(id=int(reqid))
    except Requirements_table.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Requirement not found'
        }, status=404)

    # 3. Get User (LOGIN)
    try:
        user_obj = User.objects.get(id=int(userid))
    except User.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'User not found'
        }, status=404)

    # 4. Save Donation Record
    donation = Donate_money.objects.create(
        date=datetime.now().date(),
        REQUIREMENTS=req_obj,
        LOGIN=user_obj,
        status="Completed" if payment_id else "Pending",
        amount=donation_amount
    )

    return JsonResponse({
        'status': 'ok',
        'message': 'Donation successfully recorded',
        'donation_id': donation.id,
        'requirement_id': req_obj.id,
        'amount': donation.amount,
        'date': str(donation.date),
        'donation_status': donation.status
    })


@csrf_exempt
def view_my_donations(request):
    """
    Retrieves donation history for a specific user.
    Can accept 'lid' via GET or POST.
    """
    userid = request.GET.get('lid') or request.POST.get('lid')

    if not userid:
        return JsonResponse({
            'status': 'error',
            'message': 'User ID (lid) is missing'
        }, status=400)

    try:
        user_obj = User.objects.get(id=int(userid))
    except User.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'User not found'
        }, status=404)

    donations = Donate_money.objects.filter(LOGIN=user_obj).select_related('REQUIREMENTS').order_by('-id')

    donation_list = []
    for d in donations:
        donation_list.append({
            'id': d.id,
            'amount': d.amount,
            'status': d.status,
            'date': str(d.date),
            'requirement_id': d.REQUIREMENTS.id,
            # Requirements_table-ൽ ഉള്ള ഫീൽഡുകൾക്കനുസരിച്ച് (ഉദാ: requirement_name, description) താഴെ നൽകാം:
            'requirement_title': getattr(d.REQUIREMENTS, 'requirement', getattr(d.REQUIREMENTS, 'title', 'Requirement')),
        })

    return JsonResponse({
        'status': 'ok',
        'data': donation_list
    })
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from myapp.models import Requirements_table



from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from myapp.models import Donate_money


@csrf_exempt
def user_view_send_donations(request):
    """
    Returns all donations made by the user, including the donated amount,
    status, requirement information, camp name, and coordinator contacts.
    """
    try:
        userid = request.POST.get('lid') or request.GET.get('lid')

        if not userid:
            return JsonResponse({
                'status': 'error',
                'message': 'User ID (lid) is missing'
            }, status=400)

        try:
            user_obj = User.objects.get(id=int(userid))
        except (User.DoesNotExist, ValueError):
            return JsonResponse({
                'status': 'error',
                'message': 'User record not found'
            }, status=404)

        # Query Donate_money and prefetch linked Requirements, Camp, and Coordinator
        donations = Donate_money.objects.filter(LOGIN=user_obj).select_related(
            'REQUIREMENTS',
            'REQUIREMENTS__CAMP',
            'REQUIREMENTS__CAMP__COORDINATOR'
        ).order_by('-id')

        data_list = []
        total_amount = 0.0

        for donation in donations:
            total_amount += float(donation.amount)

            req = donation.REQUIREMENTS
            camp = req.CAMP if req else None
            coord = camp.COORDINATOR if camp else None

            data_list.append({
                'donation_id': donation.id,
                'amount': float(donation.amount),
                'donation_status': str(donation.status),
                'donation_date': donation.date.strftime("%Y-%m-%d") if donation.date else "",

                # Requirement fields
                'id': req.id if req else None,
                'title': req.title if req else "Relief Assistance",
                'needquantity': req.needquantity if req else "",
                'details': req.details if req else "",

                # Camp fields
                'camp_name': camp.campname if camp else "Not Specified",
                'camp_place': camp.place if camp else "",
                'camp_district': camp.district if camp else "",

                # Coordinator fields
                'coordinator_name': coord.name if coord else "Not Assigned",
                'coordinator_phone': str(coord.phone) if coord else "",
            })

        return JsonResponse({
            'status': 'ok',
            'total_contributed': round(total_amount, 2),
            'count': len(data_list),
            'data': data_list
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f"Failed to retrieve donations: {str(e)}"
        }, status=500)


@csrf_exempt
def view_amount_requirement_donations(request):

    reqid = request.GET.get('reqid') or request.POST.get('reqid')

    if not reqid:
        return JsonResponse({
            'status': 'error',
            'message': 'Requirement ID (reqid) is missing'
        }, status=400)

    try:
        req_obj = Requirements_table.objects.get(id=int(reqid))
    except Requirements_table.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Requirement not found'
        }, status=404)

    donations = Donate_money.objects.filter(REQUIREMENTS=req_obj).select_related('LOGIN').order_by('-id')

    donation_list = []
    total_collected = 0.0

    for d in donations:
        total_collected += d.amount
        donation_list.append({
            'id': d.id,
            'amount': d.amount,
            'status': d.status,
            'date': str(d.date),
            'donor_name': d.LOGIN.username,
        })

    return JsonResponse({
        'status': 'ok',
        'requirement_id': req_obj.id,
        'total_collected': total_collected,
        'donations': donation_list
    })


def user_view_goods_history(request):
    lid = request.POST['lid']
    ob = Donate_goods.objects.filter(LOGIN_id=lid)
    mdata = []
    for i in ob:
        mdata.append({
            'title': i.REQUIREMENTS.title,
            'needquantity': i.REQUIREMENTS.needquantity,
            'details': i.REQUIREMENTS.details,
            'campname': i.REQUIREMENTS.CAMP.campname,
            'place': i.REQUIREMENTS.CAMP.place,
            'coordinatorname': i.REQUIREMENTS.CAMP.COORDINATOR.name,
            'coordinatorphone': i.REQUIREMENTS.CAMP.COORDINATOR.phone,
            'quantity': i.quantity,
            'status': i.status,
            'date': str(i.date),
            'id': str(i.id)

        })
    print(mdata)
    return JsonResponse({"status": "ok", "data": mdata})


def view_goods_donations(request):
    don = Donate_goods.objects.filter(
        REQUIREMENTS__CAMP__COORDINATOR__LOGIN_id=request.user.id
    ).order_by('-date')

    l = []

    for i in don:
        d = Donations_Assign_table.objects.filter(
            DONATE_id=i.id
        ).select_related('VOLUNTEER').first()

        l.append({
            'id': i.id,
            'date': i.date,
            'status': i.status,
            'quantity': i.quantity,

            'title': i.REQUIREMENTS.title,
            'details': i.REQUIREMENTS.details,

            'username': i.LOGIN.username,
            'email': i.LOGIN.email,

            'campname': i.REQUIREMENTS.CAMP.campname,
            'place': i.REQUIREMENTS.CAMP.place,

            # Volunteer details
            'volunteer': d.VOLUNTEER.name if d else 'Not Assigned',
            'phone': d.VOLUNTEER.phone if d else 'Not Assigned',
            'dstatus': d.status if d else 'Not Assigned',
        })

    return render(
        request,
        'camp coordinator/view request resources.html',
        {'data': l}
    )


def coordinator_assigntask_volunteer(request, id):
    request.session['did'] = id
    camp = Assign_table.objects.filter(CAMP__COORDINATOR__LOGIN_id=request.user.id)
    return render(request, 'camp coordinator/assign volunteer.html', {'camps': camp})


def admin_assigntask_volunteer_post(request):
    volunteer = request.POST['volunteer']
    obj = Donations_Assign_table()
    obj.date = datetime.now().today()
    obj.VOLUNTEER_id = volunteer
    obj.DONATE_id = request.session['did']
    obj.status = 'Task Assigned'
    obj.save()



    return redirect('/myapp/view_goods_donations/')


@login_required(login_url='/myapp/login/')
def change_passwords(request):
    return render(request, 'camp coordinator/changepassword.html')


@login_required(login_url='/myapp/login/')
def change_passwordposts(request):
    current_password = request.POST['current_password']
    new_password = request.POST['new_password']
    confirm_password = request.POST['confirm_password']

    f = check_password(current_password, request.user.password)
    if f:
        if new_password == confirm_password:
            user = request.user
            user.set_password(confirm_password)
            user.save()
            messages.success(request, "Password changed successfully. Please log in again.")
            return redirect('/myapp/login/')
        else:
            messages.error(request, "New password and confirm password do not match.")
            return redirect('/myapp/change_password/')
    else:
        messages.error(request, "Current password is incorrect.")
        return redirect('/myapp/change_password/')


def volunteer_view_assign_task(request):
    lid = request.POST['lid']
    ob = Donations_Assign_table.objects.filter(VOLUNTEER__LOGIN_id=lid)
    mdata = []
    for i in ob:
        mdata.append({
            'title': i.DONATE.REQUIREMENTS.title,
            'details': i.DONATE.REQUIREMENTS.details,
            'campname': i.DONATE.REQUIREMENTS.CAMP.campname,
            'place': i.DONATE.REQUIREMENTS.CAMP.place,
            'coordinatorname': i.DONATE.REQUIREMENTS.CAMP.COORDINATOR.name,
            'coordinatorphone': i.DONATE.REQUIREMENTS.CAMP.COORDINATOR.phone,
            'quantity': i.DONATE.quantity,
            'status': i.status,
            'date': str(i.date),
            'id': str(i.id)

        })
    print(mdata)
    return JsonResponse({"status": "ok", "data": mdata})


def update_assign_task(request):
    did = request.POST['did']

    aa=Donate_goods.objects.get(id=request.POST['did'])
    aa.status ='Collected'
    aa.save()
    obj = Donations_Assign_table.objects.get(id=did)
    obj.status = "Collected"
    obj.save()
    return JsonResponse({"status": "ok"})


def volunteerviewrequirements(request):
    lid = request.POST['lid']

    ob = Assign_table.objects.filter(
        VOLUNTEER__LOGIN_id=lid
    )

    mdata = []

    for i in ob:

        req = Requirements_table.objects.filter(
            CAMP_id=i.CAMP.id
        ).first()

        if req is None:
            continue

        mdata.append({
            'title': req.title,
            'needquantity': req.needquantity,
            'details': req.details,
            'campname': i.CAMP.campname,
            'place': i.CAMP.place,
            'coordinator': i.CAMP.COORDINATOR.name,
            'phone': i.CAMP.COORDINATOR.phone,
            'date': str(i.date),
            'id': str(i.id)
        })

    print(mdata)

    return JsonResponse({
        "status": "ok",
        "data": mdata
    })


def volunteer_add_daily_report(request):
    notes = request.POST['notes']
    lid = request.POST['lid']
    lob = Dialy_activity_report()
    lob.VOLUNTEER = Volunteer_table.objects.get(LOGIN__id=lid)
    lob.notes = notes
    lob.date = datetime.now().today()
    lob.save()
    return JsonResponse({'task': 'ok'})


def volunteerviewdailyreport(request):
    lid = request.POST['lid']
    ob = Dialy_activity_report.objects.filter(VOLUNTEER__LOGIN_id=lid)
    mdata = []
    for i in ob:
        mdata.append({

            'notes': i.notes,
            'date': str(i.date), 'id': str(i.id)

        })
    print(mdata)
    return JsonResponse({"status": "ok", "data": mdata})


def delete_daily_report(request):
    id = request.POST['id']
    Dialy_activity_report.objects.get(id=id).delete()
    return JsonResponse({'status': 'ok'})


from django.http import JsonResponse
from django.db.models import Q
from django.utils import timezone

from .models import Chat_table


# =========================================================
# SEND CHAT MESSAGE
# =========================================================

def User_sendchat(request):
    if request.method != "POST":
        return JsonResponse({
            "status": "error",
            "message": "POST method required"
        }, status=405)

    try:

        from_id = request.POST.get("from_id", "").strip()
        to_id = request.POST.get("to_id", "").strip()
        message = request.POST.get("message", "").strip()

        print("FROM ID :", from_id)
        print("TO ID   :", to_id)
        print("MESSAGE :", message)

        # =====================================================
        # VALIDATION
        # =====================================================

        if not from_id:
            return JsonResponse({
                "status": "error",
                "message": "Sender ID is required"
            })

        if not to_id:
            return JsonResponse({
                "status": "error",
                "message": "Receiver ID is required"
            })

        if not message:
            return JsonResponse({
                "status": "error",
                "message": "Message cannot be empty"
            })

        # =====================================================
        # CREATE CHAT
        # =====================================================

        chat = Chat_table()

        chat.FROMID_id = from_id
        chat.TOID_id = to_id
        chat.message = message
        chat.date = timezone.now()

        chat.save()

        return JsonResponse({
            "status": "ok",
            "message": "Message sent successfully",
            "data": {
                "id": chat.id,
                "message": chat.message,
                "from": str(chat.FROMID_id),
                "to": str(chat.TOID_id),
                "date": chat.date.strftime("%Y-%m-%d %H:%M:%S"),
            }
        })

    except Exception as e:

        print("User_sendchat Error :", e)

        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=500)


# =========================================================
# VIEW CHAT
# =========================================================

def User_viewchat(request):
    if request.method != "POST":
        return JsonResponse({
            "status": "error",
            "message": "POST method required"
        }, status=405)

    try:

        from_id = request.POST.get("from_id", "").strip()
        to_id = request.POST.get("to_id", "").strip()

        print("CHAT FROM :", from_id)
        print("CHAT TO   :", to_id)

        # =====================================================
        # VALIDATION
        # =====================================================

        if not from_id:
            return JsonResponse({
                "status": "error",
                "message": "Sender ID is required"
            })

        if not to_id:
            return JsonResponse({
                "status": "error",
                "message": "Receiver ID is required"
            })

        # =====================================================
        # GET BOTH SENT AND RECEIVED MESSAGES
        # =====================================================

        res = Chat_table.objects.filter(

            Q(
                FROMID_id=from_id,
                TOID_id=to_id
            )

            |

            Q(
                FROMID_id=to_id,
                TOID_id=from_id
            )

        ).order_by(
            "date",
            "id"
        )

        # =====================================================
        # RESPONSE DATA
        # =====================================================

        chat_list = []

        for item in res:
            chat_list.append({

                "id":
                    item.id,

                "message":
                    item.message,

                "from":
                    str(item.FROMID_id),

                "to":
                    str(item.TOID_id),

                "date":
                    item.date.strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
            })

        return JsonResponse({

            "status": "ok",

            "data":
                chat_list
        })

    except Exception as e:

        print("User_viewchat Error :", e)

        return JsonResponse({

            "status": "error",

            "message":
                str(e)

        }, status=500)


def volunteerviewert(request):
    ob = ERT_table.objects.all()
    mdata = []
    for i in ob:
        mdata.append({
            'name': i.name,
            'phone': str(i.phone),
            'photo': request.build_absolute_uri(i.photo.url) if i.photo else "",
            'place': str(i.place),
            'id': str(i.LOGIN.id)

        })
    print(mdata)
    return JsonResponse({"status": "ok", "data": mdata})


def coordinator_view_daily_report(request, id):
    vol = Dialy_activity_report.objects.filter(VOLUNTEER_id=id)
    return render(request, 'camp coordinator/view volunteer daily report.html', {'data': vol})


def ertviewvolunteer(request):
    ob = Volunteer_table.objects.filter(status="Verified")
    mdata = []
    for i in ob:
        mdata.append({
            'name': i.name,
            'phone': str(i.phone),
            'email': str(i.email),
            'photo': request.build_absolute_uri(i.photo.url) if i.photo else "",
            'place': str(i.place),
            'id': str(i.LOGIN.id)

        })
    print(mdata)
    return JsonResponse({"status": "ok", "data": mdata})


def ertviewcampcoordinator(request):
    ob = Camp_coordinator_table.objects.filter(status="Verified")
    mdata = []
    for i in ob:
        mdata.append({
            'name': i.name,
            'phone': str(i.phone),
            'email': str(i.email),
            'photo': request.build_absolute_uri(i.photo.url) if i.photo else "",
            'place': str(i.place),
            'id': str(i.LOGIN.id)

        })
    print(mdata)
    return JsonResponse({"status": "ok", "data": mdata})


def ertviewvictim(request):
    ob = Disaster_victim_table.objects.all()
    mdata = []
    for i in ob:
        mdata.append({
            'name': i.name,
            'phone': str(i.phone),
            'email': str(i.email),
            'gender': str(i.gender),
            'district': str(i.district),
            'disasterdetails': str(i.disasterdetails),
            'latitude': str(i.latitude),
            'longitude': str(i.longitude),
            'dob': str(i.dob),
            'photo': request.build_absolute_uri(i.photo.url) if i.photo else "",
            'place': str(i.place),
            'id': str(i.id),

        })
    print(mdata)
    return JsonResponse({"status": "ok", "data": mdata})


from django.shortcuts import render
from .models import Requirements_table, User_table


def camp_coordinator_view_blockchain(request):
    donation=Donate_goods.objects.filter(REQUIREMENTS__CAMP__COORDINATOR__LOGIN_id=request.user.id)

    return render(
        request,
        'camp coordinator/view donations.html',
        {
            'data': donation
        }
    )


def admin_coordinator_view_blockchain(request):
    contract_list = []

    try:

        # =====================================================
        # GET ALL DONATION IDS FROM BLOCKCHAIN
        # =====================================================

        blockchain_ids = contract.functions.getAllDonationsIds().call()

        for bc_id in blockchain_ids:

            try:

                # =================================================
                # GET DONATION DATA FROM BLOCKCHAIN
                # =================================================

                user_id, request_id, amount, date, donation_hash = (
                    contract.functions.getMark(bc_id).call()
                )

                # Ignore invalid records
                if user_id == 0 or request_id == 0:
                    continue

                # =================================================
                # FIND REQUIREMENT
                # =================================================

                req = Requirements_table.objects.select_related(
                    'CAMP',
                    'CAMP__COORDINATOR'
                ).filter(
                    id=request_id
                ).first()

                # Requirement does not exist
                if not req:
                    print(
                        "Requirement not found:",
                        request_id
                    )
                    continue

                # =================================================
                # FIND DONOR
                # =================================================

                donor = User_table.objects.filter(
                    LOGIN_id=user_id
                ).first()

                # =================================================
                # CAMP COORDINATOR
                # =================================================

                coordinator = req.CAMP.COORDINATOR

                # =================================================
                # ADD DONATION
                # =================================================

                contract_list.append({

                    # Blockchain information
                    'bc_id': str(bc_id),

                    'user_id': str(user_id),

                    'request_id': str(request_id),

                    'amount': str(amount),

                    'date': str(date),

                    'hash': str(donation_hash),

                    # Requirement information
                    'title': req.title,

                    'needquantity': req.needquantity,

                    'details': req.details,

                    # Camp information
                    'campname': req.CAMP.campname,

                    'place': req.CAMP.place,

                    'district': req.CAMP.district,

                    # Coordinator information
                    'coordinator_name': (
                        coordinator.name
                        if coordinator
                        else 'Unknown'
                    ),

                    'coordinator_phone': (
                        str(coordinator.phone)
                        if coordinator
                        else '-'
                    ),

                    # Donor information
                    'donor_name': (
                        donor.name
                        if donor
                        else 'Unknown Donor'
                    ),

                    'donor_email': (
                        donor.email
                        if donor
                        else '-'
                    ),

                    'donor_phone': (
                        str(donor.phone)
                        if donor
                        else '-'
                    ),
                })

            except Exception as e:

                print(
                    "Skipped blockchain donation",
                    bc_id,
                    ":",
                    e
                )

    except Exception as e:

        print(
            "Blockchain Error:",
            e
        )

    # =========================================================
    # LATEST DONATIONS FIRST
    # =========================================================

    contract_list.reverse()

    print(
        "Total Donations:",
        len(contract_list)
    )

    print(
        contract_list
    )

    return render(
        request,
        'admin/view donation transactions.html',
        {
            'data': contract_list
        }
    )


def admin_view_goods_distribution(request):
    donations = Donations_Assign_table.objects.select_related(
        'DONATE',
        'DONATE__REQUIREMENTS',
        'DONATE__REQUIREMENTS__CAMP',
        'DONATE__REQUIREMENTS__CAMP__COORDINATOR',
        'VOLUNTEER'
    ).order_by('-date')

    data = []

    for item in donations:
        donate = item.DONATE
        req = donate.REQUIREMENTS
        camp = req.CAMP
        volunteer = item.VOLUNTEER

        data.append({
            'id': item.id,
            'date': item.date,
            'title': req.title,
            'needquantity': req.needquantity,
            'details': req.details,
            'quantity': donate.quantity,
            'donation_date': donate.date,
            'donation_status': donate.status,
            'campname': camp.campname,
            'place': camp.place,
            'district': camp.district,
            'coordinator': camp.COORDINATOR.name,
            'coordinator_phone': camp.COORDINATOR.phone,
            'volunteer': volunteer.name,
            'volunteer_phone': volunteer.phone,
            'distribution_status': item.status,
            'distribution_date': item.date,
        })

    return render(
        request,
        'admin/view goods distribution reports.html',
        {'data': data}
    )


#####



from django.shortcuts import render, get_object_or_404
from django.db.models import Sum, Count
from django.utils import timezone

from .models import (
    Relief_camp_table,
    Disaster_victim_table,
    Requirements_table,
    Donate_goods,
    Assign_table,
    Donations_Assign_table,
    Dialy_activity_report,
)


def coordinator_generate_camp_report(request, id):
    """
    Generate a complete report for a particular relief camp.
    """

    # ---------------------------------------------------------
    # CAMP
    # ---------------------------------------------------------

    camp = get_object_or_404(
        Relief_camp_table,
        id=id,
        COORDINATOR__LOGIN_id=request.user.id
    )

    # ---------------------------------------------------------
    # VICTIMS
    # ---------------------------------------------------------

    victims = Disaster_victim_table.objects.filter(
        COORDINATOR=camp.COORDINATOR
    )

    victim_count = victims.count()

    # ---------------------------------------------------------
    # REQUIREMENTS
    # ---------------------------------------------------------

    requirements = Requirements_table.objects.filter(
        CAMP=camp
    )

    requirement_count = requirements.count()

    # ---------------------------------------------------------
    # GOODS DONATIONS
    # ---------------------------------------------------------

    goods_donations = Donate_goods.objects.filter(
        REQUIREMENTS__CAMP=camp
    ).order_by('-date')

    donation_count = goods_donations.count()

    # ---------------------------------------------------------
    # GOODS DONATION QUANTITY
    # ---------------------------------------------------------

    total_donation_quantity = 0

    for donation in goods_donations:
        try:
            total_donation_quantity += float(
                donation.quantity
            )
        except (ValueError, TypeError):
            pass

    # ---------------------------------------------------------
    # ASSIGNED VOLUNTEERS
    # ---------------------------------------------------------

    volunteer_assignments = Assign_table.objects.filter(
        CAMP=camp
    ).select_related(
        'VOLUNTEER'
    )

    volunteer_count = volunteer_assignments.values(
        'VOLUNTEER'
    ).distinct().count()

    # ---------------------------------------------------------
    # DONATION DELIVERY ASSIGNMENTS
    # ---------------------------------------------------------

    donation_tasks = Donations_Assign_table.objects.filter(
        DONATE__REQUIREMENTS__CAMP=camp
    ).select_related(
        'DONATE',
        'VOLUNTEER'
    ).order_by('-date')

    completed_tasks = donation_tasks.filter(
        status__iexact='Collected'
    ).count()

    pending_tasks = donation_tasks.exclude(
        status__iexact='Collected'
    ).count()

    # ---------------------------------------------------------
    # DAILY VOLUNTEER REPORTS
    # ---------------------------------------------------------

    volunteer_reports = Dialy_activity_report.objects.filter(
        VOLUNTEER__in=volunteer_assignments.values('VOLUNTEER')
    ).select_related(
        'VOLUNTEER'
    ).order_by('-date')

    daily_report_count = volunteer_reports.count()

    # ---------------------------------------------------------
    # RECENT REQUIREMENTS
    # ---------------------------------------------------------

    recent_requirements = requirements.order_by(
        '-date'
    )[:10]

    # ---------------------------------------------------------
    # RECENT DONATIONS
    # ---------------------------------------------------------

    recent_donations = goods_donations[:10]

    # ---------------------------------------------------------
    # CONTEXT
    # ---------------------------------------------------------

    context = {
        'camp': camp,

        'victims': victims,
        'victim_count': victim_count,

        'requirements': requirements,
        'requirement_count': requirement_count,
        'recent_requirements': recent_requirements,

        'goods_donations': goods_donations,
        'recent_donations': recent_donations,
        'donation_count': donation_count,
        'total_donation_quantity': total_donation_quantity,

        'volunteer_assignments': volunteer_assignments,
        'volunteer_count': volunteer_count,

        'donation_tasks': donation_tasks,
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,

        'volunteer_reports': volunteer_reports,
        'daily_report_count': daily_report_count,

        'generated_date': timezone.now().date(),
    }

    return render(
        request,
        'camp coordinator/camp report.html',
        context
    )


######emergency sos


import json

from django.http import JsonResponse

from .models import (
    User_table,
    EmergencySOS,
    Emergency_Notification_table
)


def emergency_sos(request):
    if request.method != "POST":
        return JsonResponse({
            "status": "error",
            "message": "Only POST method is allowed"
        })

    try:

        # =====================================================
        # READ JSON DATA
        # =====================================================

        data = json.loads(request.body)

        lid = data.get("lid")
        latitude = data.get("latitude")
        longitude = data.get("longitude")
        sos_status = data.get("status", "Emergency")

        # =====================================================
        # VALIDATE LOCATION
        # =====================================================

        if latitude is None or longitude is None:
            return JsonResponse({
                "status": "error",
                "message": "Location is required"
            })

        # =====================================================
        # VALIDATE USER ID
        # =====================================================

        if lid is None or lid == "":
            return JsonResponse({
                "status": "error",
                "message": "User ID is required"
            })

        # =====================================================
        # CONVERT DATA TYPES
        # =====================================================

        try:

            lid = int(lid)
            latitude = float(latitude)
            longitude = float(longitude)

        except (ValueError, TypeError):

            return JsonResponse({
                "status": "error",
                "message": "Invalid SOS data"
            })

        # =====================================================
        # VALIDATE LATITUDE
        # =====================================================

        if latitude < -90 or latitude > 90:
            return JsonResponse({
                "status": "error",
                "message": "Invalid latitude"
            })

        # =====================================================
        # VALIDATE LONGITUDE
        # =====================================================

        if longitude < -180 or longitude > 180:
            return JsonResponse({
                "status": "error",
                "message": "Invalid longitude"
            })

        # =====================================================
        # GET USER
        # =====================================================

        try:

            user = User_table.objects.get(
                LOGIN_id=lid
            )

        except User_table.DoesNotExist:

            return JsonResponse({
                "status": "error",
                "message": "User not found"
            })

        # =====================================================
        # SAVE EMERGENCY SOS
        # =====================================================

        sos = EmergencySOS.objects.create(

            USER=user,

            latitude=latitude,

            longitude=longitude,

            status=sos_status
        )

        # =====================================================
        # CREATE EMERGENCY NOTIFICATION
        # =====================================================

        notification_message = (
            "Emergency SOS received. "
            "Location: Latitude "
            + str(latitude)
            + ", Longitude "
            + str(longitude)
        )

        notification = Emergency_Notification_table.objects.create(

            USER=user,

            notification=notification_message,

            status="unread"
        )

        # =====================================================
        # SUCCESS RESPONSE
        # =====================================================

        return JsonResponse({

            "status": "ok",

            "message": "SOS alert sent successfully",

            "sos_id": sos.id,

            "notification_id": notification.id,

            "latitude": sos.latitude,

            "longitude": sos.longitude,

            "emergency_status": sos.status,

            "notification_status": notification.status
        })


    # =========================================================
    # INVALID JSON
    # =========================================================

    except json.JSONDecodeError:

        return JsonResponse({

            "status": "error",

            "message": "Invalid JSON data"
        })


    # =========================================================
    # OTHER ERROR
    # =========================================================

    except Exception as e:

        print("SOS ERROR:", e)

        return JsonResponse({

            "status": "error",

            "message": "Unable to process SOS request"
        })


def view_emergency_sos(request):
    sos = EmergencySOS.objects.select_related('USER').all().order_by('-id')

    return render(
        request,
        'admin/emergency_sos.html',
        {
            'sos': sos
        }
    )


# ============================================================
# ERT VIEW EMERGENCY NOTIFICATION
# ============================================================



# ============================================================
# CALCULATE DISTANCE BETWEEN TWO LOCATIONS
# ============================================================
from math import radians, sin, cos, sqrt, atan2


def calculate_distance(lat1, lon1, lat2, lon2):
    # Earth radius in kilometres
    R = 6371.0

    lat1 = radians(float(lat1))
    lon1 = radians(float(lon1))

    lat2 = radians(float(lat2))
    lon2 = radians(float(lon2))

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        sin(dlat / 2) ** 2
        +
        cos(lat1)
        * cos(lat2)
        * sin(dlon / 2) ** 2
    )

    c = 2 * atan2(
        sqrt(a),
        sqrt(1 - a)
    )

    distance = R * c

    return distance


def ert_view_emergency_noti(request):
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "POST request required"})
    # ========================================================
    # GET DATA FROM FLUTTER
    # ========================================================
    lid = request.POST.get('lid')
    nid = request.POST.get('nid', '0')
    print("----------------------------------------")
    print("ERT EMERGENCY NOTIFICATION")
    print("ERT LOGIN ID:", lid)
    print("LAST SOS ID:", nid)
    # ========================================================
    # VALIDATE LOGIN ID
    # ========================================================
    if not lid:
        return JsonResponse({"status": "error", "message": "Login ID missing"})
    # ========================================================
    # CONVERT NID TO INTEGER
    # ========================================================
    try:
        nid = int(nid)

    except:

        nid = 0
    # ========================================================
    # GET ERT USER
    # ========================================================
    try:
        ert_user = User.objects.get(
            id=lid
        )

    except User.DoesNotExist:
        return JsonResponse({"status": "error", "message": "ERT user not found"})

    # ========================================================
    # GET LATEST ERT LOCATION
    # ========================================================

    ert_location = Location.objects.filter(
        LOGIN=ert_user
    ).order_by('-id').first()
    if not ert_location:
        print("ERT LOCATION NOT FOUND")
        return JsonResponse({
            "status": "no",
            "message": "ERT location not available"
        })

    # ========================================================
    # ERT CURRENT LOCATION
    # ========================================================

    ert_lat = ert_location.latitude
    ert_lon = ert_location.longitude

    print("ERT LATITUDE:", ert_lat)
    print("ERT LONGITUDE:", ert_lon)

    # ========================================================
    # TODAY'S EMERGENCY SOS
    # ========================================================

    today = datetime.now().date()

    sos_list = EmergencySOS.objects.filter(
        date=today,
        id__gt=nid,
        # status="Emergency"
    ).order_by('id')

    print("SOS COUNT:", sos_list.count())

    # ========================================================
    # CHECK EVERY SOS
    # ========================================================

    for sos in sos_list:

        print("----------------------------------------")

        print("SOS ID:", sos.id)

        print(
            "SOS LOCATION:",
            sos.latitude,
            sos.longitude
        )

        # ====================================================
        # CALCULATE DISTANCE
        # ====================================================

        distance = calculate_distance(
            ert_lat,
            ert_lon,
            sos.latitude,
            sos.longitude
        )

        print(
            "DISTANCE:",
            distance,
            "KM"
        )

        # ====================================================
        # 5 KM RADIUS
        # ====================================================

        if distance <= 5:
            print("MATCH FOUND")
            print("EMERGENCY IS WITHIN 5 KM")

            return JsonResponse({

                "status": "ok",

                "nid": sos.id,

                "message":
                    "Emergency At Your Location",

                "latitude":
                    sos.latitude,

                "longitude":
                    sos.longitude,

                "distance":
                    round(distance, 2)
            })

    # ========================================================
    # NO NEARBY SOS
    # ========================================================

    print("NO NEARBY EMERGENCY")

    return JsonResponse({
        "status": "no"
    })




    # ============================================================


# GET ALL NEARBY EMERGENCIES
# ============================================================

def ert_nearby_emergencies(request):
    if request.method != "POST":
        return JsonResponse({
            "status": "error",
            "message": "POST request required"
        })

    lid = request.POST.get("lid")

    if not lid:
        return JsonResponse({
            "status": "error",
            "message": "Login ID missing"
        })

    # ========================================================
    # GET ERT
    # ========================================================

    try:

        ert_user = User.objects.get(
            id=int(lid)
        )

    except User.DoesNotExist:

        return JsonResponse({
            "status": "error",
            "message": "User not found"
        })

    # ========================================================
    # GET ERT LOCATION
    # ========================================================

    ert_location = Location.objects.filter(
        LOGIN=ert_user
    ).order_by("-id").first()

    if not ert_location:
        return JsonResponse({
            "status": "error",
            "message": "ERT location not available"
        })

    ert_lat = ert_location.latitude
    ert_lon = ert_location.longitude

    # ========================================================
    # TODAY'S ACTIVE SOS
    # ========================================================

    today = datetime.now().date()

    sos_list = EmergencySOS.objects.filter(
        date=today,
        status="Emergency"
    ).order_by("-id")

    emergency_list = []

    # ========================================================
    # FIND SOS WITHIN 5 KM
    # ========================================================

    for sos in sos_list:

        distance = calculate_distance(
            ert_lat,
            ert_lon,
            sos.latitude,
            sos.longitude
        )

        if distance <= 15:

            username = ""

            if sos.USER:
                username = sos.USER.name

            emergency_list.append({

                "id":
                    sos.id,

                "username":
                    username,

                "latitude":
                    sos.latitude,

                "longitude":
                    sos.longitude,

                "distance":
                    round(distance, 2),

                "date":
                    str(sos.date),

                "time":
                    str(sos.time),

                "message":
                    "Emergency SOS"

            })

    return JsonResponse({

        "status": "ok",

        "ert_latitude":
            ert_lat,

        "ert_longitude":
            ert_lon,

        "emergencies":
            emergency_list

    })




    #################=======================================================================


import json
import pickle
import requests
from datetime import date

from django.shortcuts import render
from django.http import JsonResponse

# from .sample import getmaindata
from .river import get_rivers_near_location
from .models import Prediction, Notification_table

# ============================================================
# WEATHER API
# ============================================================

API_KEY = (
    "2b4e8c141af04762ac56c790177e7e46"
)

# ============================================================
# KNN MODEL
# ============================================================

MODEL_PATH = (
    r"C:\Users\GAYATHRI\PycharmProjects\geonexus"
    r"C:\Users\GAYATHRI\PycharmProjects\geonexus\myapp\knn_model.pkl"
)

# ============================================================
# SOIL TYPES
#
# IMPORTANT:
# These values MUST match the encoding used
# during KNN training.
# ============================================================

SOIL_TYPES = [

    "Fluvisols",

    "Andosols",

    "Arenosols",

    "Chernozem",

    "Gleysols",

    "Histosols",

    "Kastanozems",

    "Luvisols",

    "Nitisols",

    "Regosols",

    "Vertisols",

    "Solonchaks",

    "Podzols",

    "Alisols",

    "Cambisols",

    "Calcisols",

    "Phaeozems",

    "Acrisols",

    "Plinthosols",

    "Clay",

    "Laterite Soil"

]

# ============================================================
# UNKNOWN SOIL FALLBACK
# ============================================================

DEFAULT_SOIL = "Laterite Soil"


# ============================================================
# MAP START
# ============================================================

def map_start(request):
    return render(
        request,
        "admin/map_start.html"
    )


# ============================================================
# REVERSE GEOCODE (for district, used in Notification_table)
# ============================================================

def reverse_geocode(lat, lon):
    """
    Returns (place, district) using Nominatim reverse geocoding.
    Falls back to empty strings on any failure - this must
    NEVER break the prediction flow.
    """

    try:

        url = "https://nominatim.openstreetmap.org/reverse"

        params = {

            "format": "json",

            "lat": lat,

            "lon": lon,

            "zoom": 10,

            "addressdetails": 1

        }

        response = requests.get(

            url,

            params=params,

            headers={"User-Agent": "DisasterPredictionSystem/1.0"},

            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        address = data.get("address", {})

        place = (

            address.get("city")

            or address.get("town")

            or address.get("village")

            or address.get("suburb")

            or ""

        )

        district = (

            address.get("state_district")

            or address.get("county")

            or address.get("state")

            or ""

        )

        return place, district

    except Exception as e:

        print("Reverse geocode error:", str(e))

        return "", ""


# ============================================================
# WEATHER
# ============================================================

def get_weather(lat, lon):
    url = (
        "https://api.weatherbit.io/v2.0/current"
    )

    params = {

        "lat": lat,

        "lon": lon,

        "key": API_KEY

    }

    try:

        response = requests.get(

            url,

            params=params,

            timeout=20
        )

        response.raise_for_status()

        data = response.json()

        print(
            "\nWEATHER DATA:"
        )

        print(
            data
        )

        if not data.get(
                "data"
        ):
            print(
                "Weather API returned no data"
            )

            return None

        return data

    except requests.exceptions.RequestException as e:

        print(
            "Weather API error:",
            str(e)
        )

        return None

    except ValueError as e:

        print(
            "Weather JSON error:",
            str(e)
        )

        return None


# ============================================================
# SAVE PREDICTION + NOTIFICATION
# ============================================================

def save_prediction_and_notification(

        lat,
        lon,
        status,
        soil_type,
        river_distance_km,
        slope_angle,
        elevation,
        rainfall,
        humidity,
        temperature,
        weather_data,
        city_name

):
    """
    Saves the Prediction row always.
    Saves a Notification_table row only when status == "Disaster".

    Wrapped so that a DB / geocoding failure here never breaks
    the response already computed for the user.
    """

    today = date.today()

    # ========================================================
    # weather_data field is CharField(max_length=150) in the
    # model, so it CANNOT hold the full weather JSON. It is
    # serialized and hard-truncated here so save() does not
    # raise. Recommended fix: change the model field to
    # TextField if you need the full weather payload stored.
    # ========================================================

    try:

        weather_str = json.dumps(weather_data)[:150]

    except Exception:

        weather_str = str(weather_data)[:150]

    try:

        Prediction.objects.create(

            date=today,

            value=status,

            risk=status,

            river=str(river_distance_km),

            soil_type=str(soil_type),

            slope=str(slope_angle),

            altitude=str(elevation),

            rainfall=str(rainfall),

            humidity=str(humidity),

            temperature=str(temperature),

            weather_data=weather_str,

            latitude=lat,

            longitude=lon

        )

        print("Prediction saved to DB.")

    except Exception as e:

        print("Failed to save Prediction:", str(e))

    # ========================================================
    # NOTIFICATION - only for Disaster
    # ========================================================

    if status == "Disaster":

        try:

            place, district = reverse_geocode(lat, lon)

            if not place:
                place = city_name or "Unknown location"

            Notification_table.objects.create(

                title=f"Disaster risk detected near {place}",

                date=today,

                latitude=lat,

                longitude=lon,

                place=place,

                district=district

            )

            print("Notification saved to DB.")

        except Exception as e:

            print("Failed to save Notification:", str(e))


# ============================================================
# GET PREDICTION
# ============================================================

def get_predict(request):
    if request.method != "POST":
        return JsonResponse(
            {
                "error":
                    "POST request required"
            },
            status=400
        )

    try:

        # ====================================================
        # LATITUDE
        # ====================================================

        lat_value = request.POST.get(
            "lat"
        )

        # ====================================================
        # LONGITUDE
        # ====================================================

        lon_value = request.POST.get(
            "lon"
        )

        if not lat_value or not lon_value:
            return render(

                request,

                "admin/result.html",

                {

                    "status":
                        "error",

                    "val":
                        "Invalid latitude or longitude"

                }
            )

        lat = float(
            lat_value
        )

        lon = float(
            lon_value
        )

        print(
            "\n======================================"
        )

        print(
            "DISASTER PREDICTION"
        )

        print(
            "======================================"
        )

        print(
            "Latitude :",
            lat
        )

        print(
            "Longitude:",
            lon
        )

        # ====================================================
        # ENVIRONMENTAL DATA
        # ====================================================

        elevation, soil_type, slope_angle = getmaindata(

            lat,

            lon
        )

        # If elevation API failed
        if elevation is None:
            elevation = 0.0

        print(
            "\nENVIRONMENTAL DATA"
        )

        print(
            "Elevation:",
            elevation
        )

        print(
            "Soil:",
            soil_type
        )

        print(
            "Slope:",
            slope_angle
        )

        # ====================================================
        # RIVER
        # ====================================================

        river_data = get_rivers_near_location(

            lat,

            lon
        )

        # Default = 10 km
        river_distance_km = 10.0

        if (

                    isinstance(
                        river_data,
                        list
                    )

                and

                        len(river_data) > 0

        ):

            first_river = river_data[0]

            distance = first_river.get(
                "distance_km"
            )

            if isinstance(
                    distance,
                    (int, float)
            ):
                river_distance_km = float(
                    distance
                )

        else:

            print(
                "River API unavailable."
            )

            print(
                "Using fallback:",
                river_distance_km,
                "km"
            )

        print(
            "River Distance:",
            river_distance_km,
            "km"
        )

        # ====================================================
        # WEATHER
        # ====================================================

        weather_data = get_weather(

            lat,

            lon
        )

        if weather_data is None:
            return render(

                request,

                "admin/result.html",

                {

                    "status":
                        "error",

                    "val":
                        "Weather data unavailable",

                    "st":
                        soil_type,

                    "river":
                        river_distance_km,

                    "altitude":
                        elevation,

                    "rainfall":
                        0,

                    "city_name":
                        ""

                }
            )

        weather = weather_data[
            "data"
        ][0]

        # ====================================================
        # WEATHER VALUES
        # ====================================================

        rainfall = float(

            weather.get(
                "precip",
                0
            )
            or 0
        )

        humidity = float(

            weather.get(
                "rh",
                0
            )
            or 0
        )

        temperature = float(

            weather.get(
                "temp",
                0
            )
            or 0
        )

        city_name = weather.get(
            "city_name",
            ""
        )

        # ====================================================
        # SOIL
        # ====================================================

        soil_type = str(
            soil_type
        ).strip()

        # ====================================================
        # FIX UNKNOWN
        # ====================================================

        if (

                    not soil_type

                or

                        soil_type.lower() == "unknown"

        ):
            print(
                "\nSoil API did not return soil type."
            )

            print(
                "Using fallback soil:",
                DEFAULT_SOIL
            )

            soil_type = DEFAULT_SOIL

        # ====================================================
        # CHECK SOIL EXISTS
        # ====================================================

        if soil_type not in SOIL_TYPES:
            print(
                "\nWARNING:"
            )

            print(
                "API Soil:",
                soil_type
            )

            print(
                "Not present in SOIL_TYPES."
            )

            print(
                "Using:",
                DEFAULT_SOIL
            )

            soil_type = DEFAULT_SOIL

        # ====================================================
        # ENCODE SOIL
        # ====================================================

        soil_encoded = SOIL_TYPES.index(
            soil_type
        )

        # ====================================================
        # LOAD KNN
        # ====================================================

        with open(
                MODEL_PATH,
                "rb"
        ) as file:

            knn = pickle.load(
                file
            )

        # ====================================================
        # FINAL ROW
        #
        # 1  latitude
        # 2  longitude
        # 3  elevation
        # 4  river distance
        # 5  slope
        # 6  rainfall
        # 7  soil
        # 8  humidity
        # 9  temperature
        # ====================================================

        row = [

            float(lat),

            float(lon),

            float(elevation),

            float(river_distance_km),

            float(slope_angle),

            float(rainfall),

            int(soil_encoded),

            float(humidity),

            float(temperature)

        ]

        # ====================================================
        # DEBUG
        # ====================================================

        print(
            "\n======================================"
        )

        print(
            "FINAL ML INPUT"
        )

        print(
            "======================================"
        )

        print(
            "Latitude       :",
            lat
        )

        print(
            "Longitude      :",
            lon
        )

        print(
            "Elevation      :",
            elevation
        )

        print(
            "River Distance :",
            river_distance_km
        )

        print(
            "Slope Angle    :",
            slope_angle
        )

        print(
            "Rainfall       :",
            rainfall
        )

        print(
            "Soil Type      :",
            soil_type
        )

        print(
            "Soil Encoded   :",
            soil_encoded
        )

        print(
            "Humidity       :",
            humidity
        )

        print(
            "Temperature    :",
            temperature
        )

        print(
            "FINAL ROW      :",
            row
        )

        print(
            "Model expects  :",
            knn.n_features_in_
        )

        print(
            "Actual features:",
            len(row)
        )

        # ====================================================
        # FEATURE COUNT
        # ====================================================

        if len(row) != knn.n_features_in_:
            raise ValueError(

                f"KNN model expects "
                f"{knn.n_features_in_} features, "
                f"but received "
                f"{len(row)}."
            )

        # ====================================================
        # PREDICTION
        # ====================================================

        prediction = knn.predict(
            [row]
        )

        print(
            "\nMODEL PREDICTION:",
            prediction
        )

        prediction_value = int(
            prediction[0]
        )

        # ====================================================
        # RESULT
        # ====================================================

        if prediction_value == 0:

            status = "Non-Disaster"

        else:

            status = "Disaster"

        print(
            "FINAL RESULT:",
            status
        )

        # ====================================================
        # SAVE TO DB
        # Prediction is always saved.
        # Notification_table is saved only when status == "Disaster".
        # ====================================================

        save_prediction_and_notification(

            lat=lat,

            lon=lon,

            status=status,

            soil_type=soil_type,

            river_distance_km=river_distance_km,

            slope_angle=slope_angle,

            elevation=elevation,

            rainfall=rainfall,

            humidity=humidity,

            temperature=temperature,

            weather_data=weather_data,

            city_name=city_name

        )

        # ====================================================
        # RESULT PAGE
        # ====================================================

        return render(

            request,

            "admin/result.html",

            {

                "status":
                    "ok",

                "val":
                    status,

                "weather_data":
                    weather_data,

                "st":
                    soil_type,

                "river":
                    river_distance_km,

                "altitude":
                    elevation,

                "rainfall":
                    rainfall,

                "city_name":
                    city_name,

                "slope":
                    slope_angle,

                "temperature":
                    temperature,

                "humidity":
                    humidity

            }
        )

    # ========================================================
    # ERROR
    # ========================================================

    except Exception as e:

        print(
            "\n======================================"
        )

        print(
            "PREDICTION ERROR"
        )

        print(
            "======================================"
        )

        print(
            str(e)
        )

        return render(

            request,

            "admin/result.html",

            {

                "status":
                    "error",

                "val":
                    "Prediction failed",

                "error":
                    str(e)

            }
        )

        # ===========================================testing


from datetime import date
from django.shortcuts import render
from django.http import JsonResponse

from .models import Prediction, Notification_table


# ============================================================
# DUMMY DISASTER TEST
# ============================================================

def dummy_disaster_prediction(request):
    # ====================================================
    # DUMMY LOCATION
    # ====================================================

    latitude = float(
        request.POST.get("lat", "11.2577762")
    )

    longitude = float(
        request.POST.get("lon", "75.7844875")
    )

    # ====================================================
    # DUMMY ENVIRONMENT DATA
    # ====================================================

    rainfall = 145.5
    humidity = 94.0
    temperature = 26.0

    elevation = 35.0

    # Near river
    river_distance_km = 0.45

    # High slope
    slope_angle = 28.0

    soil_type = "Laterite Soil"

    # ====================================================
    # FORCE DISASTER FOR TESTING
    # ====================================================

    status = "Disaster"

    # ====================================================
    # LOCATION
    # ====================================================

    place = request.POST.get(
        "place",
        "Kozhikode"
    )

    district = request.POST.get(
        "district",
        "Kozhikode"
    )

    # ====================================================
    # WEATHER DATA
    # ====================================================

    weather_data = {
        "city_name": place,
        "rainfall": rainfall,
        "humidity": humidity,
        "temperature": temperature,
        "condition": "Heavy Rainfall"
    }

    # ====================================================
    # SAVE PREDICTION
    # ====================================================

    prediction_obj = Prediction.objects.create(

        date=date.today(),

        value="Disaster",

        risk="high",

        river=str(river_distance_km),

        soil_type=soil_type,

        slope=str(slope_angle),

        altitude=str(elevation),

        rainfall=str(rainfall),

        humidity=str(humidity),

        temperature=str(temperature),

        weather_data=str(weather_data)[:150],

        latitude=latitude,

        longitude=longitude
    )

    print("======================================")
    print("DUMMY DISASTER PREDICTION")
    print("======================================")
    print("Latitude       :", latitude)
    print("Longitude      :", longitude)
    print("Elevation      :", elevation)
    print("River Distance :", river_distance_km)
    print("Slope          :", slope_angle)
    print("Rainfall       :", rainfall)
    print("Soil           :", soil_type)
    print("Humidity       :", humidity)
    print("Temperature    :", temperature)
    print("Result         :", status)
    print("Prediction ID  :", prediction_obj.id)

    # ====================================================
    # SAVE NOTIFICATION
    # ====================================================

    notification_obj = None

    if status == "Disaster":
        notification_obj = Notification_table.objects.create(

            title=f"Disaster risk detected near {place}",

            date=date.today(),

            latitude=latitude,

            longitude=longitude,

            place=place,

            district=district
        )

        print("--------------------------------------")
        print("NOTIFICATION SAVED")
        print("--------------------------------------")
        print("Notification ID :", notification_obj.id)
        print("Title            :", notification_obj.title)
        print("Place            :", notification_obj.place)
        print("District         :", notification_obj.district)

    # ====================================================
    # RETURN RESULT
    # ====================================================

    return render(
        request,
        "admin/result.html",
        {
            "status": "ok",

            "val": status,

            "weather_data": weather_data,

            "st": soil_type,

            "river": river_distance_km,

            "altitude": elevation,

            "rainfall": rainfall,

            "city_name": place,

            "slope": slope_angle,

            "temperature": temperature,

            "humidity": humidity,

            "dummy": True,

            "notification_saved":
                notification_obj is not None
        }
    )


import math

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Notification_table, Location

# =========================================================
# True  -> every logged-in user gets every new alert
#          (location is NOT needed)
# False -> only users within ALERT_RADIUS_KM get the alert
# =========================================================
ALERT_ALL_LOGGED_IN_USERS = True
ALERT_RADIUS_KM = 10


def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2
         + math.cos(math.radians(lat1))
         * math.cos(math.radians(lat2))
         * math.sin(dlon / 2) ** 2)
    return R * 2 * math.asin(math.sqrt(a))


def get_user_location(lid):
    """Return (lat, lon) of the user's latest location, or None."""
    location = Location.objects.filter(LOGIN_id=lid).order_by('-id').first()
    if not location:
        return None
    try:
        return float(location.latitude), float(location.longitude)
    except (TypeError, ValueError):
        return None


def distance_to(user_loc, notification):
    """Distance in km between user and disaster, or None if unknown."""
    if not user_loc:
        return None
    try:
        return haversine_km(user_loc[0], user_loc[1],
                            float(notification.latitude),
                            float(notification.longitude))
    except (TypeError, ValueError):
        return None


def ok_response(notification, distance_km):
    return JsonResponse({
        "status": "ok",
        "nid": notification.id,
        "message": "There is a chance of a disaster occurring. Please be careful.",
        "title": notification.title,
        "latitude": notification.latitude,
        "longitude": notification.longitude,
        "place": notification.place,
        "district": notification.district,
        "distance": round(distance_km, 2) if distance_km is not None else "",
    })




    ##########################disaster notification


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.db import models
from datetime import datetime
import math


def calculate_distance_notify(lat1, lon1, lat2, lon2):
    """
    Calculate distance between two latitude/longitude points
    using Haversine formula.
    Returns distance in kilometers.
    """

    R = 6371.0  # Earth radius in KM

    lat1 = math.radians(float(lat1))
    lon1 = math.radians(float(lon1))
    lat2 = math.radians(float(lat2))
    lon2 = math.radians(float(lon2))

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


@csrf_exempt
def user_view_disaster_noti(request):
    try:

        if request.method != "POST":
            return JsonResponse({
                "status": "error",
                "message": "POST method required"
            })

        lid = request.POST.get('lid')

        if not lid:
            return JsonResponse({
                "status": "error",
                "message": "Login id missing"
            })

        try:
            user = User.objects.get(id=lid)
        except User.DoesNotExist:
            return JsonResponse({
                "status": "error",
                "message": "User not found"
            })

        location = Location.objects.filter(
            LOGIN=user
        ).order_by('-date', '-id').first()

        if not location:
            return JsonResponse({
                "status": "error",
                "message": "User location not available"
            })

        user_lat = float(location.latitude)
        user_lon = float(location.longitude)
        seen_ids = SeenNotification.objects.filter(LOGIN=user).values_list('NOTIFICATION_id', flat=True)
        today = datetime.now().date()
        notifications = Notification_table.objects.exclude(id__in=seen_ids)
        notification_list = []
        for notification in notifications:
            notification_lat = float(notification.latitude)
            notification_lon = float(notification.longitude)
            distance = calculate_distance_notify(
                user_lat,
                user_lon,
                notification_lat,
                notification_lon
            )
            if distance <= 10:
                seen = SeenNotification()
                seen.LOGIN = user
                seen.NOTIFICATION = notification
                seen.save()
                notification_list.append({
                    "id": notification.id,
                    "title": notification.title,
                    "date": str(notification.date),
                    "latitude": notification.latitude,
                    "longitude": notification.longitude,
                    "place": notification.place,
                    "district": notification.district,
                    "distance": round(distance, 2)
                })
        if len(notification_list) > 0:
            return JsonResponse({
                "status": "ok",
                "message": "Emergency Disaster Alert..",
                "notifications": notification_list
            })

        else:
            return JsonResponse({
                "status": "no",
                "message": "No nearby disaster notification",
                "notifications": []
            })

    except Exception as e:
        print("Disaster notification error:", str(e))
        return JsonResponse({
            "status": "error",
            "message": str(e)
        })


import json
from django.shortcuts import render
from .models import Prediction


def admin_view_ai_predictions(request):
    predictions = Prediction.objects.all().order_by('-date', '-id')
    map_data = [
        {
            'id': p.id,
            'lat': p.latitude,
            'lng': p.longitude,
            'river': p.river,
            'risk': p.risk,
            'value': p.value,
            'date': p.date.strftime('%Y-%m-%d'),
        }
        for p in predictions
    ]

    return render(
        request,
        'admin/view_ai_predictions.html',
        {
            'predictions': predictions,
            'map_data_json': json.dumps(map_data),
        }
    )


# ============================================================
# USER VIEW NEARBY DISASTER ALERT
# ============================================================





"""
Nearby disaster alerts feature.

Given the currently logged-in user's most recent saved Location,
find all Notification_table entries within a radius (in km) and
return them sorted by distance (closest first).

No GeoDjango/PostGIS needed — uses the Haversine formula on plain
FloatField lat/lon columns, with a bounding-box pre-filter so the
DB does most of the narrowing before Python computes exact distance.
"""

import math

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from .models import Location, Notification_table


def haversine(lat1, lon1, lat2, lon2):
    """Great-circle distance between two points, in kilometers."""
    R = 6371  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


################################
import math

from django.http import JsonResponse

from .models import Location, Notification_table


def calculate_distance2(lat1, lon1, lat2, lon2):
    """Haversine distance in kilometers."""
    R = 6371.0

    lat1, lon1, lat2, lon2 = map(math.radians, [float(lat1), float(lon1), float(lat2), float(lon2)])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def nearby_alerts(request):
    # Return JSON instead of a redirect when not logged in
    if not request.user.is_authenticated:
        return JsonResponse(
            {"status": "error", "message": "Login required", "data": []},
            status=401
        )

    MAX_RADIUS_KM = 10

    # Latest location of this user
    user_location = Location.objects.filter(
        LOGIN=request.user
    ).order_by('-date', '-id').first()

    if not user_location:
        return JsonResponse({
            "status": "error",
            "message": "User location not available",
            "data": []
        })

    try:
        user_lat = float(user_location.latitude)
        user_lon = float(user_location.longitude)
    except (TypeError, ValueError):
        return JsonResponse({
            "status": "error",
            "message": "Invalid user location",
            "data": []
        })

    print("User location:", user_lat, user_lon, flush=True)

    nearby = []

    for alert in Notification_table.objects.all():
        try:
            alert_lat = float(alert.latitude)
            alert_lon = float(alert.longitude)
        except (TypeError, ValueError):
            continue

        distance = calculate_distance2(user_lat, user_lon, alert_lat, alert_lon)

        print(f"Alert {alert.id}: {distance:.2f} km", flush=True)

        if distance <= MAX_RADIUS_KM:
            nearby.append({
                "id": alert.id,
                "title": alert.title,
                "date": alert.date.strftime("%Y-%m-%d") if alert.date else "",
                "place": alert.place,
                "district": alert.district,
                "latitude": alert_lat,
                "longitude": alert_lon,
                "distance": round(distance, 2),
            })

    # Nearest first
    nearby.sort(key=lambda x: x["distance"])

    return JsonResponse({
        "status": "success",
        "message": "Nearby disaster alerts found" if nearby else "No disaster alert within 10 km",
        "radius": MAX_RADIUS_KM,
        "user_location": {"latitude": user_lat, "longitude": user_lon},
        "count": len(nearby),
        "data": nearby
    })


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


# from .models import Prediction   # <- keep your own import


def _to_float(value):
    """Convert DB value (str / Decimal / float) to float, or None."""
    try:
        if value is None:
            return None
        text = str(value).strip()
        if text == "":
            return None
        return float(text)
    except (ValueError, TypeError):
        return None


@csrf_exempt
def ert_view_disaster_predictions(request):
    try:
        predictions = Prediction.objects.filter(
            risk__icontains="high"
        ).order_by('-date')

        data = []

        for p in predictions:

            lat = _to_float(p.latitude)
            lng = _to_float(p.longitude)

            # skip rows that have no usable coordinates
            if lat is None or lng is None:
                continue

            data.append({
                "id": p.id,
                "date": p.date.strftime("%Y-%m-%d") if p.date else "",

                "value": p.value,
                "risk": p.risk,
                "river": p.river,
                "soil_type": p.soil_type,
                "slope": p.slope,
                "altitude": p.altitude,
                "rainfall": p.rainfall,
                "humidity": p.humidity,
                "temperature": p.temperature,
                "weather_data": p.weather_data,

                # always numbers, never strings/Decimal
                "latitude": lat,
                "longitude": lng,
            })

        print("HIGH RISK ROWS SENT:", len(data))

        return JsonResponse({
            "status": "ok",
            "predictions": data
        })

    except Exception as e:

        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=500)


######

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.db.models import Q
from math import radians, sin, cos, sqrt, atan2
import json


# ============================================================
# SAFE REQUEST DATA PARSER
# ============================================================

def get_request_data(request):
    """
    Safely extract POST data whether the client sends
    application/x-www-form-urlencoded, multipart/form-data,
    or a raw JSON body. Never raises on empty/invalid body.
    """

    # 1. Try normal form-encoded / multipart data first
    if request.POST:
        return request.POST

    # 2. Fall back to JSON body, but guard against empty/invalid body
    if request.body:
        try:
            return json.loads(request.body.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return {}

    # 3. Nothing usable
    return {}


# ============================================================
# DISTANCE CALCULATION
# ============================================================

def calculate_distance3(lat1, lon1, lat2, lon2):
    """
    Calculate distance between two latitude/longitude points.
    Returns distance in kilometers.
    """

    earth_radius = 6371.0

    lat1 = radians(float(lat1))
    lon1 = radians(float(lon1))

    lat2 = radians(float(lat2))
    lon2 = radians(float(lon2))

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        sin(dlat / 2) ** 2
        + cos(lat1)
        * cos(lat2)
        * sin(dlon / 2) ** 2
    )

    c = 2 * atan2(
        sqrt(a),
        sqrt(1 - a)
    )

    return earth_radius * c


@csrf_exempt
def user_send_alert(request):
    if request.method != "POST":
        return JsonResponse({
            "status": "error",
            "message": "POST method required"
        })

    try:

        # Works whether Flutter sends form-encoded OR JSON body
        data = get_request_data(request)

        lid = data.get("lid")
        lati = data.get("lati")
        longi = data.get("long")

        if not lid:
            return JsonResponse({
                "status": "error",
                "message": "User login ID required"
            })

        if lati is None or longi is None:
            return JsonResponse({
                "status": "error",
                "message": "Location required"
            })

        # ----------------------------------------------------
        # GET USER
        # ----------------------------------------------------

        try:
            login_user = User.objects.get(id=lid)
        except User.DoesNotExist:
            return JsonResponse({
                "status": "error",
                "message": "User not found"
            })

        try:
            user = User_table.objects.get(LOGIN=login_user)
        except User_table.DoesNotExist:
            return JsonResponse({
                "status": "error",
                "message": "User profile not found"
            })

        # ----------------------------------------------------
        # SAVE EMERGENCY SOS
        # ----------------------------------------------------

        sos = EmergencySOS.objects.create(
            USER=user,
            latitude=lati,
            longitude=longi,
            status="Emergency"
        )

        # ----------------------------------------------------
        # CREATE EMERGENCY NOTIFICATION
        # ----------------------------------------------------

        notification_text = (
            f"Emergency SOS from {user.name}. "
            f"Phone: {user.phone}. "
            f"Location: {lati}, {longi}"
        )

        Emergency_Notification_table.objects.create(
            USER=user,
            notification=notification_text,
            status="unread"
        )

        # ----------------------------------------------------
        # RESPONSE
        # ----------------------------------------------------

        return JsonResponse({
            "status": "ok",
            "message": "Emergency alert sent successfully",
            "sos_id": sos.id,
            "latitude": lati,
            "longitude": longi
        })

    except Exception as e:

        print("SEND ALERT ERROR:", e)

        return JsonResponse({
            "status": "error",
            "message": str(e)
        })


@csrf_exempt
def view_contacts(request):
    if request.method != "POST":
        return JsonResponse({
            "status": "error",
            "message": "POST method required"
        })

    try:

        # Works whether Flutter sends form-encoded OR JSON body
        data = get_request_data(request)

        # Flutter sends logged-in User id
        lid = data.get("lid")

        if not lid:
            return JsonResponse({
                "status": "error",
                "message": "Login ID required"
            })

        # ----------------------------------------------------
        # GET USER
        # ----------------------------------------------------

        try:
            login_user = User.objects.get(id=lid)
        except User.DoesNotExist:

            return JsonResponse({
                "status": "error",
                "message": "User not found"
            })

        # ----------------------------------------------------
        # GET USER TABLE
        # ----------------------------------------------------

        try:
            user = User_table.objects.get(
                LOGIN=login_user
            )
        except User_table.DoesNotExist:

            return JsonResponse({
                "status": "error",
                "message": "User profile not found"
            })

        # ----------------------------------------------------
        # GET USER LOCATION
        # ----------------------------------------------------

        user_location = (
            Location.objects
                .filter(LOGIN=login_user)
                .order_by("-id")
                .first()
        )

        if not user_location:
            return JsonResponse({
                "status": "error",
                "message": "User location not available"
            })

        user_latitude = user_location.latitude
        user_longitude = user_location.longitude

        # ----------------------------------------------------
        # SEARCH DISTANCE
        # ----------------------------------------------------

        # Change this value if required.
        # 10 means ERT within 10 km.
        SEARCH_RADIUS_KM = 10

        result = []

        # ----------------------------------------------------
        # GET ALL ERT
        # ----------------------------------------------------

        ert_list = ERT_table.objects.select_related(
            "LOGIN"
        ).all()

        for ert in ert_list:

            # ------------------------------------------------
            # GET ERT LOCATION
            # ------------------------------------------------

            ert_location = (
                Location.objects
                    .filter(LOGIN=ert.LOGIN)
                    .order_by("-id")
                    .first()
            )

            if not ert_location:
                continue

            # ------------------------------------------------
            # CALCULATE DISTANCE
            # ------------------------------------------------

            distance = calculate_distance3(
                user_latitude,
                user_longitude,
                ert_location.latitude,
                ert_location.longitude
            )

            # ------------------------------------------------
            # SAME / NEARBY LOCATION
            # ------------------------------------------------

            if distance <= SEARCH_RADIUS_KM:
                result.append({
                    "id": ert.id,
                    "login_id": ert.LOGIN.id,
                    "name": ert.name,
                    "phone": str(ert.phone),
                    "email": ert.email,
                    "place": ert.place,
                    "district": ert.district,
                    "pin": ert.pin,
                    "gender": ert.gender,
                    "latitude": ert_location.latitude,
                    "longitude": ert_location.longitude,
                    "distance": round(distance, 2)
                })

        # ----------------------------------------------------
        # SORT NEAREST ERT FIRST
        # ----------------------------------------------------

        result.sort(
            key=lambda x: x["distance"]
        )

        return JsonResponse({
            "status": "ok",
            "user_latitude": user_latitude,
            "user_longitude": user_longitude,
            "data": result
        })

    except Exception as e:

        print("VIEW CONTACTS ERROR:", e)

        return JsonResponse({
            "status": "error",
            "message": str(e)
        })


# ============================================================
# myapp/views.py
# ============================================================
import math
from datetime import date

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Location, Notification_table

RADIUS_KM = 10  # alerts within this distance of the user's saved location are shown


def haversine_km(lat1, lon1, lat2, lon2):
    """Distance between two lat/lng points in kilometres."""
    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dlat = p2 - p1
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlon / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


@csrf_exempt
def user_view_disaster_notification(request):
    lid = request.POST.get("lid")

    if not lid:
        return JsonResponse({"status": "failed", "message": "User id missing", "data": []})

    # user's latest saved location
    loc = Location.objects.filter(LOGIN_id=lid).order_by("-date", "-id").first()
    if loc is None:
        return JsonResponse({
            "status": "failed",
            "message": "Your location is not saved yet",
            "data": [],
        })

    # 1) quick bounding-box filter in the database
    dlat = RADIUS_KM / 111.0
    dlon = RADIUS_KM / (111.0 * max(math.cos(math.radians(loc.latitude)), 0.01))

    candidates = Notification_table.objects.filter(
        latitude__range=(loc.latitude - dlat, loc.latitude + dlat),
        longitude__range=(loc.longitude - dlon, loc.longitude + dlon),
    ).order_by("-date")

    # 2) exact distance check
    alerts = []
    for n in candidates:
        dist = haversine_km(loc.latitude, loc.longitude, n.latitude, n.longitude)
        if dist <= RADIUS_KM:
            alerts.append({
                "id": n.id,
                "title": n.title,
                "date": n.date.strftime("%d-%m-%Y"),
                "place": n.place,
                "district": n.district,
                "latitude": n.latitude,
                "longitude": n.longitude,
                "distance": round(dist, 2),  # Flutter shows "$distance km"
            })

    alerts.sort(key=lambda a: a["distance"])  # nearest first

    return JsonResponse({
        "status": "success",
        "data": alerts,
        "user_location": {
            "latitude": loc.latitude,
            "longitude": loc.longitude,
        },
    })


######forgot
def forgotpasswordflutter(request):
    email = request.POST['email']
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Email not found'})

    otp = random.randint(100000, 999999)
    PasswordResetOTP.objects.create(email=email, otp=otp)

    send_mail('Your Verification Code',
              f'Your verification code is {otp}',
              settings.EMAIL_HOST_USER,
              [email],
              fail_silently=False)
    return JsonResponse({'status': 'ok', 'message': 'OTP sent'})


def verifyOtpflutterPost(request):
    email = request.POST['email']
    entered_otp = request.POST['entered_otp']
    otp_obj = PasswordResetOTP.objects.filter(email=email).latest('created_at')
    if otp_obj.otp == entered_otp:
        return JsonResponse({'status': 'ok'})
    else:
        return JsonResponse({'status': 'error'})


def changePasswordflutter(request):
    email = request.POST['email']
    newpassword = request.POST['newPassword']
    confirmPassword = request.POST['confirmPassword']
    if newpassword == confirmPassword:
        try:
            user = User.objects.get(email=email)
            user.set_password(confirmPassword)
            user.save()
            return JsonResponse({'status': 'ok'})
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User not found'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Passwords do not match'})


def forgot_web(request):
    return render(request, 'forgot.html')


def forgotPassword_otp(request):
    email = request.POST['email']
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        messages.warning(request, 'Email doesnt match')
        return redirect('/myapp/login/')
    otp = random.randint(100000, 999999)
    request.session['otp'] = str(otp)
    request.session['email'] = email

    send_mail('Your Verification Code',
              f'Your verification code is {otp}',
              settings.EMAIL_HOST_USER,
              [email],
              fail_silently=False)
    messages.success(request, 'OTP sent To your Mail')
    return redirect('/myapp/verifyOtp/')


def verifyOtp(request):
    return render(request, 'otpverification.html')


def verifyOtpPost(request):
    entered_otp = request.POST['entered_otp']
    if request.session.get('otp') == entered_otp:
        messages.success(request, 'otp verified')
        return redirect('/myapp/new_password/')
    else:
        messages.warning(request, 'Invalid OTP!!')
        return redirect('/myapp/login/')


def new_password(request):
    return render(request, 'new_password.html')


def changePassword(request):
    newpassword = request.POST['newPassword']
    confirmPassword = request.POST['confirmPassword']
    if newpassword == confirmPassword:
        email = request.session.get('email')
        user = User.objects.get(email=email)
        user.set_password(confirmPassword)
        user.save()
        messages.success(request, 'Password Updated Successfully')
        return redirect('/myapp/login/')
    else:
        messages.warning(request, 'The password doesnt match!!')
        return redirect('/myapp/new_password/')


@login_required(login_url='/myapp/login/')
def view_emergency_alerts(request):
    res = EmergencySOS.objects.all()
    return render(request, 'camp coordinator/view emergency.html', {'data': res})



from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Location


@csrf_exempt
@require_POST
def update_user_location(request):
    try:
        lid = request.POST.get('lid')
        lat = request.POST.get('latitude')
        lon = request.POST.get('longitude')

        if not lid or lat is None or lon is None:
            return JsonResponse({
                'status': 'error',
                'message': 'lid, latitude and longitude are required'
            }, status=400)

        user = User.objects.get(id=int(lid))
        latitude = float(lat)
        longitude = float(lon)

        if not (-90 <= latitude <= 90):
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid latitude'
            }, status=400)

        if not (-180 <= longitude <= 180):
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid longitude'
            }, status=400)

        # Update the user's latest location instead of creating
        # a new database row every 30 seconds.
        location = (
            Location.objects
            .filter(LOGIN=user)
            .order_by('-id')
            .first()
        )

        if location:
            location.latitude = latitude
            location.longitude = longitude
            location.date = timezone.localdate()
            location.save(
                update_fields=['latitude', 'longitude', 'date']
            )
        else:
            location = Location.objects.create(
                LOGIN=user,
                latitude=latitude,
                longitude=longitude,
                date=timezone.localdate()
            )

        return JsonResponse({
            'status': 'ok',
            'message': 'Location updated',
            'latitude': location.latitude,
            'longitude': location.longitude
        })

    except User.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'User not found'
        }, status=404)

    except (ValueError, TypeError):
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid user ID or coordinates'
        }, status=400)






# main part================================================

import json
import pandas as pd
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import Location
from .services import (
    extract_dem_terrain,
    get_live_rainfall,
    get_model_and_explainer,
    explain_prediction_shap,
)


@csrf_exempt
@require_POST
def update_user_location_for_landslide_prediction(request):
    """
    GeoNexus Landslide Early Warning & Decision Support API:
    - Persists GPS coordinates to the Location model.
    - Fuses real-time OpenWeather precipitation with SRTM DEM terrain features.
    - Runs XGBoost inference to estimate probability of landslide occurrence.
    - Generates SHAP explanation for the primary risk factor.
    - Formulates Decision Support advisory recommendations.
    """
    try:
        lid = request.POST.get('lid')
        lat = request.POST.get('latitude')
        lon = request.POST.get('longitude')

        # 1. Parameter Validation
        if not lid or lat is None or lon is None:
            return JsonResponse({
                'status': 'error',
                'message': 'Missing parameters: lid, latitude, and longitude are required'
            }, status=400)

        user = User.objects.get(id=int(lid))
        latitude = float(lat)
        longitude = float(lon)

        if not (-90.0 <= latitude <= 90.0):
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid latitude range (-90 to 90)'
            }, status=400)

        if not (-180.0 <= longitude <= 180.0):
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid longitude range (-180 to 180)'
            }, status=400)

        # 2. Update Database Record
        location = Location.objects.filter(LOGIN=user).order_by('-id').first()
        if location:
            location.latitude = latitude
            location.longitude = longitude
            location.date = timezone.localdate()
            location.save(update_fields=['latitude', 'longitude', 'date'])
        else:
            location = Location.objects.create(
                LOGIN=user,
                latitude=latitude,
                longitude=longitude,
                date=timezone.localdate()
            )

        # 3. Multi-Source Data Collection (DEM Elevation + Real-time Rainfall)
        altitude, slope = extract_dem_terrain(latitude, longitude)
        rainfall = get_live_rainfall(latitude, longitude)

        # 4. Model Loading & Inference
        xgb_data, _ = get_model_and_explainer()
        if xgb_data is None or 'model' not in xgb_data or xgb_data['model'] is None:
            return JsonResponse({
                'status': 'error',
                'message': 'XGBoost model file not loaded on server'
            }, status=500)

        input_df = pd.DataFrame([{
            'latitude': latitude,
            'longitude': longitude,
            'altitude': altitude,
            'slope': slope,
            'rainfall': rainfall
        }])

        model = xgb_data['model']
        risk_probability = float(model.predict_proba(input_df)[0][1])

        # 5. Explainable AI (SHAP Analysis)
        shap_analysis = explain_prediction_shap(input_df)

        # 6. Decision Support & Alert Logic
        if risk_probability >= 0.70:
            risk_level = "High Risk"
            risk_color = "red"
            alert_message = "Severe landslide hazard detected! Immediate caution advised."
            decision_support = {
                "action": "Immediate Evacuation",
                "advisory": "Avoid steep slope transit roads. Relocate to the designated disaster relief camp."
            }
        elif risk_probability >= 0.35:
            risk_level = "Moderate Risk"
            risk_color = "orange"
            alert_message = "Moderate landslide risk zone. Maintain heightened vigilance."
            decision_support = {
                "action": "Heightened Vigilance",
                "advisory": "Suspend night travel in hillside sectors. Report abnormal soil cracks or runoffs immediately."
            }
        else:
            risk_level = "Low Risk"
            risk_color = "green"
            alert_message = "Terrain conditions are currently stable."
            decision_support = {
                "action": "Routine Awareness",
                "advisory": "Normal conditions. Continue monitoring official meteorological alerts."
            }

        # 7. JSON Response to Flutter Frontend
        return JsonResponse({
            'status': 'ok',
            'latitude': latitude,
            'longitude': longitude,
            'risk_level': risk_level,
            'risk_color': risk_color,
            'risk_probability': round(risk_probability * 100, 2),
            'alert_message': alert_message,
            'decision_support': decision_support,
            'explainable_ai_shap': shap_analysis,
            'environmental_parameters': {
                'altitude_m': altitude,
                'slope_deg': slope,
                'rainfall_mm': rainfall
            }
        })

    except User.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'User with provided lid not found'}, status=404)
    except (ValueError, TypeError) as e:
        return JsonResponse({'status': 'error', 'message': f'Invalid parameter format: {str(e)}'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Internal Server Error: {str(e)}'}, status=500)
