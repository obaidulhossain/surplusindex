from django.urls import path
from . import views


urlpatterns = [

# Urls for Active Case Search Section

# Urls for Active Skiptracing Section
path('dashboard/', views.ProjectDashboard, name="project_dashboard"),

path('', views.ProjectManager, name="project_manager"),
path('create-project',views.CreateProject, name="create_project"),
path('createupdatecycles',views.CreateUpdateCycles, name="create_cycles"),
path("get-tasks/<int:cycle_id>/", views.get_tasks, name="get_tasks"),
path('load-tasks/', views.LoadTasks, name="load_tasks"),
path("update-assignment/", views.update_assignment, name="update_assignment"),
path('update-status/', views.UpdateStatus, name="update_status"),


path('task-manager/', views.TaskManager, name="task_manager"),
path('create-update-task-loader/', views.TaskLoaderInstance, name="create-update-task-loader"),

path('active-tasks/', views.ActiveTasks, name="active_tasks"),
path('delivered-tasks/', views.DeliveredTasks, name="delivered_tasks"),
path('project-settings/', views.ProjectSettings, name="project_settings"),
]