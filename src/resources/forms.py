from django import forms
from django.db import models
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django_summernote.widgets import SummernoteWidget
from django.forms import ModelForm
from django_select2.forms import Select2MultipleWidget
from .models import Resource, Keyword, Category, Audience, Theme, ResourceGroup, ResourcesGrouped
from authors.models import Author
from PIL import Image
from datetime import datetime, date


class ResourceForm(forms.ModelForm):
    #abstract = forms.CharField(widget=SummernoteWidget(attrs={'summernote': {'width': '100%', 'maxTextLength': 3000}}), max_length=3000)
    abstract = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Please briefly describe the resource (ideally in 500 words or less)'}), max_length = 3000)
    choices = forms.CharField(widget=forms.HiddenInput(),required=False, initial=())
    choicesSelected = forms.CharField(widget=forms.HiddenInput(),required=False, initial=())
    keywords = forms.MultipleChoiceField(choices=(), widget=Select2MultipleWidget(attrs={'data-placeholder':'Please write or select keywords to describe the resource, separated by commas'}), required=False, label="Keywords")
    category = forms.ModelChoiceField(queryset=Category.objects.filter(parent__isnull=True))
    categorySelected = forms.CharField(widget=forms.HiddenInput(),required=False)
    authorsCollection = forms.CharField(widget=forms.HiddenInput(),required=False, initial=())
    selectedAuthors = forms.CharField(widget=forms.HiddenInput(),required=False, initial=())
    authors = forms.MultipleChoiceField(choices=(), widget=Select2MultipleWidget(attrs={'data-placeholder':' Author(s) of the resource. If not known, name the project within the resource was created. Separated by commas'}), required=False,label="Authors")
    audience = forms.ModelMultipleChoiceField(queryset=Audience.objects.all(), widget=Select2MultipleWidget(attrs={'data-placeholder': 'The audience(s) for which the resource is intended. Multiple selection.'}))
    theme = forms.ModelMultipleChoiceField(queryset=Theme.objects.all(), widget=Select2MultipleWidget(attrs={'data-placeholder':'The thematic content of the resource (select as many as apply)'}), required=False)
    image1 = forms.ImageField(required=False)
    x1 = forms.FloatField(widget=forms.HiddenInput(),required=False)
    y1 = forms.FloatField(widget=forms.HiddenInput(), required=False)
    width1 = forms.FloatField(widget=forms.HiddenInput(),required=False)
    height1 = forms.FloatField(widget=forms.HiddenInput(), required=False)
    image2 = forms.ImageField(required=False)
    x2 = forms.FloatField(widget=forms.HiddenInput(),required=False)
    y2 = forms.FloatField(widget=forms.HiddenInput(), required=False)
    width2 = forms.FloatField(widget=forms.HiddenInput(),required=False)
    height2 = forms.FloatField(widget=forms.HiddenInput(), required=False)
    resource_DOI = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'placeholder':'Please provide the Digital Object Signifier that is unique to your resource, generated by the Publisher, Zenodo...'}))
    author_email  = forms.CharField(max_length=100, required=False,widget=forms.TextInput(attrs={'autocomplete':'nope','placeholder':'Not shown in the platform'}) )
    url = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'URL to where the document is hosted by the publisher, or in a permanent repository such as Zenodo, OSF, the RIO Journal, or similar'}))
    year_of_publication = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'placeholder':' enter the year (YYYY) that that this version of the resource was published'}))
    name = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'autocomplete':'nope','placeholder':' The title or name of the resource'}))
    publisher = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'autocomplete':'nope','placeholder':'The publisher of the resource, if applicable. Otherwise please name the project within which the resource was created'}) )
    license = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'autocomplete':'nope','placeholder':' Indicate the resource license, such as Creative Commons CC-BY. Enter a URL link to the license if available.'}), required=False)
    curatedList = forms.ModelMultipleChoiceField(queryset=ResourceGroup.objects.all(), widget=Select2MultipleWidget, required=False,label="Curated lists")

    class Meta:
        model = Resource
        fields = ["name", "abstract", "url", "audience", "theme","keywords", "license", "publisher", "curatedList",
         "category", "authors","author_email", "image1", "x1", "y1", "width1", "height1", "resource_DOI", "year_of_publication"]


    def save(self, args, images):
        pk = self.data.get('resourceID', '')
        publication_date = datetime.now()
        rsc = super(ResourceForm, self).save(commit=False)
        category = get_object_or_404(Category, id=self.data['categorySelected'])

        if pk:
            rsc = get_object_or_404(Resource, id=pk)
            rsc.name = self.data['name']
            rsc.abstract = self.data['abstract']
            rsc.url = self.data['url']
            rsc.license = self.data['license']
            rsc.publisher = self.data['publisher']
        else:
            rsc.dateUploaded = publication_date
            rsc.creator = args.user

        rsc.inLanguage = self.data['language']
        rsc.author_email = self.data['author_email']
        rsc.resourceDOI = self.data['resource_DOI']
        if self.data['year_of_publication'] != '':
            rsc.datePublished = self.data['year_of_publication']
        else:
            rsc.datePublished = None
        rsc.category = category

        if(images[0] != '/'):
            rsc.image1 = images[0]
        if(images[1] != '/'):
            rsc.image2 = images[1]


        rsc.save()

        rsc.audience.set(self.data.getlist('audience'))
        rsc.theme.set(self.data.getlist('theme'))

        curatedList = self.data.getlist('curatedList')

        if args.user.is_staff:
            objs = ResourcesGrouped.objects.filter(resource=rsc)
            if objs:
                for obj in objs:
                    obj.delete()
            for clist in curatedList:
                rscGroup = get_object_or_404(ResourceGroup, id=clist)
                ResourcesGrouped.objects.get_or_create(group=rscGroup,resource=rsc)

        # Keywords
        choices = self.data['choices']
        choices = choices.split(',')
        for choice in choices:
            if(choice != ''):
                keyword = Keyword.objects.get_or_create(keyword=choice)
        keywords = Keyword.objects.all()
        keywords = keywords.filter(keyword__in = choices)
        rsc.keywords.set(keywords)

        # Authors
        authors = self.data['authorsCollection']
        authors = authors.split(',')
        for author in authors:
            if(author != ''):
                Author.objects.get_or_create(author=author)
        authorsCollection = Author.objects.all()
        authors = authorsCollection.filter(author__in = authors)
        rsc.authors.set(authors)

        return 'success'


class ResourcePermissionForm(forms.Form):
    selectedUsers = forms.CharField(widget=forms.HiddenInput(),required=False, initial=())
    usersCollection = forms.CharField(widget=forms.HiddenInput(),required=False, initial=())
    usersAllowed =   forms.MultipleChoiceField(choices=(), widget=Select2MultipleWidget, required=False, label="Give additional users permission to edit")
