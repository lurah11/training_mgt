from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

class Employee(models.Model):
    DEPT_CHOICE = [
    ('qc beverage','qc beverage'),
    ('qc packaging','qc packaging'),
    ('qa','qa'),
    ('production beverage','production beverage'),
    ('production packaging','production packaging'),
    ('warehouse beverage','warehouse beverage'),
    ('warehouse packaging','warehouse packaging'),
    ('utility','utility'),
    ('sales','sales'),
    ('GA','GA'),
    ('HR','HR')
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=20, choices = DEPT_CHOICE, default='production beverage')
    is_trainer = models.BooleanField(default=False)
    def __str__(self) :
        return f"{self.user.username}_{self.department}"

class Training_master(models.Model) :
    def upload_path(instance,filename):
        return '{0}/{1}_{2}/{3}'.format(instance.trainer.department, instance.title, instance.start_date,filename)

    CATEGORY_CHOICE = [
    ('mandatory','mandatory'),
    ('additional','additional')
    ]
    title = models.CharField(max_length = 100)
    category = models.CharField(max_length=15, choices=CATEGORY_CHOICE, default ='mandatory')
    trainer = models.ForeignKey(Employee, on_delete=models.PROTECT)
    description = models.CharField(max_length = 150, blank = True, null = True)
    start_date = models.DateField()
    end_date = models.DateField()
    material = models.FileField(upload_to=upload_path)
    modified = models.DateTimeField(auto_now=True)
    pass_grade = models.DecimalField(max_digits=3,decimal_places=1,null=True, blank=True)
    time_limit = models.IntegerField(null=True, blank = True)

    def __str__(self):
        return f"{self.title}_{self.start_date}"

class Evaluation_master(models.Model):
    training = models.ForeignKey(Training_master,on_delete=models.CASCADE)
    question = models.CharField(max_length=200)


    def __str__(self):
        return f"evaluation:{self.id}_{self.training.title}"

class Answer(models.Model):
    evaluation = models.ForeignKey(Evaluation_master, on_delete = models.CASCADE)
    answer_text = models.CharField(max_length=150)
    istrue = models.BooleanField(default=False)

    def __str__(self):
        concat_text = self.answer_text[:20]
        return f"answer:{self.evaluation}:{concat_text}..."

class Training_instance(models.Model):
    STATUS_CHOICE = [
    ('passed','passed'),
    ('failed','failed')
    ]
    training = models.ForeignKey(Training_master, on_delete=models.PROTECT)
    trainee = models.ForeignKey(Employee, on_delete = models.PROTECT)
    date = models.DateField(auto_now=True)
    eval_score = models.IntegerField(blank=True, null=True)
    status = models.CharField(max_length = 10 , choices=STATUS_CHOICE, blank=True, null=True)
    is_retake = models.BooleanField(default=False)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.training.title}__{self.trainee.user.username}"


class Evaluation_instance(models.Model):
    training_inst = models.ForeignKey(Training_instance, on_delete=models.CASCADE)
    eval = models.ForeignKey(Evaluation_master, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)

    def __str__(self):
        return f"answer : {self.training_inst.trainee.user.username}_{self.training_inst.training.title}_id={self.id}"
