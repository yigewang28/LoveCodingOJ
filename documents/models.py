from django.db import models
from django.utils.translation import gettext as _
from django.utils import timezone
import datetime
from django import forms
from django.contrib.auth.models import User

# customized user model with extra profile information
class PlatformUser(models.Model):
	user = models.OneToOneField(User, primary_key=True)
	age = models.IntegerField(default=0)
	bio = models.CharField(max_length=430)
	avatar = models.FileField(upload_to = 'avatar', default = 'avatar/default-avatar.jpg')
	point = models.DecimalField(default=0)
	rank = models.IntegerField(default=0)
	school = models.CharField(max_length=50)
	account_type = models.IntegerField(default=0) # 0 for normal user and 1 for administrator
	link_github = models.CharField(max_length=100)
	link_facebook = models.CharField(max_length=100)
	link_twitter = models.CharField(max_length=100)

# coding problem model
class Problem(models.Model):
	author = models.ForeignKey(PlatformUser)
	created = models.DateTimeField(auto_now_add=True)
	description = models.FileField(upload_to = 'problem')
	script = models.FileField(upload_to = 'problem')
	test_data = models.FileField(upload_to = 'problem')
	time_limit = models.IntegerField(default=1000) # unit ms
	memory_limit = models.IntegerField(default=3000) # unit kb

# post model that relates with one coding problem
class ProblemPost(models.Model):
	problem = models.ForeignKey(Problem)
	author = models.ForeignKey(PlatformUser)
	created = models.DateTimeField(auto_now_add=True)
	content = models.CharField(max_length=430)

# comment model that relates with one post of one coding problem
class ProblemComment(models.Model):
	post = models.ForeignKey(ProblemPost)
	author = models.ForeignKey(PlatformUser)
	created = models.DateTimeField(auto_now_add=True)
	content = models.CharField(max_length=430)

# submission model that records the information about a code submission from a user for a problem
class Submission(models.Model):
	author = models.ForeignKey(PlatformUser)
	problem = models.ForeignKey(Problem)
	created = models.DateTimeField(auto_now_add=True)
	code = models.FileField(upload_to = 'code')
	competion = models.ForeignKey(Competion)
	compile_result = models.CharField(max_length=1000)
	evaluation_result = models.CharField(max_length=1000)
	timecost = models.IntegerField(default=0) # unit:ms
	status = models.IntegerField(default=0) # 0 for pending, 1 for accepted, 2 for wrong answer, 3 for compiling error, 4 for runtime error
	language = models.IntegerField(default=0) # 0 for java

# competition model 
class Competition(models.Model):
	competitors = models.ManyToManyField(PlatformUser)
	problems = models.ManyToManyField(Problem)
	host = models.ForeignKey(PlatformUser)
	created = models.DateTimeField(auto_now_add=True)
	description = models.FileField(upload_to = 'competition')
	start_time = models.DateTimeField()
	end_time = models.DateTimeField()
	restriction = models.FileField(upload_to = 'competition') # json file that is used to filter participants
	reward = models.FileField(upload_to = 'competition') # json file that is used to reward the winners

# Competition Post model
class CompetitionPost(models.Model):
	author = models.ForeignKey(PlatformUser)
	created = models.DateTimeField(auto_now_add=True)
	competition = models.ForeignKey(Competition)
	isAnnounceMent = models. BooleanField()
	content = models.CharField(max_length=430)

# Competition Post Comment model
class CompetitionComment(models.Model):
	post = models.ForeignKey(CompetitionPost)
	author = models.ForeignKey(PlatformUser)
	created = models.DateTimeField(auto_now_add=True)
	content = models.CharField(max_length=430)


