from django.urls import path
from .views import *

urlpatterns = [
    path('', LandingPage.as_view(), name="home"),
    path('general/', GeneralPageView.as_view(), name="general"),
    path('top-skills/', TopSkillsPage.as_view(), name="top-skills"),
    path('relevance/', RelevancePage.as_view(), name="relevance"),
    path('regional/', RegionalPage.as_view(), name="geography"),
    path('skills/', SkillsPage.as_view(), name="skills")
]