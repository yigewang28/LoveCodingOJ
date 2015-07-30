"""
Celery tasks
"""
# test comment

from celery import task,platforms
import celery
from models import *
from helper import *
from django.shortcuts import get_object_or_404
import time
import os
import datetime

import threading
platforms.C_FORCE_ROOT = True
@task()
def evaluate(submission_id):
    submission = get_object_or_404(Submission, id=submission_id)
    problem = submission.problem
    input_path = os.path.abspath('.') + '/media/problems/' + os.path.basename(problem.input_file.name)
    output_path = os.path.abspath('.') + '/media/problems/' + os.path.basename(problem.output_file.name)
    # code_path = os.path.abspath('.') + '/media/problems/' + 'code.c'
    code_path = os.path.abspath('.') + '/media/problems/' 
    if submission.language == 'c':
        code_path = code_path + 'code.c'
    elif submission.language == 'c++':
        code_path = code_path + 'code.cpp'
    elif submission.language == 'java':
        code_path = code_path + 'Solution.java'
    code = submission.code
    code_file = open(code_path, 'w+')
    code_file.write(code)
    code_file.close()
    
    result = judge(code_path, input_path, output_path)
    submission.state = result['result']
    submission.save()
    os.remove(code_path)


@celery.decorators.periodic_task(run_every=datetime.timedelta(minutes=2))
def myfunc():
    print 'enter callback'
    competitions = Competition.objects.all()
    for competition in competitions:
        valid_end = datetime.datetime.combine(competition.enddate,competition.endtime)
        valid_now = datetime.datetime.now() + relativedelta(hours=-4)
        if valid_now > valid_end and not competition.state == "Finished":
            competition.state = "Finished"
            competition.save()
            # caculate the rewards for every participant
            for participant in competition.participants.all():
                ac_count = Submission.objects.filter(user=participant).filter(state="Accepted").values('problem').distinct().count
                profile = participant.profile
                profile.rewards = profile.rewards + 1
                #participant.profile.rewards = participant.profile.rewards + ac_count
                profile.save()
            print 'reward callback:' + str(competition.id)
  
