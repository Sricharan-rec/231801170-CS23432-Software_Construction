from django.urls import path
from . import views


urlpatterns = [
    path('signin/', views.signin, name='signin'),
    path('signup/', views.signup, name='signup'),
    path('', views.dashboard, name='dashboard'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),  # Leaderboard URL
    path('result/',views.result,name = 'result'),
    path('logout/', views.logout_view, name='logout'),
     path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<uidb64>/<token>/', views.reset_password, name='reset_password'),
   path('quiz/<int:quiz_id>/', views.quiz_view, name='quiz'),
    path('submit-quiz/<int:topic_id>/', views.submit_quiz, name='submit_quiz'),

    path('profile',views.profile,name="profile")
]