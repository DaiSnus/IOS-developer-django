from django.contrib import admin
from .models import *

admin.site.register([
    MenuNavigation,
    PageContent,
    RelevanceStatistics,
    RegionalStatistics,
    SkillAnalysis,
])
