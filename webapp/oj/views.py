from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from oj.models import *
from oj.forms import *
from django.http import HttpResponse, Http404
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db import transaction
import json
from django.views.decorators.csrf import csrf_exempt
from tasks import *
from django.db.models import F
from datetime import datetime
import locale
from dateutil.relativedelta import relativedelta
import pytz
from django.utils import timezone
import threading

@login_required
def home(request):   
    context = {}
    context['hasLogin'] = True
    user_items = User.objects.all()
    users = []
    for user in user_items:
        ac_count = Submission.objects.filter(user=user).filter(state="Accepted").values('problem').distinct().count
        rewards = user.profile.rewards
        users.append({
            "username":user.username,
            "ac":ac_count,
            "point":rewards,
            })
    form = NewsForm()
    context['form'] = form
    context['user'] = request.user
    context['news'] = News.objects.all().order_by('-created')
    users.sort(key=lambda x:x['point'] , reverse = True)
    #users.sort(key=lambda x:x['point'])
    context['users'] = users
    return render(request, 'oj/home.html', context)

def get_ac(user_id):
    user = get_object_or_404(User, id=user_id)
    submissions = Submission.objects.filter(user=user).filter(state="Accepted").values('problem').distinct().count

@transaction.atomic
def register(request):
    context = {}

    if request.method == 'GET':
        context['form'] = RegistrationForm()
        return render(request, 'oj/register.html', context)

    # Creates a bound form from the request POST parameters and makes the 
    # form available in the request context dictionary.
    form = RegistrationForm(request.POST)
    context['form'] = form

    # Validates the form.
    if not form.is_valid():
        return render(request, 'oj/register.html', context)

    # Creates the new user from the valid form data
    new_user = User.objects.create_user(username=form.cleaned_data['username'], \
                                        first_name=form.cleaned_data['firstname'],\
                                        last_name=form.cleaned_data['lastname'],\
                                        password=form.cleaned_data['password1'],\
                                        email=form.cleaned_data['email'],
                                        )
    # Mark the user as inactive to prevent login before email confirmation.
    new_user.is_active = False
    new_user.save()

    profile = Profile(type = 1,profile_user=new_user, school="", website="", bio="",rewards=0)
    profile.save()

    # Generate a one-time use token and an email message body
    token = default_token_generator.make_token(new_user)

    email_body = """
Welcome to Online Judge.  Please click the link below to verify your email address and complete the registration of your account:

  http://%s%s
""" % (request.get_host(), 
       reverse('confirm', args=(new_user.username, token)))

    send_mail(subject="Verify your email address",
              message= email_body,
              from_email="admin@lovecoding.com",
              recipient_list=[new_user.email])

    context['email'] = form.cleaned_data['email']
    return render(request, 'oj/needs-confirmation.html', context)


@transaction.atomic
def confirm_registration(request, username, token):
    user = get_object_or_404(User, username=username)

    # Send 404 error if token is invalid
    if not default_token_generator.check_token(user, token):
        raise Http404

    # Otherwise token was valid, activate the user.
    user.is_active = True
    user.save()
    return render(request, 'oj/confirmed.html', {})

@login_required
def problems(request):  
    if request.method == 'GET':
        context = {}
        context['hasLogin'] = True

        problemItems = Problem.objects.all()
        problems = []
        for problem in problemItems:
            submissions = Submission.objects.filter(problem=problem).count
            ac_submissions = Submission.objects.filter(problem=problem).filter(state="Accepted").count
            submissions_me = Submission.objects.filter(problem=problem).filter(user=request.user).count
            ac_me = Submission.objects.filter(problem=problem).filter(state="Accepted").filter(user=request.user).count
            problems.append({
                "id":problem.id,
                "title":problem.title,
                "description":problem.description.read(),
                "ac":ac_submissions,
                "total":submissions,
                "ac_me":ac_me,
                "total_me":submissions_me,
                })
        context['problems'] = problems
        context['user'] = request.user
        return render(request, 'oj/problems.html', context)
    else:
        raise Http404

@login_required
def add_problem(request):  
    context = {}
    context['hasLogin'] = True
    if request.user.profile.type == 1:
        return redirect(reverse('problems'))
    if request.method == 'GET':
        form = ProblemForm()
        context['form'] = form
        return render(request, 'oj/add_problem.html', context)
    new_problem = Problem(author=request.user)
    form = ProblemForm(request.POST, request.FILES, instance=new_problem)
    if not form.is_valid():
        context['form'] = form
        new_problem.delete()
    else:
        if form.cleaned_data['description']:
            new_problem.content_type = form.cleaned_data['description'].content_type
            print 'content type =', form.cleaned_data['description'].content_type
        form.save()
        discussion = DiscussionProblem.objects.create(problem=new_problem)
    return redirect(reverse('problems'))

@login_required
def competition(request):  
    if request.method == 'GET':
        context = {}
        context['hasLogin'] = True
        #context['competitions'] = Competition.objects.all().order_by('-created')
        competition_list = Competition.objects.all().order_by('-created')
        competitions = []
        for competition_item in competition_list:
            state = 1
            valid_start  = datetime.combine(competition_item.startdate,competition_item.starttime)
            valid_now = datetime.now() + relativedelta(hours=-4)
            valid_end = datetime.combine(competition_item.enddate,competition_item.endtime)
            if not competition_item.participants.filter(id=request.user.id):
                if valid_now > valid_start + relativedelta(minutes=-5):
                    state = 6
            else:
                if valid_now < valid_start + relativedelta(minutes=-5):
                    state = 2
                elif valid_now < valid_start:
                    state = 3
                elif valid_now < valid_end:
                    state = 4
                else:
                    state = 5
            competitions.append({
                "id":competition_item.id,
                "name":competition_item.name,
                "author":competition_item.author,
                "startdate":competition_item.startdate,
                "starttime":competition_item.starttime,
                "enddate":competition_item.enddate,
                "endtime":competition_item.endtime,
                "state": state# 1 not in; 2 in but not valid; 3 in but wait; 4 in and valid; 5 in and after #6 not able to register
                })
        context['competitions'] = competitions
        return render(request, 'oj/competition.html', context)
    else:
        raise Http404

@login_required
def competition_single(request, id):
    if request.method == 'GET':
        competition = get_object_or_404(Competition, id=id)
        valid_start  = datetime.combine(competition.startdate,competition.starttime)
        valid_now = datetime.now() + relativedelta(hours=-4)
        valid_end = datetime.combine(competition.enddate,competition.endtime)
        if not competition.participants.filter(id=request.user.id):
            return redirect(reverse('competition'))
        elif valid_now > valid_end:
            return redirect(reverse('competition'))
        context = {}
        context['hasLogin'] = True
        context['competition'] = get_object_or_404(Competition, id=id)
        problem_list = get_object_or_404(Competition, id=id).problems.all()
        problems = []
        for problem_item in problem_list:
            total_me = Submission.objects.filter(user=request.user).filter(problem=problem_item).filter(competition=competition).count
            ac_me = Submission.objects.filter(user=request.user).filter(problem=problem_item).filter(competition=competition).filter(state="Accepted").count
            total_submissions = Submission.objects.filter(problem=problem_item).filter(competition=competition).count
            ac_submissions = Submission.objects.filter(problem=problem_item).filter(competition=competition).filter(state="Accepted").count
            problems.append({
                "id":problem_item.id,
                "title":problem_item.title,
                "ac_me":ac_me,
                "total_me":total_me,
                "ac":ac_submissions,
                "total": total_submissions,
                })
        context['problems'] = problems
        return render(request, 'oj/competition_single.html', context)
    else:
        raise Http404

@login_required
def add_competition(request):
    context = {}
    context['hasLogin'] = True
    if request.user.profile.type != 2:
        raise Http404
    if request.method == 'GET':
        problems = Problem.objects.all()
        context['problems'] = problems
        return render(request,'oj/add_competition.html', context)
    problems = request.POST.getlist('problem')
    author = request.user
    form = CompetitionForm(request.POST)
    if not form.is_valid():
        problems = Problem.objects.all()
        context['problems'] = problems
        context['errors'] = form.errors
        return render(request,'oj/add_competition.html', context)
    startdate = form.cleaned_data['startdate']
    starttime = form.cleaned_data['starttime']
    enddate = form.cleaned_data['enddate']
    endtime = form.cleaned_data['endtime']
    name = form.cleaned_data['name']
    competition = Competition.objects.create(author=author,
                                            startdate=startdate,
                                            starttime=starttime,
                                            enddate=enddate,
                                            endtime=endtime,
                                            name=name
                                            )
    for problem in problems:
        competition.problems.add(problem)
    competition.save()
    return redirect(reverse('competition'))

@login_required
def register_competition(request, id):
    competition = get_object_or_404(Competition, id=id)
    if not competition.participants.filter(id=request.user.id):
        competition.participants.add(request.user)
        competition.save()
    return redirect(reverse('competition'))

#@login_required
#def finish_competition(request, id):
#    # change state of competition
#    competition = get_object_or_404(Competition, id=id)
#    if not competition.state == "Finished":
#        competition.state = "Finished"
#        competition.save()
#        # caculate the rewards for every participant
#        for participant in competition.participants.all():
#            ac_count = Submission.objects.filter(user=participant).filter(state="Accepted").values('problem').distinct().count
#            profile = participant.profile
#            profile.rewards = profile.rewards + 1
#            #participant.profile.rewards = participant.profile.rewards + ac_count
#            profile.save()
#    return redirect(reverse('competition_single', args=(id,)))

@login_required
def profile(request, id):
    tempuser = get_object_or_404(User, id=id)
    tempprofile = tempuser.profile

    return render(request, 'oj/profile.html', {'user':tempuser,'profile':tempprofile, 'hasLogin':True})

@login_required
def single_problem(request, id):
    if request.method == 'GET':
        context = {}
        context['hasLogin'] = True
        context['user'] = request.user
        problem_item = get_object_or_404(Problem, id=id)
        problem = {}
        problem['id'] = problem_item.id
        problem['title'] = problem_item.title
        problem['description'] = problem_item.description.read()
        context['problem'] = problem
        return render(request, 'oj/single_problem.html', context);
    else:
        raise Http404

@login_required
def edit_profile(request):
    new_profile =  request.user.profile
    context = {}
    context['hasLogin'] = True
    # Just display the registration form if this is a GET request.
    if request.method == 'GET':
        context['form'] = ProfileForm(instance=new_profile)
        return render(request, 'oj/edit_profile.html', context)

    # Creates a bound form from the request POST parameters and makes the 
    # form available in the request context dictionary.
    print request.FILES
    form = ProfileForm(request.POST, request.FILES, instance=new_profile)
    
    if not form.is_valid():
        context['form'] = form
        return render(request, 'oj/edit_profile.html', context)
    else:
        if form.cleaned_data['photo']:
            new_profile.content_type = form.cleaned_data['photo'].content_type
            print 'content type =', form.cleaned_data['photo'].content_type
        form.save()
        #context['message'] = 'Item #{0} saved.'.format(new_profile.id)
        return redirect(reverse('profile', args=(request.user.id,)))

def photo(request, id):
    if request.method == 'GET':
        item = get_object_or_404(Profile, id=id)
        if not item.photo:
            raise Http404
        return HttpResponse(item.photo, content_type=item.content_type)
    else:
        raise Http404


@login_required
def myprofile(request):
    if request.method == 'GET':
        return redirect(reverse('profile', args=(request.user.id,)))
    else:
        raise Http404

    #myself = request.user
    #return render(request, 'oj/profile/html', {'user':myself, 'profile':myself.profile})

@login_required
def submission_problem(request, id):
    if request.method == 'GET':
        problem = get_object_or_404(Problem, id=id)
        submissions = Submission.objects.filter(problem=problem).order_by('-created')
        context = {}
        context['hasLogin'] = True
        context['submissions'] = submissions
        return render(request, 'oj/submission_user.html', context); 
    else:
        raise Http404

@login_required
def submission_single(request, id):
    if request.method == 'GET':
        submission = get_object_or_404(Submission, id=id)
        context = {}
        context['hasLogin'] = True
        context['submission'] = submission
        return render(request, 'oj/submission_single.html', context); 
    else:
        raise Http404

@login_required
def submission_user(request):
    if request.method == 'GET':
        submissions = Submission.objects.filter(user=request.user).order_by('-created')
        context = {}
        context['hasLogin'] = True
        context['submissions'] = submissions
        return render(request, 'oj/submission_user.html', context); 
    else:
        raise Http404

@login_required
def submit_code(request, id):
    if request.method == 'GET':
        return redirect(reverse('problems'))
    form = SubmissionForm(request.POST)
    if not form.is_valid():
        return redirect(reverse('single_problem',args=(id,)))
    user = request.user
    code = form.cleaned_data['code']
    language = form.cleaned_data['language']
    problem_id = id
    problem = get_object_or_404(Problem, id=problem_id)
    submission = Submission.objects.create(user=user,
                                            code=code,
                                            language=language,
                                            problem=problem,
                                            state='Waiting')
    evaluate.delay(submission.id)
    return redirect(reverse('submission_user'))

@login_required
def submit_competition(request, competition_id, problem_id):
    competition = get_object_or_404(Competition, id=competition_id)
    valid_start  = datetime.combine(competition.startdate,competition.starttime)
    valid_now = datetime.now() + relativedelta(hours=-4)
    valid_end = datetime.combine(competition.enddate,competition.endtime)
    if valid_now > valid_end:
        return redirect(reverse('competition'))
    elif valid_now < valid_start:
        return redirect(reverse('competition'))
    problem = get_object_or_404(Problem, id=problem_id)
    if request.method == 'GET':
        return redirect(reverse('single_competition_problem', args=(str(competition_id), str(problem_id))))
    form = SubmissionForm(request.POST)
    if not form.is_valid():
        return redirect(reverse('problems'))
    user = request.user
    code = form.cleaned_data['code']
    language = form.cleaned_data['language']
    submission = Submission.objects.create(user=user,
                                            code=code,
                                            language=language,
                                            problem=problem,
                                            competition=competition,
                                            state='Waiting...')
    evaluate.delay(submission.id)
    return redirect(reverse('competition_single', args=(str(competition_id))))

@login_required
def single_competition_problem(request, competition_id, problem_id):
    if request.method == 'GET':
        competition = get_object_or_404(Competition, id=competition_id)
        problem_item = get_object_or_404(Problem, id=problem_id)
        problem = {}
        problem['id'] = problem_item.id
        problem['title'] = problem_item.title
        problem['description'] = problem_item.description.read()

        context = {}
        context['hasLogin'] = True
        context['user'] = request.user
        context['problem'] = problem
        context['competition'] = competition
        return render(request, 'oj/single_problem.html', context); 
    else:
        raise Http404

@login_required
def discussion_problem(request, id):
    if request.method == 'GET':
        problem = get_object_or_404(Problem, id=id)
        context = {}
        context['hasLogin'] = True
        context['problem'] = get_object_or_404(Problem, id=id)
        if not DiscussionProblem.objects.filter(problem=problem):
            discussion = DiscussionProblem.objects.create(problem=problem)
        discussion = get_object_or_404(DiscussionProblem, problem=problem)
        posts = discussion.postproblem_set.all().order_by('-created')
        new_posts = []
        for post in posts:
            new_posts.append({
                "id":post.id,
                "discussion":post.discussion,
                "user":post.user,
                "text":post.text,
                "created":post.created,
                "comments":post.commentpostproblem_set.all().order_by('-created')
                })

        context['posts'] = new_posts
        return render(request, 'oj/discussion_problem.html', context); 
    else:
        raise Http404

@login_required
def add_discussion_problem(request, id):
    problem = get_object_or_404(Problem, id=id)
    discussion = get_object_or_404(DiscussionProblem, problem=problem)
    if request.method == 'GET' :
        return redirect(reverse('discussion_problem',args=id)) 
    form = PostForm(request.POST)
    if not form.is_valid():
        return redirect(reverse('discussion_problem',args=id)) 
    pos = PostProblem.objects.create(discussion=discussion,
                                    text=form.cleaned_data['text'],
                                    user=request.user)
    return redirect(reverse('discussion_problem', args=(str(problem.id))))

@login_required
def add_comment_discussion_problem(request, id):
    post = get_object_or_404(PostProblem, id=id)
    problem = post.discussion.problem
    if request.method == 'GET':
        return redirect(reverse('discussion_problem', args=(str(problem.id))))
    form = CommentPostForm(request.POST)
    if not form.is_valid():
        return redirect(reverse('discussion_problem', args=(str(problem.id))))
    comment = CommentPostProblem.objects.create(post=post,
                                                text=form.cleaned_data['text'],
                                                user=request.user)
    return redirect(reverse('discussion_problem', args=(str(problem.id))))

@login_required
def add_news(request):
    if request.method == 'GET':
        raise Http404
    else:
        context = {} 
        profile = request.user.profile
        if profile.type == 1:
            # not admin
            return redirect(reverse('home'))
        form = NewsForm(request.POST)
        if not form.is_valid():
            return redirect(reverse('home'))
        else:
            news = News.objects.create(text=form.cleaned_data['content'],author=request.user) 
            return redirect(reverse('home'))

@login_required
def competition_wait(request, id):
    if request.method == 'POST':
        raise Http404
    competition_item  = get_object_or_404(Competition, id=id)
    valid_start  = datetime.combine(competition_item.startdate,competition_item.starttime)
    valid_now = datetime.now() + relativedelta(hours=-4)
    valid_end = datetime.combine(competition_item.enddate,competition_item.endtime)
    if not competition_item.participants.filter(id=request.user.id):
        return redirect(reverse('competition'))
    elif valid_now < valid_start + relativedelta(minutes=-5):
        return redirect(reverse('competition'))
    elif valid_now > valid_start and valid_now < valid_end:
        return redirect(reverse('competition_single',args=(id)))
    context={}
    context['hasLogin'] = True
    context['competition_id'] = id
    context['starttime'] = datetime.combine(competition_item.startdate,competition_item.starttime).strftime('%m/%d/%Y %H:%M:%S')
    return render(request, 'oj/competition_wait.html', context)

def submission_json(request, id):
    submission = get_object_or_404(Submission, id=id)
    result = {
        "id":submission.id,
        "state":submission.state
        }
    response_text = json.dumps(result) #dump list as JSON
    return HttpResponse(response_text, content_type='application/json')

