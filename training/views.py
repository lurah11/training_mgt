from django.shortcuts import render, redirect
from .models import Employee,Training_master,Training_instance,Evaluation_master,Evaluation_instance,Answer
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,logout,login
import re
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import UserAttributeSimilarityValidator, MinimumLengthValidator, NumericPasswordValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password



def home_view(request):
    if request.user.is_authenticated :
        return redirect('training:trainee-home-view')
    return render (request,"training/home.html")

def login_view(request):
    if request.user.is_authenticated :
        return redirect('training:trainee-home-view')
    
    if request.method == "POST" :
        username = request.POST.get('employee_login_username')
        password = request.POST.get('employee_login_pw')

    else :
        return render(request,"training/home.html")
    check_if_user_exists = User.objects.filter(username=username).exists()
    if check_if_user_exists:
        user = authenticate(request,username=username,password=password)
        if user is not None :
            login(request,user)
            context = {
                'user':user
            }
            return render(request,"training/welcome.html",context=context)
        else:
            context = {
                'error':'invalid username or password'
            }
            return render (request,"training/home.html",context=context)
    else :
        context = {
            'error':'invalid username or password'
        }
        return render (request,"training/home.html",context=context)

def register_view(request):
    # Create the department lists using choices from models.py

    if request.user.is_authenticated :
        return redirect('training:trainee-home-view')
    
    emp = Employee()
    dept_list = []
    dept_choice = emp.DEPT_CHOICE
    for dept in dept_choice :
        dept_list.append(dept[0])
    context = {
        'department':dept_list
    }
    # check whether this is post or get request
    if request.method == "POST" :
        username = request.POST.get('employee_register_username')
        password = request.POST.get('employee_register_pw')
        email = request.POST.get('employee_register_email')
        department = request.POST.get('employee_register_department')
    else :
        context = {
            'department':dept_list
        }
        return render(request,"training/register.html",context=context)
    check_if_user_exists = User.objects.filter(username=username).exists()
    if check_if_user_exists:
        context = {
            'user_exist':'that username already exist',
            'department':dept_list
        }
        return render(request, "training/register.html",context=context)
    else :
        if re.search("\W+",username):
            context = {
                'username_error':'the username should only contain words, numbers, and underscore. You can replace space with underscore',
                'department':dept_list
            }
            return render (request,"training/register.html", context=context)
        else :
            try:
                validators = [UserAttributeSimilarityValidator, MinimumLengthValidator, NumericPasswordValidator]
                for validator in validators:
                    validator().validate(password)
                hashed_password = make_password(password)
                new_user = User(username=username, email=email, password=hashed_password)
                new_user.save()
                new_emp = Employee(user=new_user,department=department)
                new_emp.save()
                context = {
                'success':'registration is successfull',
                'department':dept_list
            }
                
            except ValidationError as e :
                  context = {
                      'error' : e,
                      'department':dept_list
                  }
                  
            return render(request,"training/register.html", context=context)

@login_required
def trainee_home_view(request):
    user = request.user
    t_inst = Training_instance.objects.filter(trainee__user=user).values("training__title","id","training__trainer__user__username","training__start_date","training__end_date","date","status","training__id","is_retake","eval_score")
    context = {
        't_inst':t_inst,
        'user':user
    }
    return render(request,"training/trainee_home.html", context=context)

@login_required
def training_detail_view(request,id):
    user = request.user
    emp = Employee.objects.get(user=user)
    #get the specific objects
    t_object = Training_master.objects.get(pk=id)
    #check whether the training has evaluation
    check_eval = Evaluation_master.objects.filter(training=t_object).exists()

    if check_eval:
        eval = True
    else:
        eval = False
    #check whether the training instance exists :
    try :
        t_instance = Training_instance.objects.get(training=t_object,trainee=emp)
    except:
        t_instance = None


    if t_instance is  None :
        do_training = 'Take This Training'
    else :
        do_training = 'ReTake This Training'

    context = {
        't':t_object,
        'eval':eval,
        'do_training':do_training,
        't_instance' : t_instance
    }
    print(context)
    return render(request,"training/training_detail.html", context=context)

@login_required
def evaluation_view(request,id) :
    user = request.user
    training = Training_master.objects.get(pk=id)
    emp = Employee.objects.get(user=user)
    eval_not_exist = False
    try :
        t_instance = Training_instance.objects.get(training=training,trainee=emp)
    except:
        t_instance = None

    is_evaluation_exist = training.evaluation_master_set.all().count()
    if t_instance is None :
        new_t_instance = Training_instance.objects.create(training=training,trainee=emp)
        new_t_instance.save()
    elif is_evaluation_exist !=0 :
        t_instance.is_retake = True
        t_instance.save()

    if is_evaluation_exist != 0 :
        questions = Evaluation_master.objects.filter(training=training)
        context = {
            't':training,
            'q_s':questions
        }
        return render (request,"training/evaluation.html", context=context)

    else :
        eval_not_exist = True
        context = {
            't' : training,
            'eval_not_exist': eval_not_exist
        }
        return render (request, "training/evaluation.html", context=context)

@login_required
def score_view(request,id):
    if request.method == "POST" :
        emp = Employee.objects.get(user=request.user)
        training = Training_master.objects.get(pk=id)
        question_list = Evaluation_master.objects.filter(training=training)
        t_instance = Training_instance.objects.get(training=training,trainee=emp)
        score = 0 ;
        counter = 0 ;
        for q in question_list :
            counter += 1
            name = f"answer_for_{q.id}"
            answer_id = request.POST.get(name)
            if answer_id :
                answer_obj = Answer.objects.get(pk=answer_id)
                if answer_obj.istrue == True :
                    score += 1
                check_eval_instance = Evaluation_instance.objects.filter(training_inst=t_instance,eval=q).exists()
                print(check_eval_instance)
                if check_eval_instance:
                    update_eval_instance = Evaluation_instance.objects.get(training_inst=t_instance,eval=q)
                    update_eval_instance.answer = answer_obj
                    update_eval_instance.save()
                else :
                    new_eval_instance = Evaluation_instance.objects.create(training_inst=t_instance,eval=q,answer=answer_obj)
                    new_eval_instance.save()

        total_score = (score/counter)*100

        t_instance.eval_score = total_score
        t_instance.save()
        if t_instance.eval_score < training.pass_grade :
            t_instance.status = 'failed'
            passed = False;
        else :
            t_instance.status = 'passed'
            passed = True ;

        t_instance.save()

        context = {
            'status' : passed,
            'score' : total_score,
            'user' : request.user
        }

        return render(request, "training/score.html", context=context)
    else :
        return redirect('training:trainee-home-view')

@login_required
def training_list_view(request):

    training_list = Training_master.objects.all()
    context = {
        'tl':training_list,
        'user':request.user
    }
    return render(request,"training/training_list.html",context=context)

@login_required
def non_post_test_view(request,id):
    emp = Employee.objects.get(user=request.user)
    training = Training_master.objects.get(pk=id)
    t_instance = Training_instance.objects.get(training=training, trainee=emp)

    understood = request.GET.get('understand_the_training')
    not_understood = request.GET.get('not_understand_the_training')

    if understood:
        t_instance.status='passed'
        t_instance.save()
    elif not_understood:
        t_instance.status='failed'
        t_instance.save()
    return redirect('training:trainee-home-view')

@login_required
def logout_view(request):
    logout(request)
    return redirect('training:home-view')
