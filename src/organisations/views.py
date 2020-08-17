from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from PIL import Image
from django.contrib.auth import get_user_model
from django.utils import formats
from datetime import datetime
from .forms import OrganisationForm
from .models import Organisation, OrganisationType
from projects.models import Project
from resources.models import Resource
from profiles.models import Profile
import random


@login_required(login_url='/login')
def new_organisation(request):
    user = request.user

    form = OrganisationForm()
    if request.method == 'POST':
        form = OrganisationForm(request.POST, request.FILES)
        if form.is_valid():
            image_path = ''
            if(request.FILES.get('logo', False)):
                photo = request.FILES['logo']
                image = Image.open(photo)
                _datetime = formats.date_format(datetime.now(), 'Y-m-d_hhmmss')
                random_num = random.randint(0, 1000)
                image_path = "media/images/" + _datetime + '_' + str(random_num) + '_' + photo.name
                image.thumbnail((144,144))
                image.save(image_path)        
            form.save(request, '/' + image_path)
            return redirect('/')
        else:
            print(form.errors)

    return render(request, 'new_organisation.html', {'form': form, 'user':user})



def organisation(request, pk):
    organisation = get_object_or_404(Organisation, id=pk)
        
    associatedProjects = Project.objects.all().filter(organisation__id=pk)
    associatedResources = Resource.objects.all().filter(organisation__id=pk)
    members = Profile.objects.all().filter(organisation__id=pk)

    return render(request, 'organisation.html', {'organisation':organisation, 'associatedProjects': associatedProjects, 'associatedResources': associatedResources,
    'members': members})


def edit_organisation(request, pk):
    organisation = get_object_or_404(Organisation, id=pk)
    user = request.user
    
    if user != organisation.creator and not user.is_staff:
        return redirect('../projects', {})

    form = OrganisationForm(initial={
        'name':organisation.name,'url': organisation.url, 'description': organisation.description, 
        'orgType': organisation.orgType, 'logo': organisation.logo, 'contact_point': organisation.contactPoint,
        'contact_point_email': organisation.contactPointEmail, 'address': organisation.address
    })

    if request.method == 'POST':
        form = OrganisationForm(request.POST, request.FILES)
        if form.is_valid():
            image_path = ''
            if(request.FILES.get('logo', False)):
                photo = request.FILES['logo']
                image = Image.open(photo)
                _datetime = formats.date_format(datetime.now(), 'Y-m-d_hhmmss')
                random_num = random.randint(0, 1000)
                image_path = "media/images/" + _datetime + '_' + str(random_num) + '_' + photo.name
                image.thumbnail((144,144))
                image.save(image_path)
                image_path = '/' + image_path
            form.save(request, image_path)
            return redirect('/')
        else:
            print(form.errors)

    return render(request, 'edit_organisation.html', {'form': form, 'organisation':organisation, 'user':user,})