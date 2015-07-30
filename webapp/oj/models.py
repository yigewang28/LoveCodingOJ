from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import datetime
from django.utils.translation import gettext as _

import locale
from dateutil.relativedelta import relativedelta
import pytz
from django.utils import timezone

class Profile(models.Model):
	profile_user = models.OneToOneField(User)
	school = models.CharField(max_length=100)
	website = models.CharField(max_length=50)
	photo = models.FileField(upload_to="photos", default='photos/defaultprofile.jpg')
	bio = models.CharField(max_length=430)
	content_type = models.CharField(max_length=50)
	rewards = models.IntegerField()
        type = models.IntegerField()

class Problem(models.Model):
	author = models.ForeignKey(User)
	title = models.CharField(max_length=100)
	description = models.FileField(upload_to="problems", blank=True)
	input_file = models.FileField(upload_to="problems")
	output_file = models.FileField(upload_to="problems")
	content_type = models.CharField(max_length=50)
	def __unicode__(self):
		return self.description.read()

class Competition(models.Model):
	author = models.ForeignKey(User)
        name = models.CharField(max_length=100)
	created = models.DateTimeField(editable=False)
	startdate = models.DateField()
	starttime = models.TimeField()
	participants = models.ManyToManyField(User, related_name="participants")
	enddate = models.DateField()
	endtime = models.TimeField()
	problems = models.ManyToManyField(Problem)
	state = models.CharField(max_length=20, null=True)
	def save(self, *args, **kwargs):
		if not self.id:
			self.created = datetime.datetime.now() + relativedelta(hours=-4)
		return super(Competition, self).save(*args, **kwargs)

class Submission(models.Model):
	user = models.ForeignKey(User)
	problem = models.ForeignKey(Problem)
	competition = models.ForeignKey(Competition, null=True)
	created = models.DateTimeField(editable=False)
	code = models.CharField(max_length=4096)
	language = models.CharField(max_length=20)
	state = models.CharField(max_length=10)
	def save(self, *args, **kwargs):
		if not self.id:
			self.created = datetime.datetime.now() + relativedelta(hours=-4)
		return super(Submission, self).save(*args, **kwargs)

class DiscussionProblem(models.Model):
	problem = models.ForeignKey(Problem)

class PostProblem(models.Model):
	discussion = models.ForeignKey(DiscussionProblem)
	created = models.DateTimeField(editable=False)
	user = models.ForeignKey(User)
	text = models.CharField(max_length=1024)
	def __unicode__(self):
		return self.text
	def save(self, *args, **kwargs):
		if not self.id:
			self.created = datetime.datetime.now() + relativedelta(hours=-4)
		return super(PostProblem, self).save(*args, **kwargs)

class CommentPostProblem(models.Model):
	post = models.ForeignKey(PostProblem)
	created = models.DateTimeField(editable=False)
	user = models.ForeignKey(User)
	text = models.CharField(max_length=1024)
	def __unicode__(self):
		return self.text
	def save(self, *args, **kwargs):
		if not self.id:
			self.created = datetime.datetime.now() + relativedelta(hours=-4)
		return super(CommentPostProblem, self).save(*args, **kwargs)

class News(models.Model):
	author = models.ForeignKey(User)
	created = models.DateTimeField(editable=False)
	text = models.CharField(max_length=1024)
	def __unicode__(self):
		return self.text
	def save(self, *args, **kwargs):
		if not self.id:
			self.created = datetime.datetime.now() + relativedelta(hours=-4)
		return super(News, self).save(*args, **kwargs)

class CommentNews(models.Model):
	news = models.ForeignKey(News)
	author = models.ForeignKey(User)
	created = models.DateTimeField(editable=False)
	text = models.CharField(max_length=1024)
	def __unicode__(self):
		return self.text
	def save(self, *args, **kwargs):
		if not self.id:
			self.created = datetime.datetime.now() + relativedelta(hours=-4)
		return super(CommentNews, self).save(*args, **kwargs)

