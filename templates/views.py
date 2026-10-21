{% comment %} from datetime import datetime
import json
import pickle
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password

from django.contrib.auth import logout, authenticate, login
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User,Group
import requests
from myapp.models import *
from myapp.river import get_rivers_near_location
from myapp.sample import getmaindata

# Create your views here.

def fun_logout(request):
    logout(request)
    return redirect('/myapp/login/')
def login_get(request):
    return render(request,'login.html')

def login_post(request):
    username=request.POST['username']
    password=request.POST['password']
    ob=authenticate(request,username=username,password=password)
    if ob is not None:
        if ob.groups.filter(name="Admin").exists():
            login(request,ob)
            return redirect('/myapp/admin_home/')
        elif ob.groups.filter(name='Camp_coordinator').exists():
            login(request,ob)
            print(request.user.id)

            return redirect('/myapp/camp_coordinator_home/')
        else:
            return redirect('/myapp/login/')
    return redirect('/myapp/login/')

def admin_home(request):
    return render(request,'admin/admin home.html')


def camp_coordinator_home(request):
    return render(request,'camp coordinator/home.html')


def registration(request):
    return render(request,'camp coordinator/signup.html')



def admin_add_ert(request):
    return render(request,'admin/add ert.html')

def admin_add_ert_post(request):
    name = request.POST['textfield']
    gender = request.POST['radiobutton']
    place = request.POST['textfield2']
    dob=request.POST['dob']
    post = request.POST['textfield3']
    pin = request.POST['textfield4']
    district = request.POST['district']
    phone = request.POST['textfield8']
    email = request.POST['textfield9']
    username = request.POST['username']
    password = request.POST['password']
    photo = request.FILES['photo']
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
    ert.district=district
    ert.dob=dob
    ert.phone = phone
    ert.email = email
    ert.photo = photo
    ert.save()
    return redirect('/myapp/admin_view_ert/')


def admin_view_ert(request):
    ert_list = ERT_table.objects.all().order_by('-id')
    return render(request,'admin/view ert.html',{'ert_list': ert_list})



def admin_edit_ert(request, id):
    ert = ERT_table.objects.get(id=id)
    request.session['ert_id']=id
    return render(request,'admin/edit ert.html',{'ert': ert})
    
def admin_ert_edit_post(request):
    ert=ERT_table.objects.get(id=request.session['ert_id'])
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




def admin_delete_ert(request, id):
    ert = ERT_table.objects.get(LOGIN=id)
    ert.delete()
    User.objects.get(id=id).delete()
    return redirect('/myapp/admin_view_ert/')


def verify_camp_coordinator(request):
    res=Camp_coordinator_table.objects.all()
    return render(request,'admin/verify camp coordinator.html',{'data':res})

def approve_camp_coordinator(request,id):
    Camp_coordinator_table.objects.filter(LOGIN=id).update(status="Verified")
    return redirect('/myapp/verify_camp_coordinator/')


def reject_camp_coordinator(request,id):
    Camp_coordinator_table.objects.filter(LOGIN=id).update(status="Rejected")
    return redirect('/myapp/verify_camp_coordinator/')


def registration_post(request):
    name = request.POST['textfield']
    gender = request.POST['radiobutton']
    place = request.POST['textfield2']
    dob=request.POST['dob']
    post = request.POST['textfield3']
    pin = request.POST['textfield4']
    district = request.POST['district']
    phone = request.POST['textfield8']
    email = request.POST['textfield9']
    username = request.POST['username']
    password = request.POST['password']
    photo = request.FILES['photo']
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
    ert.district=district
    ert.dob=dob
    ert.phone = phone
    ert.email = email
    ert.photo = photo
    ert.save()
    return redirect('/myapp/login/')


def camp_coordinator_viewprofile(request):
    res=Camp_coordinator_table.objects.get(LOGIN=request.user.id)
    return render(request,'camp coordinator/view profile.html',{'data':res})


def camp_coordinator_editprofile(request):
    res=Camp_coordinator_table.objects.get(LOGIN=request.user.id)
    return render(request,'camp coordinator/edit profile.html',{'data':res})


def camp_coordinator_editprofile_post(request):
    name = request.POST['textfield']
    gender = request.POST['radiobutton']
    place = request.POST['textfield2']
    dob=request.POST['dob']
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
    ert.district=district
    ert.dob=dob
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

def manage_relief_camp(request):
    coordinator = Camp_coordinator_table.objects.get(LOGIN=request.user.id)
    camps = Relief_camp_table.objects.filter(COORDINATOR=coordinator).order_by('-date')
    return render(request,'camp coordinator/view relief camp.html',{'data': camps})

# ==========================================================
# ADD RELIEF CAMP - PAGE
# ==========================================================

def add_relief_camp(request):
    return render(request,'camp coordinator/manage relief camp.html')

# ==========================================================
# ADD RELIEF CAMP - POST
# ==========================================================

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
def edit_relief_camp(request, id):
    camp = Relief_camp_table.objects.get(id=id)
    request.session['camp_id']=id
    return render(request,'camp coordinator/edit relief camp.html',{'data': camp})

# ==========================================================
# EDIT RELIEF CAMP - POST
# ==========================================================

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


def delete_camp(request,id):
    Relief_camp_table.objects.get(id=id).delete()
    return redirect('/myapp/manage_relief_camp/')


# =========================================================
# ADD REQUIREMENT PAGE
# =========================================================

def add_requirements(request, id):
    camp = Relief_camp_table.objects.get(id=id)
    request.session['rid']=id
    return render(request,'camp coordinator/add camp requirements.html',{'camp': camp })


# =========================================================
# ADD REQUIREMENT POST
# =========================================================

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

def view_requirements(request):
    requirements = Requirements_table.objects.filter(CAMP__COORDINATOR__LOGIN_id=request.user.id).order_by('-date')
    return render(request,'camp coordinator/view camp requirements.html',{'data': requirements})


# =========================================================
# EDIT REQUIREMENT
# =========================================================

def edit_requirement(request, id):
    requirement = Requirements_table.objects.get(id=id)
    request.session['req_id']=id
    return render(request,'camp coordinator/edit requirement.html',{'data': requirement,})


# =========================================================
# EDIT REQUIREMENT POST
# =========================================================

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

def delete_requirement(request, id):
    requirement = Requirements_table.objects.get(id=id).delete()
    return redirect('/myapp/view_requirements/')





# =========================================================
# ADD INVENTORY PAGE
# =========================================================

def add_inventory(request, id):
    camp = Relief_camp_table.objects.get(id=id)
    request.session['rid']=id
    return render(request,'camp coordinator/add inventory.html',{'camp': camp })


# =========================================================
# ADD INVENTORY POST
# =========================================================

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

def view_inventory(request):
    requirements = Inventory_table.objects.filter(CAMP__COORDINATOR__LOGIN_id=request.user.id).order_by('-date')
    return render(request,'camp coordinator/view inventory.html',{'data': requirements})


# =========================================================
# EDIT INVENTORY
# =========================================================

def edit_inventory(request, id):
    requirement = Inventory_table.objects.get(id=id)
    request.session['invt_id']=id
    return render(request,'camp coordinator/edit inventory.html',{'data': requirement,})


# =========================================================
# EDIT INVENTORY POST
# =========================================================

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

def delete_inventory(request, id):
    requirement = Inventory_table.objects.get(id=id).delete()
    return redirect('/myapp/view_inventory/')



# =========================================================
# VIEW / MANAGE DISASTER VICTIMS
# =========================================================

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

def add_disaster_victim(request):

    return render(
        request,
        'camp coordinator/add disaster victims.html'
    )


# =========================================================
# ADD DISASTER VICTIM - POST
# =========================================================

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

        photo=photo
    )

    return redirect('/myapp/manage_disaster_victim/')


# =========================================================
# EDIT DISASTER VICTIM - PAGE
# =========================================================

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

def delete_disaster_victim(request, id):

    Disaster_victim_table.objects.get(
        id=id
    ).delete()

    return redirect('/myapp/manage_disaster_victim/')





# =========================================================
# VIEW GUIDELINES
# =========================================================

def admin_view_preparedness_guidelines(request):
    data = Guidelines_table.objects.all().order_by('-date')
    return render(request,'admin/view disaster prepardness guidence.html',{'data': data})

# =========================================================
# ADD GUIDELINE PAGE
# =========================================================

def admin_add_preparedness_guideline(request):
    return render(request,'admin/upload disaster prepardness guidence.html')

# =========================================================
# ADD GUIDELINE POST
# =========================================================

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

def admin_edit_preparedness_guideline(request, id):
    data = Guidelines_table.objects.get(id=id)
    request.session['pid']=id
    return render(request,'admin/edit preparedness guideline.html',{'data': data})

# =========================================================
# EDIT GUIDELINE POST
# =========================================================

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

def admin_delete_preparedness_guideline(request, id):
    guideline = Guidelines_table.objects.get(id=id)
    guideline.delete()
    return redirect('/myapp/admin_view_preparedness_guidelines/')




# =========================================================
# VIEW EARLY WARNING NOTIFICATIONS
# =========================================================

def admin_view_notifications(request):
    notifications = Notification_table.objects.all().order_by('-date', '-id')
    return render(request,'admin/view notification.html',{'data': notifications})

# =========================================================
# ADD EARLY WARNING NOTIFICATION - PAGE
# =========================================================

from django.shortcuts import render, redirect
from .models import Notification_table


# =========================================================
# ADD EARLY WARNING NOTIFICATION - GET
# =========================================================

def admin_add_notification(request):

    return render(
        request,
        'admin/add early warning.html'
    )


# =========================================================
# ADD EARLY WARNING NOTIFICATION - POST
# =========================================================

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

def admin_edit_notification(request, id):
    notification = Notification_table.objects.get(id=id)
    request.session['nid']=id
    return render(request,'admin/edit early warning.html',{'data': notification})


# =========================================================
# EDIT EARLY WARNING NOTIFICATION - POST
# =========================================================

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

def admin_delete_notification(request, id):
    notification = Notification_table.objects.get(id=id)
    notification.delete()
    return redirect('/myapp/admin_view_notifications/')




def admin_view_complaints(request):
    comp = Complaints_table.objects.all().order_by('-date', '-id')
    return render(request,'admin/view complaints.html',{'data': comp})

def send_reply(request,id):
    request.session['com_id']=id
    return render(request,'admin/send reply.html')

def send_reply_post(request):
    reply=request.POST['reply']
    obj=Complaints_table.objects.get(id=request.session['com_id'])
    obj.reply=reply
    obj.save()
    return redirect('/myapp/admin_view_complaints/')
    

def admin_view_feedback(request):
    comp = Feedbak_table.objects.all().order_by('-date', '-id')
    return render(request,'admin/view feedback.html',{'data': comp})
 

def admin_assign_volunteer(request,id):
    request.session['vid']=id
    camp=Relief_camp_table.objects.all()
    return render(request,'admin/assign volunteer.html',{'camps':camp})

def admin_assign_volunteer_post(request):
    camp=request.POST['camp']
    obj=Assign_table()
    obj.date=datetime.now().today()
    obj.VOLUNTEER_id=request.session['vid']
    obj.CAMP_id=camp
    obj.status='Assigned'
    obj.save()
    return redirect('/myapp/admin_verify_volunteers/')




def verify_volunteers(request):
    res=Volunteer_table.objects.all()
    return render(request,'admin/verify volunteers.html',{'data':res})

def approve_volunteers(request,id):
    Volunteer_table.objects.filter(LOGIN=id).update(status="Verified")
    return redirect('/myapp/admin_verify_volunteers/')


def reject_volunteers(request,id):
    Volunteer_table.objects.filter(LOGIN=id).update(status="Rejected")
    return redirect('/myapp/admin_verify_volunteers/')

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


def admin_delete_assigned_volunteer(request, id):
    Assign_table.objects.filter(id=id).delete()

    return redirect('/myapp/admin_view_assigned_volunteers/') 




def coordinator_view_ert(request):
    res=ERT_table.objects.all()
    return render(request,'camp coordinator/view ert.html',{'data':res})
def coordinator_view_volunteers(request):
    data = Assign_table.objects.filter(CAMP__COORDINATOR__LOGIN_id=request.user)
    return render(request,'camp coordinator/view volunteers.html',{'data': data})




####################################################flutter

def user_register(request):
    name = request.POST['textfield']
    gender = request.POST['radiobutton']
    place = request.POST['textfield2']
    dob=request.POST['dob']
    post = request.POST['textfield3']
    pin = request.POST['textfield4']
    district = request.POST['district']
    phone = request.POST['textfield8']
    email = request.POST['textfield9']
    username = request.POST['username']
    password = request.POST['password']
    photo = request.FILES['photo']
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
    ert.district=district
    ert.dob=dob
    ert.phone = phone
    ert.email = email
    ert.photo = photo
    ert.save()
    return JsonResponse({'status':'ok'})

def volunteer_register(request):
    name = request.POST['textfield']
    gender = request.POST['radiobutton']
    place = request.POST['textfield2']
    dob=request.POST['dob']
    post = request.POST['textfield3']
    pin = request.POST['textfield4']
    district = request.POST['district']
    phone = request.POST['textfield8']
    email = request.POST['textfield9']
    username = request.POST['username']
    password = request.POST['password']
    photo = request.FILES['photo']
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
    ert.district=district
    ert.dob=dob
    ert.phone = phone
    ert.email = email
    ert.photo = photo
    ert.save()
    return JsonResponse({'status':'ok'})

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
            return JsonResponse({'status':'ok'})
        else:
            return JsonResponse({'status': 'no'})
    else:
        return JsonResponse({'status': 'no'})
    
    
def app_login(request):
    username = request.POST['username']
    password = request.POST['password']
    user=authenticate(request,username=username,password=password)
    if user is not None:
        login(request,user)
        if user.groups.filter(name="User").exists():
            return JsonResponse({'status':'ok','lid':str(user.id),'type':'User'})
        
        elif user.groups.filter(name="ERT").exists():
            return JsonResponse({'status':'ok','lid':str(user.id),'type':'ERT'})
        
        
        elif user.groups.filter(name="Volunteer").exists():
            return JsonResponse({'status':'ok','lid':str(user.id),'type':'Volunteer'})
        else:
            return JsonResponse({'status': 'no'})
    else:
        return JsonResponse({'status': 'no'})
    
    
def user_viewprofile(request):
    id=request.POST['lid']
    a=User_table.objects.get(LOGIN_id=id)
    return JsonResponse({
        'status':'ok',
        'name':a.name,
        'gender':a.gender,
        'phone':a.phone,
        'email':a.email,
        'DOB':a.dob,
        'place':a.place,
        'post':a.post,
        'pincode':a.pin,
        'district':a.district,
        'photo': request.build_absolute_uri(a.photo.url) if a.photo else "",
    })

def user_edit_profile(request):
    name = request.POST['textfield']
    gender = request.POST['radiobutton']
    place = request.POST['textfield2']
    dob=request.POST['dob']
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
    ert.district=district
    ert.dob=dob
    ert.phone = phone
    ert.email = email
    ert.save()
    return JsonResponse({'status':'ok'})


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
    lid=request.POST['lid']
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



def userviewnotification(request):
    ob = Notification_table.objects.all()
    mdata = []
    for i in ob:
        mdata.append({
            'title': i.title,
            'description': i.description,
            'date': str(i.date), 
            'id': str(i.id)

        })
    print(mdata)
    return JsonResponse({"status": "ok", "data": mdata})

# def _update_location(request):
#     lid=request.POST['mid']
#     lat=request.POST['lat']
#     lon=request.POST['lon']
#     dobj=Location()
#     if Location.objects.filter(LOGIN_id=lid).exists():
#         dobj = Location.objects.get(LOGIN_id=lid)
#     dobj.latitude=lat
#     dobj.longitude=lon
#     dobj.LOGIN_id=lid
#     dobj.save()
#     return JsonResponse({'status':'ok'})


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
    cid=request.POST['cid']
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
    cid=request.POST['cid']
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
    reqid=request.POST['reqid']
    lid=request.POST['lid']
    quantity=request.POST['quantity']
    obj=Donate_goods()
    obj.date=datetime.now().today()
    obj.REQUIREMENTS_id=reqid
    obj.quantity=quantity
    obj.LOGIN=User.objects.get(id=lid)
    obj.status="Donated"
    obj.save()
    return JsonResponse({'status':'ok'})
    

def volunteer_viewprofile(request):
    id=request.POST['lid']
    a=Volunteer_table.objects.get(LOGIN_id=id)
    return JsonResponse({
        'status':'ok',
        'name':a.name,
        'gender':a.gender,
        'phone':a.phone,
        'email':a.email,
        'DOB':a.dob,
        'place':a.place,
        'post':a.post,
        'pincode':a.pin,
        'district':a.district,
        'photo': request.build_absolute_uri(a.photo.url) if a.photo else "",
    })

def volunteer_edit_profile(request):
    name = request.POST['textfield']
    gender = request.POST['radiobutton']
    place = request.POST['textfield2']
    dob=request.POST['dob']
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
    ert.district=district
    ert.dob=dob
    ert.phone = phone
    ert.email = email
    ert.save()
    return JsonResponse({'status':'ok'})


def ert_viewprofile(request):
    id=request.POST['lid']
    a=ERT_table.objects.get(LOGIN_id=id)
    return JsonResponse({
        'status':'ok',
        'name':a.name,
        'gender':a.gender,
        'phone':a.phone,
        'email':a.email,
        'DOB':a.dob,
        'place':a.place,
        'post':a.post,
        'pincode':a.pin,
        'district':a.district,
        'photo': request.build_absolute_uri(a.photo.url) if a.photo else "",
    })
    
     
    
############################################camp coordinator chat with ert
def chat1(request,id):
    request.session["userid"] = id
    cid = str(request.session["userid"])
    request.session["new"] = cid
    qry = ERT_table.objects.get(LOGIN=cid)
    return render(request, "camp coordinator/Chat.html", {'photo': request.build_absolute_uri(qry.photo.url)if qry.photo else "", 'name': qry.name, 'toid': cid})

def chat_view(request):
    fromid = request.user.id
    toid = request.session["userid"]
    qry = ERT_table.objects.get(LOGIN=request.session["userid"])
    from django.db.models import Q
    res = Chat_table.objects.filter(Q(FROMID_id=fromid, TOID_id=toid) | Q(FROMID_id=toid, TOID_id=fromid))
    l = []
    for i in res:
        l.append({"id": i.id, "message": i.message, "to": i.TOID_id, "date": i.date, "from": i.FROMID_id})
    return JsonResponse({'photo': request.build_absolute_uri(qry.photo.url)if qry.photo else "", "data": l, 'name': qry.name, 'toid': request.session["userid"]})

def chat_send(request, msg):
    lid =  request.user.id
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

# def User_sendchat(request):
#     FROM_id=request.POST['from_id']
#     TOID_id=request.POST['to_id']
#     print(FROM_id)
#     print(TOID_id)
#     msg=request.POST['message']
#     from  datetime import datetime
#     c=Chat_table()
#     c.FROMID_id=FROM_id
#     c.TOID_id=TOID_id
#     c.message=msg
#     c.date=datetime.now()
#     c.save()
#     return JsonResponse({'status':"ok"})


# def User_viewchat(request):
#     fromid = request.POST["from_id"]
#     toid = request.POST["to_id"]
#     from django.db.models import Q
#     res = Chat_table.objects.filter(Q(FROMID_id=fromid, TOID_id=toid) | Q(FROMID_id=toid, TOID_id=fromid))
#     l = []
#     for i in res:
#         l.append({"id": i.id, "message": i.message, "from": i.FROMID_id, "date": i.date, "to": i.TOID_id})
#     return JsonResponse({"status":"ok",'data':l})


##############################################################


#camp coordinator chat with volunteer


def chat2(request,id):
    request.session["userid"] = id
    cid = str(request.session["userid"])
    request.session["new"] = cid
    qry = Volunteer_table.objects.get(LOGIN=cid)
    return render(request, "camp coordinator/chat with volunteers.html", {'photo': request.build_absolute_uri(qry.photo.url)if qry.photo else "", 'name': qry.name, 'toid': cid})

def chat_view2(request):
    fromid = request.user.id
    toid = request.session["userid"]
    qry = Volunteer_table.objects.get(LOGIN=request.session["userid"])
    from django.db.models import Q
    res = Chat_table.objects.filter(Q(FROMID_id=fromid, TOID_id=toid) | Q(FROMID_id=toid, TOID_id=fromid))
    l = []
    for i in res:
        l.append({"id": i.id, "message": i.message, "to": i.TOID_id, "date": i.date, "from": i.FROMID_id})
    return JsonResponse({'photo': request.build_absolute_uri(qry.photo.url)if qry.photo else "", "data": l, 'name': qry.name, 'toid': request.session["userid"]})

def chat_send2(request, msg):
    lid =  request.user.id
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
    lid=request.POST['lid']
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
from myapp.models import Requirements_table
from myapp.blockchain import contract, w3


@csrf_exempt
def add_donation_bc_post(request):

    if request.method != "POST":
        return JsonResponse({
            'status': 'error',
            'message': 'POST request required'
        }, status=400)

    try:

        # --------------------------------------------------
        # GET DATA FROM FLUTTER
        # --------------------------------------------------

        reqid = request.POST.get('reqid')
        amount = request.POST.get('amount')
        userid = request.POST.get('lid')
        payment_id = request.POST.get('payment_id', '')

        print("REQ ID:", reqid)
        print("AMOUNT:", amount)
        print("USER ID:", userid)
        print("PAYMENT ID:", payment_id)

        # --------------------------------------------------
        # VALIDATION
        # --------------------------------------------------

        if not reqid:
            return JsonResponse({
                'status': 'error',
                'message': 'Requirement ID is missing'
            }, status=400)

        if not amount:
            return JsonResponse({
                'status': 'error',
                'message': 'Donation amount is missing'
            }, status=400)

        if not userid:
            return JsonResponse({
                'status': 'error',
                'message': 'User ID is missing'
            }, status=400)

        # --------------------------------------------------
        # GET REQUIREMENT
        # --------------------------------------------------

        try:
            ob = Requirements_table.objects.get(
                id=int(reqid)
            )
        except Requirements_table.DoesNotExist:

            return JsonResponse({
                'status': 'error',
                'message': 'Requirement not found'
            }, status=404)

        # --------------------------------------------------
        # DATE
        # --------------------------------------------------

        date = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        # --------------------------------------------------
        # BLOCKCHAIN
        # --------------------------------------------------
        #
        # Solidity:
        #
        # addDonations(
        #   uint256 user_id,
        #   uint256 request_id,
        #   string amount,
        #   string date,
        #   string hash
        # )
        #
        # Therefore 5 arguments are required.
        # --------------------------------------------------

        tx_hash = contract.functions.addDonations(

            int(userid),       # user_id

            int(ob.id),       # requirement_id

            str(amount),      # amount

            str(date),        # date

            str(payment_id)   # hash/payment ID

        ).transact()

        # --------------------------------------------------
        # WAIT FOR BLOCKCHAIN CONFIRMATION
        # --------------------------------------------------

        receipt = w3.eth.wait_for_transaction_receipt(
            tx_hash
        )

        # --------------------------------------------------
        # GET BLOCKCHAIN DONATION ID
        # --------------------------------------------------

        blockchain_id = contract.functions \
            .getAllDonationsIds() \
            .call()[-1]

        # --------------------------------------------------
        # TRANSACTION HASH
        # --------------------------------------------------

        transaction_hash = tx_hash.hex()

        print(
            "Blockchain ID:",
            blockchain_id
        )

        print(
            "Transaction Hash:",
            transaction_hash
        )

        # --------------------------------------------------
        # RESPONSE
        # --------------------------------------------------

        return JsonResponse({

            'status': 'ok',

            'message':
                'Donation successfully recorded',

            'blockchain_id':
                blockchain_id,

            'transaction_hash':
                transaction_hash,

            'requirement_id':
                ob.id,

            'amount':
                str(amount)

        })

    except Exception as e:

        print(
            "Donation Error:",
            str(e)
        )

        return JsonResponse({

            'status': 'error',

            'message':
                str(e)

        }, status=500)

from django.http import JsonResponse
from myapp.models import Requirements_table
from myapp.blockchain import contract


def user_view_send_donations(request):
    lid = request.POST.get('lid')
    if not lid:
        return JsonResponse({
            'status': 'error',
            'message': 'User ID is required'
        })
    contract_list = []
    try:
        logged_user_id = int(lid)

        # Get all blockchain donation IDs
        blockchain_ids = contract.functions.getAllDonationsIds().call()

        for bc_id in blockchain_ids:

            try:
                # Read donation from blockchain
                user_id, request_id, amount, date, hash_value = (
                    contract.functions.getMark(bc_id).call()
                )

                # -------------------------------------------------
                # IMPORTANT:
                # Show only donations belonging to logged-in user
                # -------------------------------------------------
                if int(user_id) != logged_user_id:
                    continue

                # Get requirement
                req = Requirements_table.objects.filter(
                    id=request_id
                ).select_related(
                    'CAMP',
                    'CAMP__COORDINATOR'
                ).first()

                if not req:
                    continue

                # -------------------------------------------------
                # Add user's donation history
                # -------------------------------------------------
                contract_list.append({

                    'id': str(bc_id),

                    'title':
                        req.title,

                    'needquantity':
                        req.needquantity,

                    'details':
                        req.details,

                    'campname':
                        req.CAMP.campname,

                    'place':
                        req.CAMP.place,

                    'coordinatorname':
                        req.CAMP.COORDINATOR.name,

                    'coordinatorphone':
                        str(req.CAMP.COORDINATOR.phone),

                    'amount':
                        str(amount),

                    'date':
                        str(date),

                    'transaction_hash':
                        str(hash_value),
                })

            except Exception as e:
                print(
                    "Skipped blockchain donation:",
                    bc_id,
                    e
                )
                continue

        # Optional: newest donation first
        contract_list.reverse()

        print(
            "Logged User:",
            logged_user_id
        )

        print(
            "Donation History:",
            contract_list
        )

        return JsonResponse({
            'status': 'ok',
            'contracts': contract_list
        })

    except Exception as e:

        print(
            "Donation history error:",
            e
        )

        return JsonResponse({
            'status': 'error',
            'message': str(e)
        })


def user_view_goods_history(request):
    lid=request.POST['lid']
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
    don = Donate_goods.objects.filter(REQUIREMENTS__CAMP__COORDINATOR__LOGIN_id=request.user.id).order_by('-date')
    l=[]
    for i in don:
        d=Donations_Assign_table.objects.filter(DONATE_id=i.id).first()
        l.append({
            'id':i.id,
            'date':i.date,
            'status':i.status,
            'quantity':i.quantity,
            'title':i.REQUIREMENTS.title,
            'details':i.REQUIREMENTS.details,
            'username':i.LOGIN.username,
            'email':i.LOGIN.email,
            'campname':i.REQUIREMENTS.CAMP.campname,
            'place':i.REQUIREMENTS.CAMP.place,
            
            'volunteer':d.VOLUNTEER.name,
            'phone':d.VOLUNTEER.phone,
            'dstatus':d.status,
            
            })
    return render(request,'camp coordinator/view request resources.html',{'data': l})



def coordinator_assigntask_volunteer(request,id):
    request.session['did']=id
    camp=Assign_table.objects.filter(CAMP__COORDINATOR__LOGIN_id=request.user.id)
    return render(request,'camp coordinator/assign volunteer.html',{'camps':camp})

def admin_assigntask_volunteer_post(request):
    volunteer=request.POST['volunteer']
    obj=Donations_Assign_table()
    obj.date=datetime.now().today()
    obj.VOLUNTEER_id=volunteer
    obj.DONATE_id=request.session['did']
    obj.status='Task Assigned'
    obj.save()
    
    # c=Donate_goods.objects.get(id=request.session['did'])
    # c.status="Task Assigned"
    # c.save()
    
    return redirect('/myapp/view_goods_donations/')



@login_required(login_url='/myapp/login/')
def change_passwords(request):
    return render(request,'camp coordinator/changepassword.html')


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
    lid=request.POST['lid']
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
    did=request.POST['did']
    obj=Donations_Assign_table.objects.get(id=did)
    obj.status="Collected"
    obj.save()
    return JsonResponse({"status": "ok"})
    
    
def volunteerviewrequirements(request):
    lid=request.POST['lid']
    ob = Assign_table.objects.filter(VOLUNTEER__LOGIN_id=lid)
    mdata = []
    for i in ob:
        req=Requirements_table.objects.filter(CAMP_id=i.CAMP.id).first()
        mdata.append({
            'title': req.title,
            'needquantity': req.needquantity,
            'details': req.details,
            'campname':i.CAMP.campname,
            'place':i.CAMP.place,
            'coordinator':i.CAMP.COORDINATOR.name,
            'phone':i.CAMP.COORDINATOR.phone,
            'date': str(i.date), 
            'id': str(i.id)

        })
    print(mdata)
    return JsonResponse({"status": "ok", "data": mdata})



def volunteer_add_daily_report(request):
    notes=request.POST['notes']
    lid=request.POST['lid']
    lob = Dialy_activity_report()
    lob.VOLUNTEER = Volunteer_table.objects.get(LOGIN__id=lid)
    lob.notes = notes
    lob.date = datetime.now().today()
    lob.save()
    return JsonResponse({'task': 'ok'})
    
def volunteerviewdailyreport(request):
    lid=request.POST['lid']
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
    id=request.POST['id']
    Dialy_activity_report.objects.get(id=id).delete()
    return JsonResponse({'status':'ok'})



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
            'photo': request.build_absolute_uri(i.photo.url)if i.photo else "",
            'place': str(i.place), 
            'id': str(i.LOGIN.id)

        })
    print(mdata)
    return JsonResponse({"status": "ok", "data": mdata})


def coordinator_view_daily_report(request,id):
    vol=Dialy_activity_report.objects.filter(VOLUNTEER_id=id)
    return render(request,'camp coordinator/view volunteer daily report.html',{'data':vol})




def ertviewvolunteer(request):
    ob = Volunteer_table.objects.filter(status="Verified")
    mdata = []
    for i in ob:
        mdata.append({
            'name': i.name,
            'phone': str(i.phone),
            'email': str(i.email),
            'photo': request.build_absolute_uri(i.photo.url)if i.photo else "",
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
            'photo': request.build_absolute_uri(i.photo.url)if i.photo else "",
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
            'dob': str(i.dob),
            'photo': request.build_absolute_uri(i.photo.url)if i.photo else "",
            'place': str(i.place), 
            'id': str(i.id),

        })
    print(mdata)
    return JsonResponse({"status": "ok", "data": mdata})


from django.shortcuts import render
from .models import Requirements_table, User_table


def camp_coordinator_view_blockchain(request):

    contract_list = []

    try:
        # Get all donation IDs from blockchain
        blockchain_ids = contract.functions.getAllDonationsIds().call()

        for bc_id in blockchain_ids:

            try:
                # Read donation from blockchain
                user_id, request_id, amount, date, donation_hash = (
                    contract.functions.getMark(bc_id).call()
                )

                # Ignore invalid donation
                if user_id == 0 or request_id == 0:
                    continue

                # -------------------------------------------------
                # Find requirement belonging to this coordinator
                # -------------------------------------------------
                req = Requirements_table.objects.filter(
                    id=request_id,
                    CAMP__COORDINATOR__LOGIN_id=request.user.id
                ).select_related(
                    'CAMP',
                    'CAMP__COORDINATOR'
                ).first()

                # If requirement is not from this coordinator's
                # camp, skip the donation
                if not req:
                    continue

                # -------------------------------------------------
                # Find donor/user
                # -------------------------------------------------
                donor = User_table.objects.filter(
                    LOGIN_id=user_id
                ).first()

                # -------------------------------------------------
                # Add donation information
                # -------------------------------------------------
                contract_list.append({
                    'bc_id': str(bc_id),

                    'user_id': str(user_id),

                    'request_id': str(request_id),

                    'amount': str(amount),

                    'date': str(date),

                    'hash': str(donation_hash),

                    # Requirement details
                    'title': req.title,

                    'needquantity': req.needquantity,

                    'details': req.details,

                    # Camp details
                    'campname': req.CAMP.campname,

                    'place': req.CAMP.place,

                    # Donor details
                    'donor_name': donor.name if donor else 'Unknown Donor',

                    'donor_email': donor.email if donor else '-',

                    'donor_phone': (
                        str(donor.phone)
                        if donor else '-'
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
        print("Blockchain Error:", e)

    # Latest donations first
    contract_list.reverse()

    return render(
        request,
        'camp coordinator/view donations.html',
        {
            'data': contract_list
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

            # Requirement
            'title': req.title,
            'needquantity': req.needquantity,
            'details': req.details,

            # Donation
            'quantity': donate.quantity,
            'donation_date': donate.date,
            'donation_status': donate.status,

            # Camp
            'campname': camp.campname,
            'place': camp.place,
            'district': camp.district,

            # Coordinator
            'coordinator': camp.COORDINATOR.name,
            'coordinator_phone': camp.COORDINATOR.phone,

            # Volunteer
            'volunteer': volunteer.name,
            'volunteer_phone': volunteer.phone,

            # Distribution
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


####################################################################


import pickle
import requests
from django.shortcuts import render
from django.http import JsonResponse
from .sample import getmaindata
from .river import get_rivers_near_location


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
    r"E:\Regional\disaster\disaster_management"
    r"\myapp\knn_model.pkl"
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




######emergency sos


import json

from django.http import JsonResponse
from django.contrib.auth.models import User

from .models import EmergencySOS


# def emergency_sos(request):

    # if request.method != "POST":
    #     return JsonResponse({
    #         "status": "error",
    #         "message": "Only POST method is allowed"
    #     })

    # try:

    #     # ======================================================
    #     # GET JSON DATA FROM FLUTTER
    #     # ======================================================

    #     data = json.loads(request.body)

    #     lid = data.get("lid")
    #     latitude = data.get("latitude")
    #     longitude = data.get("longitude")
    #     status = data.get("status", "Emergency")

    #     # ======================================================
    #     # VALIDATION
    #     # ======================================================

    #     if latitude is None or longitude is None:

    #         return JsonResponse({
    #             "status": "error",
    #             "message": "Location is required"
    #         })

    #     if lid is None or lid == "":

    #         return JsonResponse({
    #             "status": "error",
    #             "message": "User ID is required"
    #         })

    #     # ======================================================
    #     # CONVERT VALUES
    #     # ======================================================

    #     try:
    #         lid = int(lid)
    #         latitude = float(latitude)
    #         longitude = float(longitude)

    #     except (ValueError, TypeError):

    #         return JsonResponse({
    #             "status": "error",
    #             "message": "Invalid SOS data"
    #         })

    #     # ======================================================
    #     # CHECK LOCATION RANGE
    #     # ======================================================

    #     if latitude < -90 or latitude > 90:

    #         return JsonResponse({
    #             "status": "error",
    #             "message": "Invalid latitude"
    #         })

    #     if longitude < -180 or longitude > 180:

    #         return JsonResponse({
    #             "status": "error",
    #             "message": "Invalid longitude"
    #         })

    #     # ======================================================
    #     # FIND USER
    #     # ======================================================

    #     user = None

    #     try:

    #         user = User_table.objects.get(
    #             LOGIN=lid
    #         )

    #     except User.DoesNotExist:

    #         user = None

    #     # ======================================================
    #     # SAVE SOS
    #     # ======================================================

    #     sos = EmergencySOS.objects.create(

    #         USER=user,

    #         latitude=latitude,

    #         longitude=longitude,

    #         status=status
    #     )

    #     # ======================================================
    #     # SUCCESS RESPONSE
    #     # ======================================================

    #     return JsonResponse({

    #         "status": "ok",

    #         "message":
    #             "SOS alert sent successfully",

    #         "sos_id":
    #             sos.id,

    #         "latitude":
    #             sos.latitude,

    #         "longitude":
    #             sos.longitude,

    #         "emergency_status":
    #             sos.status
    #     })

    # except json.JSONDecodeError:

    #     return JsonResponse({
    #         "status": "error",
    #         "message": "Invalid JSON data"
    #     })

    # except Exception as e:

    #     print("SOS ERROR:", e)

    #     return JsonResponse({
    #         "status": "error",
    #         "message": "Unable to process SOS request"
    #     })

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

            # If LOGIN is a ForeignKey to Django User,
            # use LOGIN_id here.

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
        return JsonResponse({"status": "error","message": "POST request required"})
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
        return JsonResponse({"status": "error","message": "Login ID missing"})
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
        return JsonResponse({"status": "error","message": "ERT user not found"})

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
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
    

# import json
# import pickle
# import requests

# from django.http import JsonResponse
# from django.shortcuts import render


# # ============================================================
# # IMPORT YOUR FUNCTIONS
# # ============================================================

# # IMPORTANT:
# # Change this import according to where these functions are defined.
# #
# # Example:
# # from .utils import get_rivers_near_location, getmaindata


# # ============================================================
# # WEATHERBIT API KEY
# # ============================================================

# API_KEY = '2b4e8c141af04762ac56c790177e7e46'


# # ============================================================
# # SOIL TYPES
# # ============================================================

# st = [
#     'Fluvisols',
#     'Andosols',
#     'Arenosols',
#     'Chernozem',
#     'Gleysols',
#     'Histosols',
#     'Kastanozems',
#     'Luvisols',
#     'Nitisols',
#     'Regosols',
#     'Vertisols',
#     'Solonchaks',
#     'Podzols',
#     'Alisols',
#     'Cambisols',
#     'Calcisols',
#     'Phaeozems',
#     'Acrisols',
#     'Plinthosols',
#     'Clay',
#     'Unknown'
# ]


# # ============================================================
# # MAP START
# # ============================================================

# def map_start(request):

#     return render(
#         request,
#         'admin/map_start.html'
#     )


# # ============================================================
# # DISASTER PREDICTION
# # ============================================================

# def get_predict(request):

#     # ========================================================
#     # ONLY POST REQUEST
#     # ========================================================

#     if request.method != 'POST':

#         return render(
#             request,
#             "admin/map_start.html"
#         )

#     try:

#         # ====================================================
#         # 1. GET LATITUDE AND LONGITUDE
#         # ====================================================

#         try:

#             lat = float(
#                 request.POST.get('lat')
#             )

#             lon = float(
#                 request.POST.get('lon')
#             )

#         except (TypeError, ValueError):

#             return render(
#                 request,
#                 "admin/result.html",
#                 {
#                     "val": "Invalid latitude or longitude"
#                 }
#             )


#         print("========================================")
#         print("LOCATION")
#         print("========================================")
#         print("Latitude :", lat)
#         print("Longitude:", lon)
#         print("========================================")


#         # ====================================================
#         # 2. GET RIVER DISTANCE
#         # ====================================================

#         distance_str = 1000.0

#         try:

#             river_data = get_rivers_near_location(
#                 lat,
#                 lon
#             )

#             if (
#                 isinstance(river_data, dict)
#                 and "error" in river_data
#             ):

#                 print("River API Error:")
#                 print(
#                     river_data["error"]
#                 )

#             else:

#                 print("Rivers near location:")

#                 for river in river_data:

#                     if isinstance(
#                         river.get("distance_km"),
#                         (float, int)
#                     ):

#                         distance_str = float(
#                             river["distance_km"]
#                         )

#                         break

#         except Exception as e:

#             print(
#                 "River API Exception:",
#                 str(e)
#             )


#         # ====================================================
#         # 3. GET ELEVATION, SOIL AND SLOPE
#         # ====================================================

#         try:

#             elevation, soil_type, slope_angle = getmaindata(
#                 float(lat),
#                 float(lon)
#             )

#         except Exception as e:

#             print(
#                 "Elevation/Soil/Slope error:",
#                 str(e)
#             )

#             elevation = 0.0

#             soil_type = "Unknown"

#             slope_angle = 0.0


#         print("========================================")
#         print("ENVIRONMENT DATA")
#         print("========================================")

#         print(
#             "Elevation    :",
#             elevation
#         )

#         print(
#             "Soil         :",
#             soil_type
#         )

#         print(
#             "Slope        :",
#             slope_angle
#         )

#         print(
#             "River Dist.  :",
#             distance_str
#         )

#         print("========================================")


#         # ====================================================
#         # 4. GET WEATHER DATA
#         # ====================================================

#         weather_data = {}

#         try:

#             api_url = (
#                 f"https://api.weatherbit.io/v2.0/current"
#                 f"?lat={lat}"
#                 f"&lon={lon}"
#                 f"&key={API_KEY}"
#             )

#             response = requests.get(
#                 api_url,
#                 timeout=10
#             )

#             response.raise_for_status()

#             weather_data = response.json()

#             print("========================================")
#             print("WEATHER DATA")
#             print("========================================")
#             print(weather_data)
#             print("========================================")

#         except Exception as e:

#             print(
#                 "Weather API Error:",
#                 str(e)
#             )

#             weather_data = {}


#         # ====================================================
#         # 5. LOAD KNN MODEL
#         # ====================================================

#         model_path = (
#             r"E:\Regional\disaster\disaster_management"
#             r"\myapp\knn_model.pkl"
#         )

#         try:

#             with open(
#                 model_path,
#                 'rb'
#             ) as file:

#                 knn = pickle.load(file)

#         except Exception as e:

#             return JsonResponse(
#                 {
#                     "error": "Unable to load KNN model",
#                     "details": str(e)
#                 },
#                 status=500
#             )


#         print("========================================")
#         print("KNN MODEL")
#         print("========================================")

#         print(
#             "Expected features:",
#             knn.n_features_in_
#         )

#         print("========================================")


#         # ====================================================
#         # 6. DUMMY DISASTER DATA
#         # ====================================================
#         #
#         # IMPORTANT:
#         #
#         # This is ONLY for testing.
#         #
#         # These values represent a HIGH LANDSLIDE-RISK
#         # environmental condition.
#         #
#         # Feature order MUST be exactly the same as
#         # the order used while training the KNN model.
#         #
#         # 1. Latitude
#         # 2. Longitude
#         # 3. Elevation
#         # 4. River Distance
#         # 5. Slope
#         # 6. Precipitation
#         # 7. Soil Index
#         # 8. Humidity
#         # 9. Temperature
#         #
#         # ====================================================

#         dummy_mode = True


#         if dummy_mode:

#             print("========================================")
#             print("USING DUMMY DISASTER DATA")
#             print("========================================")


#             # ------------------------------------------------
#             # LOCATION
#             # ------------------------------------------------

#             dummy_lat = 11.5560

#             dummy_lon = 76.0405


#             # ------------------------------------------------
#             # HIGH ELEVATION
#             # ------------------------------------------------

#             dummy_elevation = 1500.0


#             # ------------------------------------------------
#             # VERY CLOSE TO RIVER
#             # ------------------------------------------------

#             dummy_river_distance = 0.02


#             # ------------------------------------------------
#             # VERY STEEP SLOPE
#             # ------------------------------------------------

#             dummy_slope = 70.0


#             # ------------------------------------------------
#             # VERY HEAVY RAINFALL
#             # ------------------------------------------------

#             dummy_precipitation = 400.0


#             # ------------------------------------------------
#             # CLAY SOIL
#             # ------------------------------------------------

#             dummy_soil = "Clay"


#             # ------------------------------------------------
#             # VERY HIGH HUMIDITY
#             # ------------------------------------------------

#             dummy_humidity = 99.0


#             # ------------------------------------------------
#             # TEMPERATURE
#             # ------------------------------------------------

#             dummy_temperature = 18.0


#             # ------------------------------------------------
#             # SOIL ENCODING
#             # ------------------------------------------------

#             if dummy_soil in st:

#                 soil_index = st.index(
#                     dummy_soil
#                 )

#             else:

#                 soil_index = st.index(
#                     "Unknown"
#                 )


#             # ------------------------------------------------
#             # FINAL DUMMY ROW
#             # ------------------------------------------------

#             row = [

#                 dummy_lat,

#                 dummy_lon,

#                 dummy_elevation,

#                 dummy_river_distance,

#                 dummy_slope,

#                 dummy_precipitation,

#                 soil_index,

#                 dummy_humidity,

#                 dummy_temperature

#             ]


#         else:

#             # =================================================
#             # REAL DATA MODE
#             # =================================================

#             print("========================================")
#             print("USING REAL API DATA")
#             print("========================================")


#             # -------------------------------------------------
#             # SOIL ENCODING
#             # -------------------------------------------------

#             if soil_type in st:

#                 soil_index = st.index(
#                     soil_type
#                 )

#             else:

#                 soil_index = st.index(
#                     "Unknown"
#                 )


#             # -------------------------------------------------
#             # DEFAULT WEATHER VALUES
#             # -------------------------------------------------

#             precipitation = 0.0

#             humidity = 0.0

#             temperature = 0.0


#             # -------------------------------------------------
#             # EXTRACT WEATHER VALUES
#             # -------------------------------------------------

#             try:

#                 if (
#                     "data" in weather_data
#                     and
#                     len(weather_data["data"]) > 0
#                 ):

#                     weather = weather_data["data"][0]


#                     precipitation = float(
#                         weather.get(
#                             "precip",
#                             0
#                         )
#                     )


#                     humidity = float(
#                         weather.get(
#                             "rh",
#                             0
#                         )
#                     )


#                     temperature = float(
#                         weather.get(
#                             "temp",
#                             0
#                         )
#                     )

#             except Exception as e:

#                 print(
#                     "Weather value extraction error:",
#                     str(e)
#                 )


#             # -------------------------------------------------
#             # FINAL REAL DATA ROW
#             # -------------------------------------------------

#             row = [

#                 float(lat),

#                 float(lon),

#                 float(elevation),

#                 float(distance_str),

#                 float(slope_angle),

#                 precipitation,

#                 soil_index,

#                 humidity,

#                 temperature

#             ]


#         # ====================================================
#         # 7. PRINT FINAL INPUT
#         # ====================================================

#         print("========================================")
#         print("FINAL INPUT TO KNN")
#         print("========================================")


#         print(
#             "Latitude       :",
#             row[0]
#         )


#         print(
#             "Longitude      :",
#             row[1]
#         )


#         print(
#             "Elevation      :",
#             row[2]
#         )


#         print(
#             "River Distance :",
#             row[3]
#         )


#         print(
#             "Slope          :",
#             row[4]
#         )


#         print(
#             "Precipitation  :",
#             row[5]
#         )


#         print(
#             "Soil Index     :",
#             row[6]
#         )


#         print(
#             "Humidity       :",
#             row[7]
#         )


#         print(
#             "Temperature    :",
#             row[8]
#         )


#         print("----------------------------------------")

#         print(
#             "Complete Row:"
#         )

#         print(row)


#         print("----------------------------------------")

#         print(
#             "Number of features:",
#             len(row)
#         )


#         print(
#             "Model expects      :",
#             knn.n_features_in_
#         )


#         print("========================================")


#         # ====================================================
#         # 8. CHECK FEATURE COUNT
#         # ====================================================

#         if len(row) != knn.n_features_in_:

#             raise ValueError(
#                 f"Expected "
#                 f"{knn.n_features_in_} features, "
#                 f"but got {len(row)}"
#             )


#         # ====================================================
#         # 9. KNN PREDICTION
#         # ====================================================

#         res = knn.predict(
#             [row]
#         )


#         prediction = int(
#             res[0]
#         )


#         print("========================================")
#         print("KNN PREDICTION")
#         print("========================================")

#         print(
#             "Raw result:",
#             res
#         )

#         print(
#             "Prediction:",
#             prediction
#         )

#         print("========================================")


#         # ====================================================
#         # 10. DISASTER / NON-DISASTER
#         # ====================================================

#         if prediction == 1:

#             status = "not ok"

#             result = "Disaster"

#             print(
#                 "🚨 RESULT: DISASTER"
#             )

#         else:

#             status = "ok"

#             result = "Non-Disaster"

#             print(
#                 "✅ RESULT: NON-DISASTER"
#             )


#         # ====================================================
#         # 11. RESULT PAGE DATA
#         # ====================================================

#         context = {

#             "status": status,

#             "val": result,

#             "weather_data": weather_data,

#             # Actual soil from API
#             "st": (
#                 dummy_soil
#                 if dummy_mode
#                 else soil_type
#             ),

#             # Actual river distance used by model
#             "river": row[3],

#             # Actual elevation used by model
#             "altitude": row[2],

#             # Actual rainfall used by model
#             "rainfall": row[5],

#             "city_name": "",

#             "prediction": prediction,

#             "latitude": row[0],

#             "longitude": row[1],

#             "slope": row[4],

#             "humidity": row[7],

#             "temperature": row[8],

#             "dummy_mode": dummy_mode

#         }


#         # ====================================================
#         # 12. RENDER RESULT
#         # ====================================================

#         return render(
#             request,
#             "admin/result.html",
#             context
#         )


#     # ========================================================
#     # VALUE ERROR
#     # ========================================================

#     except ValueError as e:

#         print(
#             "Prediction ValueError:",
#             str(e)
#         )

#         return JsonResponse(
#             {
#                 "error": "Prediction failed",

#                 "details": str(e)
#             },
#             status=500
#         )


#     # ========================================================
#     # GENERAL ERROR
#     # ========================================================

#     except Exception as e:

#         print(
#             "Prediction Error:",
#             str(e)
#         )

#         return JsonResponse(
#             {
#                 "error": "Prediction failed",

#                 "details": str(e)
#             },
#             status=500
#         )



# ###############################



# # import requests
# # import joblib
# # from .sample import getmaindata
# # from .river import get_rivers_near_location

# # API_KEY = 'cebbc9586ddf420fba18e2a5993a7477'

# # def webmap_start(request):
# #     return render(request,'admin/map_start.html')

# # def webget_predict(request):
# #     if request.method == 'POST':
# #         try:

# #             lat = float(request.POST['lat'])
# #             lon = float(request.POST['lon'])
# #             distance_str = "1000"

# #             # Get river data
# #             river_data = get_rivers_near_location(lat, lon)
# #             if "error" in river_data:
# #                 print(river_data["error"])
# #             else:
# #                 print(f"Rivers near location ({lat}, {lon}):")
# #                 for river in river_data:
# #                     if isinstance(river["distance_km"], (float, int)):
# #                         distance_str = float(river['distance_km'])
# #                         break
# #                     else:
# #                         distance_str = "Distance not available"
# #                         break

# #             # Fetch elevation, soil type, and slope angle data
# #             elevation, soil_type, slope_angle = getmaindata(float(lat), float(lon))
# #             print(elevation, soil_type, slope_angle, distance_str)

# #             if lat is None or lon is None:
# #                 return render(request,"result.html",{"val":"invalid"})
# #             # Fetch weather data
# #             api_url = f'https://api.weatherbit.io/v2.0/current?lat={lat}&lon={lon}&key={API_KEY}'
# #             response = requests.get(api_url)
# #             weather_data = response.json()
# #             print(weather_data)

# #         except json.JSONDecodeError as e:
# #             print(e)
# #             return render(request, "ERT/ert_result.html", {"val": "invalid"})

# #             # return JsonResponse({'error': 'Invalid JSON'}, status=400)

# #     # Load the KNN model
# #     # knn = joblib.load(r"C:\Users\akash\PycharmProjects\disaster_weatherprediction\myapp\knn-model.joblib")
# #     with open('knn_model.pkl', 'rb') as file:
# #         knn = pickle.load(file)
# #         # knn=joblib.load("knn-model.joblib")
# #     # res = knn.predict([row])

# #     # Ensure the input data matches the expected dimensions
# #     try:
# #         # Adjust the row to have the correct number of features
# #         st = [
# #             'Fluvisols',
# #             'Andosols',
# #             'Arenosols',
# #             'Chernozem',
# #             'Gleysols',
# #             'Histosols',
# #             'Kastanozems',
# #             'Luvisols',
# #             'Nitisols',
# #             'Regosols',
# #             'Vertisols',
# #             'Solonchaks',
# #             'Podzols',
# #             'Alisols',
# #             'Cambisols',
# #             'Calcisols',
# #             'Phaeozems',
# #             'Acrisols',
# #             'Plinthosols',
# #             'Clay'
# #         ]
# #         try:


# #             row = [float(lat), float(lon), float(elevation), float(distance_str), float(slope_angle),weather_data['data'][0]['precip'],st.index(soil_type),weather_data['data'][0]['rh'],weather_data['data'][0]['rh']]  # Adjust as necessary
# #         except:
# #             row = [float(lat), float(lon), float(0), float(distance_str), float(slope_angle),
# #                    0, st.index(soil_type), 0,
# #                    1]  # Adjust as necessary

# #         if len(row) != knn.n_features_in_:
# #             raise ValueError(f"Expected {knn.n_features_in_} features, but got {len(row)}")

# #         # Make the prediction
# #         res = knn.predict([row])
# #         print(res, "++++++++++++++++++")

# #         if res[0] == 0:
# #             return render(request,"result.html",{'status': 'ok', 'val': 'Non-Disaster','weather_data':weather_data,'st':soil_type,'river':distance_str,'altitude':0,'rainfall':"",'city_name':""})
# #         else:
# #             return HttpResponse({'status': 'not ok', 'val': 'Disaster','weather_data':weather_data,'st':soil_type,'river':distance_str,'altitude':elevation,'rainfall':'','city_name':''})

# #     except ValueError as e:
# #         print("Error in prediction:", str(e))
# #         return JsonResponse({'error': 'Prediction failed', 'details': str(e)}, status=500)

# #     return JsonResponse({'status': 'not ok', 'val': 'Disaster','weather_data':weather_data})

# # def map_start(request):
# #     return render(request,'map_start.html')

# # def get_predict(request):
# #     if request.method == 'POST':
# #         try:

# #             lat = float(request.POST['lat'])
# #             lon = float(request.POST['lon'])
# #             distance_str = "1000"

# #             # Get river data
# #             river_data = get_rivers_near_location(lat, lon)
# #             if "error" in river_data:
# #                 print(river_data["error"])
# #             else:
# #                 print(f"Rivers near location ({lat}, {lon}):")
# #                 for river in river_data:
# #                     if isinstance(river["distance_km"], (float, int)):
# #                         distance_str = float(river['distance_km'])
# #                         break
# #                     else:
# #                         distance_str = "Distance not available"
# #                         break

# #             # Fetch elevation, soil type, and slope angle data
# #             elevation, soil_type, slope_angle = getmaindata(float(lat), float(lon))
# #             print(elevation, soil_type, slope_angle, distance_str)

# #             if lat is None or lon is None:
# #                 return render(request,"result.html",{"val":"invalid"})
# #             # Fetch weather data
# #             api_url = f'https://api.weatherbit.io/v2.0/current?lat={lat}&lon={lon}&key={API_KEY}'
# #             response = requests.get(api_url)
# #             weather_data = response.json()
# #             print(weather_data)

# #         except json.JSONDecodeError as e:
# #             print(e)
# #             return render(request, "result.html", {"val": "invalid"})

# #             # return JsonResponse({'error': 'Invalid JSON'}, status=400)

# #     # Load the KNN model
# #     # knn = joblib.load(r"C:\Users\akash\PycharmProjects\disaster_weatherprediction\myapp\knn-model.joblib")
# #     with open('knn_model.pkl', 'rb') as file:
# #         knn = pickle.load(file)
# #         # knn=joblib.load("knn-model.joblib")
# #     # res = knn.predict([row])

# #     # Ensure the input data matches the expected dimensions
# #     try:
# #         # Adjust the row to have the correct number of features
# #         st = [
# #             'Fluvisols',
# #             'Andosols',
# #             'Arenosols',
# #             'Chernozem',
# #             'Gleysols',
# #             'Histosols',
# #             'Kastanozems',
# #             'Luvisols',
# #             'Nitisols',
# #             'Regosols',
# #             'Vertisols',
# #             'Solonchaks',
# #             'Podzols',
# #             'Alisols',
# #             'Cambisols',
# #             'Calcisols',
# #             'Phaeozems',
# #             'Acrisols',
# #             'Plinthosols',
# #             'Clay'

# #         ]
# #         try:


# #             row = [float(lat), float(lon), float(elevation), float(distance_str), float(slope_angle),weather_data['data'][0]['precip'],st.index(soil_type),weather_data['data'][0]['rh'],weather_data['data'][0]['rh']]  # Adjust as necessary
# #         except:
# #             row = [float(lat), float(lon), float(0), float(distance_str), float(slope_angle),
# #                    0, st.index(soil_type), 0,
# #                    1]  # Adjust as necessary

# #         if len(row) != knn.n_features_in_:
# #             raise ValueError("Expected {knn.n_features_in_} features, but got {len(row)}")


# #         # Make the prediction
# #         res = knn.predict([row])
# #         print(res, "++++++++++++++++++")

# #         if res[0] == 0:
# #             return render(request,"result.html",{'status': 'ok', 'val': 'Non-Disaster','weather_data':weather_data,'st':soil_type,'river':distance_str,'altitude':0,'rainfall':"",'city_name':""})
# #         else:
# #             return HttpResponse({'status': 'not ok', 'val': 'Disaster','weather_data':weather_data,'st':soil_type,'river':distance_str,'altitude':elevation,'rainfall':'','city_name':''})

# #     except ValueError as e:
# #         print("Error in prediction:", str(e))
# #         return JsonResponse({'error': 'Prediction failed', 'details': str(e)}, status=500)

# #     return JsonResponse({'status': 'not ok', 'val': 'Disaster','weather_data':weather_data})

# # ========================================================= # GET WEATHER DATA # ========================================================= 


# # import pickle
# # import requests

# # from datetime import datetime

# # from django.shortcuts import render
# # from django.http import JsonResponse

# # from .sample import getmaindata
# # from .river import get_rivers_near_location
# # from .models import Prediction


# # # =========================================================
# # # WEATHER API KEY
# # # =========================================================

# # API_KEY = "cebbc9586ddf420fba18e2a5993a7477"
# # # API_KEY = "02275f4e0a7d3765813425c48457f53c"


# # # =========================================================
# # # SOIL TYPES
# # # MUST MATCH TRAINING DATA ORDER
# # # =========================================================

# # SOIL_TYPES = [
# #     'Fluvisols',
# #     'Andosols',
# #     'Arenosols',
# #     'Chernozem',
# #     'Gleysols',
# #     'Histosols',
# #     'Kastanozems',
# #     'Luvisols',
# #     'Nitisols',
# #     'Regosols',
# #     'Vertisols',
# #     'Solonchaks',
# #     'Podzols',
# #     'Alisols',
# #     'Cambisols',
# #     'Calcisols',
# #     'Phaeozems',
# #     'Acrisols',
# #     'Plinthosols',
# #     'Clay'
# # ]


# # # =========================================================
# # # LOAD KNN MODEL
# # # =========================================================

# # def load_knn_model():

# #     try:

# #         model_path = r"E:\Regional\disaster\disaster_management\knn_model.pkl"

# #         with open(model_path, "rb") as file:
# #             model = pickle.load(file)

# #         return model

# #     except Exception as e:

# #         print("KNN model loading error:", e)

# #         return None


# # # =========================================================
# # # MAP PAGE
# # # =========================================================

# # def webmap_start(request):

# #     return render(
# #         request,
# #         "admin/map_start.html"
# #     )


# # def map_start(request):

# #     return render(
# #         request,
# #         "map_start.html"
# #     )


# # # =========================================================
# # # GET RIVER DISTANCE
# # # =========================================================

# # def get_river_distance(lat, lon):

# #     default_distance = 1000.0

# #     try:

# #         river_data = get_rivers_near_location(
# #             float(lat),
# #             float(lon)
# #         )

# #         if not river_data:

# #             print("No river data found.")

# #             return default_distance


# #         if isinstance(river_data, dict):

# #             if "error" in river_data:

# #                 print(
# #                     "River API error:",
# #                     river_data["error"]
# #                 )

# #                 return default_distance

# #             river_data = [river_data]


# #         for river in river_data:

# #             distance = river.get("distance_km")

# #             if distance is not None:

# #                 try:

# #                     return float(distance)

# #                 except (TypeError, ValueError):

# #                     continue


# #     except Exception as e:

# #         print(
# #             "River distance error:",
# #             e
# #         )


# #     return default_distance


# # # =========================================================
# # # GET WEATHER DATA
# # # =========================================================

# # def get_weather_data(lat, lon):

# #     try:

# #         if not API_KEY:

# #             print("Weather API key is missing.")

# #             return {}


# #         api_url = (
# #             "https://api.weatherbit.io/v2.0/current"
# #             f"?lat={lat}"
# #             f"&lon={lon}"
# #             f"&key={API_KEY}"
# #         )


# #         response = requests.get(
# #             api_url,
# #             timeout=15
# #         )


# #         print(
# #             "Weather API status:",
# #             response.status_code
# #         )


# #         if response.status_code != 200:

# #             print(
# #                 "Weather API response:",
# #                 response.text
# #             )

# #             return {}


# #         weather_data = response.json()


# #         if not weather_data.get("data"):

# #             print("Weather data is empty.")

# #             return {}


# #         return weather_data


# #     except requests.RequestException as e:

# #         print(
# #             "Weather API error:",
# #             e
# #         )

# #         return {}


# #     except ValueError as e:

# #         print(
# #             "Weather JSON error:",
# #             e
# #         )

# #         return {}


# #     except Exception as e:

# #         print(
# #             "Weather error:",
# #             e
# #         )

# #         return {}


# # # =========================================================
# # # EXTRACT WEATHER VALUES
# # # =========================================================

# # def extract_weather_values(weather_data):

# #     default_weather = {

# #         "precip": 0.0,

# #         "rh": 0.0,

# #         "temp": 0.0
# #     }


# #     if not weather_data:

# #         return default_weather


# #     try:

# #         current = weather_data["data"][0]


# #         precip = float(
# #             current.get(
# #                 "precip",
# #                 0.0
# #             )
# #         )


# #         rh = float(
# #             current.get(
# #                 "rh",
# #                 0.0
# #             )
# #         )


# #         temp = float(
# #             current.get(
# #                 "temp",
# #                 0.0
# #             )
# #         )


# #         return {

# #             "precip": precip,

# #             "rh": rh,

# #             "temp": temp

# #         }


# #     except Exception as e:

# #         print(
# #             "Weather value extraction error:",
# #             e
# #         )

# #         return default_weather


# # # =========================================================
# # # GET PREDICTION
# # # =========================================================

# # def get_prediction(lat, lon):

# #     # -----------------------------------------------------
# #     # 1. RIVER DISTANCE
# #     # -----------------------------------------------------

# #     river_distance = get_river_distance(
# #         lat,
# #         lon
# #     )


# #     # -----------------------------------------------------
# #     # 2. ELEVATION / SOIL / SLOPE
# #     # -----------------------------------------------------

# #     try:

# #         elevation, soil_type, slope_angle = getmaindata(
# #             float(lat),
# #             float(lon)
# #         )


# #         print(
# #             "Elevation:",
# #             elevation
# #         )

# #         print(
# #             "Soil Type:",
# #             soil_type
# #         )

# #         print(
# #             "Slope Angle:",
# #             slope_angle
# #         )


# #     except Exception as e:

# #         print(
# #             "Environmental data error:",
# #             e
# #         )

# #         elevation = 0.0

# #         soil_type = "Clay"

# #         slope_angle = 0.0


# #     # -----------------------------------------------------
# #     # 3. CONVERT NUMERIC VALUES
# #     # -----------------------------------------------------

# #     try:

# #         elevation = float(elevation)

# #     except (TypeError, ValueError):

# #         elevation = 0.0


# #     try:

# #         slope_angle = float(slope_angle)

# #     except (TypeError, ValueError):

# #         slope_angle = 0.0


# #     try:

# #         river_distance = float(river_distance)

# #     except (TypeError, ValueError):

# #         river_distance = 1000.0


# #     # -----------------------------------------------------
# #     # 4. SOIL ENCODING
# #     # -----------------------------------------------------

# #     if soil_type not in SOIL_TYPES:

# #         print(
# #             "Unknown soil type:",
# #             soil_type
# #         )

# #         soil_type = "Clay"


# #     soil_encoded = SOIL_TYPES.index(
# #         soil_type
# #     )


# #     # -----------------------------------------------------
# #     # 5. WEATHER
# #     # -----------------------------------------------------

# #     weather_data = get_weather_data(
# #         lat,
# #         lon
# #     )


# #     weather_values = extract_weather_values(
# #         weather_data
# #     )


# #     rainfall = weather_values["precip"]

# #     humidity = weather_values["rh"]

# #     temperature = weather_values["temp"]


# #     # -----------------------------------------------------
# #     # IMPORTANT:
# #     # NEVER RETURN NONE FOR weather_data
# #     # -----------------------------------------------------

# #     if weather_data is None:

# #         weather_data = {}


# #     # -----------------------------------------------------
# #     # 6. MODEL INPUT
# #     #
# #     # MUST MATCH TRAINING ORDER
# #     # -----------------------------------------------------

# #     row = [

# #         float(lat),

# #         float(lon),

# #         float(elevation),

# #         float(river_distance),

# #         float(slope_angle),

# #         float(rainfall),

# #         float(soil_encoded),

# #         float(humidity),

# #         float(temperature)

# #     ]


# #     print(
# #         "Prediction input:",
# #         row
# #     )


# #     # -----------------------------------------------------
# #     # 7. LOAD MODEL
# #     # -----------------------------------------------------

# #     knn = load_knn_model()


# #     if knn is None:

# #         return {

# #             "success": False,

# #             "error": "Unable to load KNN model."

# #         }


# #     # -----------------------------------------------------
# #     # 8. CHECK FEATURE COUNT
# #     # -----------------------------------------------------

# #     try:

# #         expected_features = knn.n_features_in_


# #         print(
# #             "Model expects features:",
# #             expected_features
# #         )


# #         print(
# #             "Provided features:",
# #             len(row)
# #         )


# #     except AttributeError:

# #         expected_features = len(row)


# #     if len(row) != expected_features:

# #         return {

# #             "success": False,

# #             "error": (
# #                 f"Feature count mismatch. "
# #                 f"Model expects {expected_features} "
# #                 f"features, but received "
# #                 f"{len(row)} features."
# #             )

# #         }


# #     # -----------------------------------------------------
# #     # 9. PREDICTION
# #     # -----------------------------------------------------

# #     try:

# #         prediction = knn.predict(
# #             [row]
# #         )


# #         result = int(
# #             prediction[0]
# #         )


# #         print(
# #             "Prediction result:",
# #             result
# #         )


# #     except Exception as e:

# #         print(
# #             "Model prediction error:",
# #             e
# #         )


# #         return {

# #             "success": False,

# #             "error": str(e)

# #         }


# #     # -----------------------------------------------------
# #     # 10. STATUS
# #     # -----------------------------------------------------

# #     if result == 0:

# #         status = "Non-Disaster"

# #         risk = "Low"

# #     else:

# #         status = "Disaster"

# #         risk = "High"


# #     # -----------------------------------------------------
# #     # 11. RETURN RESULT
# #     # -----------------------------------------------------

# #     return {

# #         "success": True,

# #         "prediction": result,

# #         "status": status,

# #         "risk": risk,

# #         "latitude": float(lat),

# #         "longitude": float(lon),

# #         "elevation": elevation,

# #         "soil_type": soil_type,

# #         "river_distance": river_distance,

# #         "slope_angle": slope_angle,

# #         "rainfall": rainfall,

# #         "humidity": humidity,

# #         "temperature": temperature,

# #         "weather_data": weather_data,

# #         "features": row

# #     }


# # # =========================================================
# # # WEB PREDICTION
# # # =========================================================

# # def webget_predict(request):

# #     if request.method != "POST":

# #         return render(
# #             request,
# #             "admin/result.html",
# #             {
# #                 "status": "error",
# #                 "val": "Invalid Request",
# #                 "message": "POST request required."
# #             }
# #         )


# #     try:

# #         # -------------------------------------------------
# #         # GET LATITUDE
# #         # -------------------------------------------------

# #         lat_value = request.POST.get("lat")


# #         # -------------------------------------------------
# #         # GET LONGITUDE
# #         # -------------------------------------------------

# #         lon_value = request.POST.get("lon")


# #         # -------------------------------------------------
# #         # CHECK
# #         # -------------------------------------------------

# #         if not lat_value or not lon_value:

# #             return render(
# #                 request,
# #                 "admin/result.html",
# #                 {
# #                     "status": "error",
# #                     "val": "Invalid Location",
# #                     "message": (
# #                         "Latitude and longitude are required."
# #                     )
# #                 }
# #             )


# #         # -------------------------------------------------
# #         # CONVERT
# #         # -------------------------------------------------

# #         lat = float(lat_value)

# #         lon = float(lon_value)


# #         # -------------------------------------------------
# #         # VALIDATE LATITUDE
# #         # -------------------------------------------------

# #         if not -90 <= lat <= 90:

# #             return render(
# #                 request,
# #                 "admin/result.html",
# #                 {
# #                     "status": "error",
# #                     "val": "Invalid Latitude",
# #                     "message": (
# #                         "Latitude must be between "
# #                         "-90 and 90."
# #                     )
# #                 }
# #             )


# #         # -------------------------------------------------
# #         # VALIDATE LONGITUDE
# #         # -------------------------------------------------

# #         if not -180 <= lon <= 180:

# #             return render(
# #                 request,
# #                 "admin/result.html",
# #                 {
# #                     "status": "error",
# #                     "val": "Invalid Longitude",
# #                     "message": (
# #                         "Longitude must be between "
# #                         "-180 and 180."
# #                     )
# #                 }
# #             )


# #         # -------------------------------------------------
# #         # GET PREDICTION
# #         # -------------------------------------------------

# #         result = get_prediction(
# #             lat,
# #             lon
# #         )


# #         # -------------------------------------------------
# #         # PREDICTION FAILED
# #         # -------------------------------------------------

# #         if not result["success"]:

# #             return render(
# #                 request,
# #                 "admin/result.html",
# #                 {
# #                     "status": "error",
# #                     "val": "Prediction Failed",
# #                     "message": result["error"]
# #                 }
# #             )


# #         # =================================================
# #         # SAVE PREDICTION
# #         # =================================================

# #         obj = Prediction()


# #         obj.date = datetime.now()


# #         obj.value = result["status"]

# #         obj.risk = result["risk"]

# #         obj.river = result["river_distance"]

# #         obj.soil_type = result["soil_type"]

# #         obj.slope = result["slope_angle"]

# #         obj.altitude = result["elevation"]

# #         obj.rainfall = result["rainfall"]

# #         obj.humidity = result["humidity"]

# #         obj.temperature = result["temperature"]


# #         # =================================================
# #         # FIX:
# #         # weather_data MUST NOT BE NULL
# #         # =================================================

# #         weather_data = result.get(
# #             "weather_data",
# #             {}
# #         )


# #         if weather_data is None:

# #             weather_data = {}


# #         obj.weather_data = weather_data


# #         obj.latitude = result["latitude"]

# #         obj.longitude = result["longitude"]


# #         obj.save()


# #         print(
# #             "Prediction saved successfully."
# #         )


# #         # -------------------------------------------------
# #         # SUCCESS PAGE
# #         # -------------------------------------------------

# #         return render(
# #             request,
# #             "admin/result.html",
# #             {
# #                 "status": "ok",

# #                 "val": result["status"],

# #                 "risk": result["risk"],

# #                 "st": result["soil_type"],

# #                 "river": result["river_distance"],

# #                 "altitude": result["elevation"],

# #                 "slope": result["slope_angle"],

# #                 "rainfall": result["rainfall"],

# #                 "humidity": result["humidity"],

# #                 "temperature": result["temperature"],

# #                 "latitude": result["latitude"],

# #                 "longitude": result["longitude"],

# #                 "weather_data": weather_data
# #             }
# #         )


# #     except ValueError as e:

# #         print(
# #             "Invalid input:",
# #             e
# #         )


# #         return render(
# #             request,
# #             "admin/result.html",
# #             {
# #                 "status": "error",
# #                 "val": "Invalid Input",
# #                 "message": (
# #                     "Invalid latitude or longitude."
# #                 )
# #             }
# #         )


# #     except Exception as e:

# #         print(
# #             "Prediction error:",
# #             e
# #         )


# #         return render(
# #             request,
# #             "admin/result.html",
# #             {
# #                 "status": "error",
# #                 "val": "Prediction Error",
# #                 "message": str(e)
# #             }
# #         )
# #########last code
# # API_KEY = '2b4e8c141af04762ac56c790177e7e46'

# # def map_start(request):
# #     return render(request,'admin/map_start.html')

# # def get_predict(request):
# #     if request.method == 'POST':
# #         try:

# #             lat = float(request.POST['lat'])
# #             lon = float(request.POST['lon'])
# #             distance_str = "1000"

# #             # Get river data
# #             river_data = get_rivers_near_location(lat, lon)
# #             if "error" in river_data:
# #                 print(river_data["error"])
# #             else:
# #                 print(f"Rivers near location ({lat}, {lon}):")
# #                 for river in river_data:
# #                     if isinstance(river["distance_km"], (float, int)):
# #                         distance_str = float(river['distance_km'])
# #                         break
# #                     else:
# #                         distance_str = "Distance not available"
# #                         break

# #             # Fetch elevation, soil type, and slope angle data
# #             elevation, soil_type, slope_angle = getmaindata(float(lat), float(lon))
# #             print(elevation, soil_type, slope_angle, distance_str)

# #             if lat is None or lon is None:
# #                 return render(request,"result.html",{"val":"invalid"})
# #             # Fetch weather data
# #             api_url = f'https://api.weatherbit.io/v2.0/current?lat={lat}&lon={lon}&key={API_KEY}'
# #             response = requests.get(api_url)
# #             weather_data = response.json()
# #             print(weather_data)

# #         except json.JSONDecodeError as e:
# #             print(e)
# #             return render(request, "admin/result.html", {"val": "invalid"})

# #     with open(r'E:\Regional\disaster\disaster_management\myapp\knn_model.pkl', 'rb') as file:
# #         knn = pickle.load(file)
# #     # Ensure the input data matches the expected dimensions
# #     try:
# #         # Adjust the row to have the correct number of features
# #         st = [
# #             'Fluvisols',
# #             'Andosols',
# #             'Arenosols',
# #             'Chernozem',
# #             'Gleysols',
# #             'Histosols',
# #             'Kastanozems',
# #             'Luvisols',
# #             'Nitisols',
# #             'Regosols',
# #             'Vertisols',
# #             'Solonchaks',
# #             'Podzols',
# #             'Alisols',
# #             'Cambisols',
# #             'Calcisols',
# #             'Phaeozems',
# #             'Acrisols',
# #             'Plinthosols',
# #             'Clay',
# #             'Unknown'

# #         ]
# #         try:


# #             # row = [float(lat), float(lon), float(elevation), float(distance_str), float(slope_angle),weather_data['data'][0]['precip'],st.index(soil_type),weather_data['data'][0]['rh'],weather_data['data'][0]['rh']]  # Adjust as necessary
# #             row = [
# #     11.5560,
# #     76.0405,
# #     850.0,
# #     0.25,
# #     38.0,
# #     85.0,
# #     st.index("Clay"),
# #     92.0,
# #     23.0
# # ]
# #         except:
# #             row = [float(lat), float(lon), float(0), float(distance_str), float(slope_angle),
# #                    0, st.index(soil_type), 0,
# #                    1]  # Adjust as necessary

# #         if len(row) != knn.n_features_in_:
# #             raise ValueError("Expected {knn.n_features_in_} features, but got {len(row)}")


# #         # Make the prediction
# #         res = knn.predict([row])
# #         print(res, "++++++++++++++++++")

# #         if res[0] == 0:
# #             return render(request,"admin/result.html",{'status': 'ok', 'val': 'Non-Disaster','weather_data':weather_data,'st':soil_type,'river':distance_str,'altitude':0,'rainfall':"",'city_name':""})
# #         else:
# #             return HttpResponse({'status': 'not ok', 'val': 'Disaster','weather_data':weather_data,'st':soil_type,'river':distance_str,'altitude':elevation,'rainfall':'','city_name':''})

# #     except ValueError as e:
# #         print("Error in prediction:", str(e))
# #         return JsonResponse({'error': 'Prediction failed', 'details': str(e)}, status=500)




 {% endcomment %}
