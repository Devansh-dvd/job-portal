from django.urls import path
from .apiviews import (
    register,
    login,
    create_application,
    register_hiring_team,
    login_hiring_team,
    me,
    list_candidates,
    create_interview_booking,
    list_interviews,
)
from rest_framework_simplejwt.views import (TokenObtainPairView, TokenRefreshView)

urlpatterns = [
    path('register/', register),
    path('login/', login),
    path('me/', me, name='me'),
    path("applications/", create_application),
    path('hiring-team/register/', register_hiring_team),
    path('hiring-team/login/', login_hiring_team),
    path('candidates/', list_candidates, name='list_candidates'),
    path('interviews/', create_interview_booking, name='create_interview_booking'),
    path('interviews/my/', list_interviews, name='list_interviews'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
