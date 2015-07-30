from oj.models import *
from django.contrib.auth.models import User
import os
from django.core.files import File

user = User.objects.get(username='XinyueChen')

root = 'problems/'
folders = os.listdir(root)
for folder in folders:
    print folder
    files = os.listdir(root + folder)
    description = ''
    input = ''
    output = ''
    for file in files:
        print file
        if file.endswith('input.txt'):
            input = root + folder + '/' + file
        elif file.endswith('output.txt'):
            output = root + folder + '/' + file
        else:
            description = root + folder + '/' + file
    problem = Problem.objects.create(author = user,
            title = folder,
            description= File(open(description)),
            input_file = File(open(input)),
            output_file = File(open(output)),
            content_type = 'txt')

