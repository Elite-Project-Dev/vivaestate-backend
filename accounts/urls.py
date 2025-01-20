from django.urls import path
from .views import AgentSignupView , UserSignupView

urlpatterns = [
    path('agent/signup/', AgentSignupView.as_view(), name='agent-signup'),
    path('user/signup/', UserSignupView.as_view(), name='user-signup')
]
