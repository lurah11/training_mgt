from django.contrib import admin
from .models import Employee,Training_master,Training_instance,Evaluation_master,Evaluation_instance,Answer

admin.site.register(Employee)
admin.site.register(Training_master)
admin.site.register(Training_instance)
admin.site.register(Evaluation_master)
admin.site.register(Evaluation_instance)
admin.site.register(Answer)
