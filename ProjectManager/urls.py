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
path('create-update-task-view/',views.TaskViewInstance, name="create-update-task-view" ),

path('task-viewer/', views.TaskViewer, name="task_viewer"),
path('task-viewer/<int:task_id>/start/', views.start_task, name="start_task"),
path('task-viewer/<int:task_id>/pause/', views.pause_task, name="pause_task"),
path('task-viewer/<int:task_id>/stop/', views.stop_task, name="stop_task"),
path('deliver-task/', views.MarkasDelivered, name="deliver-task"),
path('deliver-upload-task/', views.DeliverUploadTask, name="deliver-upload-task"),
path('deliver-casesearch-task/', views.DeliverCasesearchTask, name="deliver-casesearch-task"),
path('deliver-skiptrace-task/', views.DeliverSkiptraceTask, name="deliver-skiptrace-task"),
path('deliver-publish-task/', views.DeliverPublishTask, name="deliver-publish-task"),
path('deliver-update-cycle-task/',views.DeliverUpdateCycle, name="deliver-update-cycle-task"),


path('deliver-post-foreclosure-case-task/', views.DeliverPostForeclosureCasesearchTask, name="deliver-post-foreclosure-case-task"),
path('save-note/',views.SaveNote, name="save_note"),

path('active-tasks/', views.ActiveTasks, name="active_tasks"),
path('delivered-tasks/', views.DeliveredTasks, name="delivered_tasks"),
path('project-settings/', views.ProjectSettings, name="project_settings"),
]