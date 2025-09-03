from django.urls import path
from . import views


urlpatterns = [
    path('case_checklist', views.caseChecklist, name="case_checklist"),
    path('skiptracing_checklist', views.SkiptracingChecklist, name="skiptracing_checklist"),
    



]