from django.urls import path,include
from .views import (home_view,login_view,register_view,trainee_home_view,training_detail_view,evaluation_view, score_view,
training_list_view, non_post_test_view,logout_view)


app_name = 'training'

urlpatterns = [
    path('',home_view,name='home-view'),
    path('login',login_view,name='login-view'),
    path('register',register_view, name = 'register-view'),
    path('trainee', trainee_home_view, name = 'trainee-home-view'),
    path('training_detail/<int:id>',training_detail_view, name = 'training-detail-view' ),
    path('evaluation/<int:id>',evaluation_view,name='evaluation-view'),
    path('score/<int:id>',score_view, name='score-view' ),
    path('training_list', training_list_view, name='training-list-view'),
    path('no_post_test/<int:id>',non_post_test_view, name = 'no-post-test-view' ),
    path('logout',logout_view,name='logout-view')
]
