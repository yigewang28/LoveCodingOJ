from django import forms
from django.contrib.auth.models import User
from models import *

from datetime import datetime
import locale
from dateutil.relativedelta import relativedelta
import pytz
from django.utils import timezone
import threading


MAX_UPLOAD_SIZE= 250000000
 
class RegistrationForm(forms.Form):
    firstname = forms.CharField(max_length=20)
    lastname  = forms.CharField(max_length=20)
    username   = forms.CharField(max_length = 20)
    email      = forms.EmailField(max_length = 30)
    password1  = forms.CharField(max_length = 200, 
                                 label='Password', 
                                 widget = forms.PasswordInput())
    password2  = forms.CharField(max_length = 200, 
                                 label='Confirm password',  
                                 widget = forms.PasswordInput())


    # Customizes form validation for properties that apply to more
    # than one field.  Overrides the forms.Form.clean function.
    def clean(self):
        # Calls our parent (forms.Form) .clean function, gets a dictionary
        # of cleaned data as a result
        cleaned_data = super(RegistrationForm, self).clean()

        # Confirms that the two password fields match
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords did not match.")

        # We must return the cleaned data we got from our parent.
        return cleaned_data


    # Customizes form validation for the username field.
    def clean_username(self):
        # Confirms that the username is not already present in the
        # User model database.
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__exact=username):
            raise forms.ValidationError("Username is already taken.")
        return username

class NewsForm(forms.Form):
    content = forms.CharField()


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ('profile_user', 'follower','content_type','rewards','type')
    def clean_photo(self):
        #print "lllllllllllll"
        photo = self.cleaned_data['photo']
        #print photo
        try:
            if not photo:
               return None
            elif not photo.content_type.startswith('image'):
                raise forms.ValidationError('File type is not image')
            elif photo.size > MAX_UPLOAD_SIZE:
                raise forms.ValidationError('File too big (max size is {0} bytes)'.format(MAX_UPLOAD_SIZE))
        except AttributeError:
            raise forms.ValidationError('No file is uploaded')
        return photo


class ProblemForm(forms.ModelForm):
    class Meta:
        model = Problem
        exclude = ('content_type','author')
    def clean_description(self):
        description = self.cleaned_data['description']
        if not description:
            return description.ValidationError('The description is empty')
        if description.size > MAX_UPLOAD_SIZE:
            raise forms.ValidationError('File too big (max size is {0} bytes)'.format(MAX_UPLOAD_SIZE))
        return description

    def clean_title(self):
        title = self.cleaned_data['title']
        if Problem.objects.filter(title=title):
            return forms.ValidationError('The name of the problem has been used.')
        return title
class SubmissionForm(forms.Form):
    #problem = forms.DecimalField()
    language = forms.CharField()
    code = forms.CharField()
    #def clean_problem(self):
    #    problem = self.cleaned_data.get('problem')
    #    if not Problem.objects.get(id=problem):
    #       raise forms.ValidationError("Problem doesn't exist.")
    #    return problem
    def clean_language(self):
        lang = self.cleaned_data.get('language')
        valid_lang_list = ['c', 'java', 'c++', 'python']
        if not lang in valid_lang_list:
           raise forms.ValidationError("Language is not valid.")
        return lang

class PostForm(forms.Form):
    text = forms.CharField()
    def clean_test(self):
        text = self.cleaned_data['text']
        if text.strip() == '':
            raise forms.ValidationError("Post must contain characters.")
        return text

class CommentPostForm(forms.Form):
    text = forms.CharField()
    def clean_text(self):
        text = self.cleaned_data['text']
        print 'comment text:' + text.strip()
        if text.strip() == '':
            raise forms.ValidationError("Comment must contain characters.")
        return text


class CompetitionForm(forms.Form):
    startdate = forms.DateField()
    starttime = forms.TimeField()
    enddate = forms.DateField()
    endtime = forms.TimeField()
    name = forms.CharField()
    def clean(self):
        # Calls our parent (forms.Form) .clean function, gets a dictionary
        # of cleaned data as a result
        cleaned_data = super(CompetitionForm, self).clean()

        # Confirms that the two password fields match
        start_date = cleaned_data.get('startdate')
        start_time = cleaned_data.get('starttime')
        end_date = cleaned_data.get('enddate')
        end_time = cleaned_data.get('endtime')
        start_datetime = datetime.combine(start_date,start_time)
        end_datetime = datetime.combine(end_date,end_time)
        now = datetime.now() + relativedelta(hours=-4)
        if start_datetime < now +  relativedelta(seconds=+60):
            raise forms.ValidationError("Competition start time is not valid.")
        elif end_datetime < start_datetime + relativedelta(minutes=+1):
            raise forms.ValidationError("Competition end time is not valid.")

        # We must return the cleaned data we got from our parent.
        return cleaned_data
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if Competition.objects.filter(name=name):
            raise forms.ValidationError("Competition name is not valid.")
        return name






