from oj.models import *
from django.contrib.auth.models import User
f = open('admin.ini','r')
lines = f.readlines()
for line in lines:
    user = User.objects.get(username=line.strip()).profile
    user.type = 2
    print user.type
    user.save()


