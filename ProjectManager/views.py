from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import JsonResponse
from . models import *
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import datetime
from datetime import date, timedelta
from django.views.decorators.csrf import csrf_exempt
import json
# Create your views here.
#-----------------------Project Manager---------------------

def ProjectManager(request):
    current_year = datetime.date.today().year
    years = range(current_year - 2, current_year + 3)  # two years back & two ahead
    project_instance = None
    cycle_instance = None
    tasks = None
    if request.method == 'POST':
        selected_project = request.POST.get('project', False)
        selected_year = int(request.POST.get('cycle-year', current_year))
        selected_cycle = request.POST.get('cycle', None)
    else:
        selected_project = request.GET.get('project', False)
        selected_year = int(request.GET.get('cycle-year', current_year))
        selected_cycle = request.GET.get('cycle', None)
    
    
    
    projects = Projects.objects.filter(active=True).order_by('name')
    today = date.today()
    if selected_project:
        project_instance = Projects.objects.get(pk=selected_project)
        if selected_cycle:
            cycle_instance = UpdateCycle.objects.get(pk = selected_cycle)
            tasks = Tasks.objects.filter(cycle=cycle_instance).select_related("project").prefetch_related("assigned_to").order_by("delivery_date")
            for task in tasks:
                if task.status == "delivered":
                    task.css_class = "delivered"
                elif task.status == "assigned":
                    task.css_class = "assigned"
                elif task.status == "completed":
                    task.css_class = "task-completed"
                elif task.status == "created":
                    task.css_class = "created"
                elif task.delivery_date and task.delivery_date < today:
                    task.css_class = "delivery-due"
                else:
                    task.css_class = ""
    
    load_cycles = UpdateCycle.objects.filter(project=project_instance, year=selected_year)
    
    context = {
        'projects' : projects,
        'selected_project' : selected_project,
        'project_instance' : project_instance,
        'years': years,
        'current_year': current_year,
        'selected_year': selected_year,
        'load_cycles':load_cycles,
        'selected_cycle':selected_cycle,
        'cycle_instance':cycle_instance,
        'tasks':tasks,
        'today':today,
    }

    return render(request, 'ProjectManager/project-manager.html', context)
@login_required
def CreateUpdateCycles(request):
    if request.method == "POST":
        selected_project = request.POST.get('project')
        selected_year = int(request.POST.get("cycle-year"))
        project_instance = Projects.objects.get(pk=selected_project)
        
        # Start date = first Monday of the year
        year_start = date(selected_year, 1, 1)
        if year_start.weekday() != 0:  # 0 = Monday
            year_start += timedelta(days=(7 - year_start.weekday()))
        # Last day of the year
        year_end = date(selected_year, 12, 31)
        # Extend to next Sunday if year_end isn’t Sunday
        if year_end.weekday() != 6:  # 6 = Sunday
            year_end += timedelta(days=(6 - year_end.weekday()))
        
        cycles_to_create = []
        week_num = 1
        cycle_start = year_start
        while cycle_start <= year_end:
            cycle_end = cycle_start + timedelta(days=6)
            sale_from = cycle_start + timedelta(days=15)
            sale_to = sale_from + timedelta(days=6)
            status = "backlog" if cycle_end < date.today() else "active"
            cycles_to_create.append(UpdateCycle(
                project=project_instance,
                year=selected_year,
                week=week_num,
                cycle_start=cycle_start,
                cycle_end=cycle_end,
                sale_from=sale_from,
                sale_to=sale_to,
                status=status
            ))

            week_num += 1
            cycle_start = cycle_start + timedelta(weeks=1)
        # bulk create for efficiency
        UpdateCycle.objects.bulk_create(cycles_to_create, ignore_conflicts=True)

        messages.success(request, f"{len(cycles_to_create)} update cycles created for {project_instance.name} ({selected_year})")
        return redirect(f"{reverse('project_manager')}?project={selected_project}&cycle-year={selected_year}")

    return redirect("project_manager")


@login_required
def CreateProject(request):
    if request.method == "POST":
        Name = request.POST.get('pr_name')
        Description = request.POST.get('pr_description')

        if Name:  # Prevent creating empty project
            Projects.objects.create(name=Name, description=Description)
            messages.success(request, "Project Instance Created")
        else:
            messages.error(request, "Project name cannot be empty.")
        
    return redirect('project_manager')


@csrf_exempt  # or use @csrf_protect if posting with CSRF
def UpdateStatus(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            task_id = data.get("task_id")
            status = data.get("status")

            task = Tasks.objects.get(id=task_id)
            task.status = status
            task.save()
            return JsonResponse({"success": True, "status": status})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    return JsonResponse({"success": False, "error": "Invalid request"})


@csrf_exempt  # or use @csrf_protect if posting with CSRF
def update_assignment(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            task_id = data.get("task_id")
            user_id = data.get("user_id")

            task = Tasks.objects.get(id=task_id)
            user = User.objects.get(id=user_id)

            if user in task.assigned_to.all():
                task.assigned_to.remove(user)  # ✅ Unassign
                status = "removed"
            else:
                task.assigned_to.add(user)  # ✅ Assign
                status = "added"
            if task.status not in ["delivered", "completed"]:
                if task.assigned_to.count() < 1:
                    task.status = "created"
                else:
                    task.status = "assigned"
                task.save()
            return JsonResponse({"success": True, "status": status})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    return JsonResponse({"success": False, "error": "Invalid request"})


def get_tasks(request, cycle_id):
    # Get the cycle instance
    try:
        cycle = UpdateCycle.objects.get(pk=cycle_id)
    except UpdateCycle.DoesNotExist:
        return JsonResponse({"error": "Cycle not found", "tasks": []}, status=404)
    
    # Get tasks for the cycle
    tasks = Tasks.objects.filter(cycle_id=cycle_id).select_related("project").prefetch_related("assigned_to").order_by("delivery_date")
    
    # Prepare task data
    # task_data = []
    # for task in tasks:
    #     task_data.append({
    #         "task_name": task.task_name,
    #         "task_group": task.task_group,
    #         "status": task.status,
    #         "assigned_to": [u.username for u in task.assigned_to.all()],
    #         "delivery_date": task.delivery_date,
    #     })

    # # Include cycle info
    # cycle_info = {
    #     "id": cycle.id,
    #     "project":cycle.project.pk,
    #     "week": cycle.week,
    #     "cycle_start": cycle.cycle_start.strftime("%Y-%m-%d"),
    #     "cycle_end": cycle.cycle_end.strftime("%Y-%m-%d"),
    #     "sale_from": cycle.sale_from.strftime("%Y-%m-%d"),
    #     "sale_to": cycle.sale_to.strftime("%Y-%m-%d"),
    #     "status": cycle.status,
    #     "year": cycle.year,
    # }
    return redirect(f"{reverse('project_manager')}?project={cycle.project.pk}&cycle-year={cycle.year}&cycle={cycle.pk}")



# def get_tasks(request, cycle_id):
#     # Get the cycle instance
#     try:
#         cycle = UpdateCycle.objects.get(pk=cycle_id)
#     except UpdateCycle.DoesNotExist:
#         return JsonResponse({"error": "Cycle not found", "tasks": []}, status=404)
    
#     # Get tasks for the cycle
#     tasks = Tasks.objects.filter(cycle_id=cycle_id).select_related("project").prefetch_related("assigned_to").order_by("delivery_date")
    
#     # Prepare task data
#     task_data = []
#     for task in tasks:
#         task_data.append({
#             "task_name": task.task_name,
#             "task_group": task.task_group,
#             "status": task.status,
#             "assigned_to": [u.username for u in task.assigned_to.all()],
#             "delivery_date": task.delivery_date,
#         })

#     # Include cycle info
#     cycle_info = {
#         "id": cycle.id,
#         "project":cycle.project.pk,
#         "week": cycle.week,
#         "cycle_start": cycle.cycle_start.strftime("%Y-%m-%d"),
#         "cycle_end": cycle.cycle_end.strftime("%Y-%m-%d"),
#         "sale_from": cycle.sale_from.strftime("%Y-%m-%d"),
#         "sale_to": cycle.sale_to.strftime("%Y-%m-%d"),
#         "status": cycle.status,
#         "year": cycle.year,
#     }
#     return JsonResponse({
#         "cycle": cycle_info,
#         "tasks": task_data
#     })


def LoadTasks(request):
    if request.method == "POST":
        selected_project = request.POST.get('project')
        selected_year = request.POST.get('year')
        selected_cycle = request.POST.get('cycle')

        project_instance = Projects.objects.get(pk=selected_project)
        cycle_instance = UpdateCycle.objects.get(pk=selected_cycle)
        task_loader = TasksTemplate.objects.filter(project=project_instance, archived=False)
        reporting_date = cycle_instance.cycle_end
        tasks_to_create = []
        for task in task_loader:
            #cycle_end = cycle_start + timedelta(days=6)
            delivery_date = date.today() + timedelta(days=task.task_duration)
            reporting_date = delivery_date + timedelta(days=1)
            #status = "backlog" if cycle_end < date.today() else "active"
           
            tasks_to_create.append(Tasks(
                cycle=cycle_instance,
                project=project_instance,
                template = task,
                task_name=task.task_name,
                task_group=task.task_group,
                date_assigned = date.today(),
                delivery_date = delivery_date,
                reporting_date = reporting_date,
                description = task.job_detail,
                status = "created",
            ))

        try:
            # bulk create for efficiency
            Tasks.objects.bulk_create(tasks_to_create, ignore_conflicts=True)
            messages.success(request, f'Tasks created for {project_instance.name} Week : {cycle_instance.week}')
        except Exception as e:
            messages.error(request, f'Task creation not successful: {e}')
            print("❌ Error creating task:", e)

    return redirect(f"{reverse('project_manager')}?project={selected_project}&cycle-year={selected_year}&cycle={selected_cycle}")

#-----------------------Dashboard---------------------



def ProjectDashboard(request):
    return render(request, 'ProjectManager/project-dashboard.html')




#-----------------------Task Manager---------------------


def TaskManager(request):
    selected_project = (
        request.POST.get("project") or request.GET.get("project")
    )
    selected_task = (
        request.POST.get("task") or request.GET.get("task")
    )
    task_instance = None
    project_instance = None
    taskloader = None
    if selected_project and selected_project.isdigit():
        selected_project = int(selected_project)
        project_instance = Projects.objects.get(pk=selected_project)
        taskloader = TasksTemplate.objects.filter(project=project_instance)

    if selected_task:
        task_instance = TasksTemplate.objects.get(pk=selected_task)

    projects = Projects.objects.filter(active=True).order_by("name").distinct()
    da_list = User.objects.filter(groups__name='researcher')
    admin_list = User.objects.filter(groups__name='admin')
    context = {
        'projects': projects,
        'selected_project': selected_project,
        'project_instance': project_instance,
        'taskloader':taskloader,
        'da_list':da_list,
        'admin_list':admin_list,
        'selected_task':selected_task,
        'task_instance':task_instance,
    }
    return render(request, 'ProjectManager/task-manager.html', context)

def TaskLoaderInstance(request):
    if request.method == "POST":
        selected_project = request.POST.get("project")
        selected_task = request.POST.get("task")
        task_name = request.POST.get('task_name')
        weekday = request.POST.get('weekday')
        task_duration = request.POST.get('task_duration')
        task_group = request.POST.get('task_group')
        assigned_to = request.POST.getlist('assigned_to')
        job_description = request.POST.get('job_description')

        if selected_project:
            project_instance = Projects.objects.get(pk=selected_project)
            

            try:
                if selected_task:
                    task_instance = TasksTemplate.objects.get(pk=selected_task)
                    task_instance.task_name = task_name
                    task_instance.weekday = weekday
                    task_instance.task_group = task_group
                    task_instance.job_detail = job_description
                    task_instance.task_duration = task_duration
                    task_instance.assigned_to.clear()
                    for username in assigned_to:
                        assigned_to_user = User.objects.get(username=username)
                        task_instance.assigned_to.add(assigned_to_user)
                    task_instance.save()
                    messages.success(request, f'Task instance in {project_instance.name} updated successfully.')
                else:
                    task = TasksTemplate.objects.create(
                        project = project_instance,
                        weekday = weekday,
                        task_duration = task_duration,
                        task_group = task_group,
                        task_name = task_name,
                        job_detail = job_description,
                    )
                    for username in assigned_to:
                        assigned_to_user = User.objects.get(username=username)
                        task.assigned_to.add(assigned_to_user)
                    messages.success(request, f'A task instance created to be loaded in {project_instance.name}')
            except Exception as e:
                messages.error(request, f'Task instance creation not successful: {e}')
                print("❌ Error creating task:", e)
    else:
        selected_project = request.GET.get("project")
    
    return redirect(f"{reverse('task_manager')}?project={selected_project}")



#-----------------------Active Tasks---------------------




def ActiveTasks(request):
    return render(request, 'ProjectManager/active-tasks.html')




#-----------------------Delivered Tasks---------------------




def DeliveredTasks(request):
    return render(request, 'ProjectManager/delivered-tasks.html')




#-----------------------Project Settings---------------------




def ProjectSettings(request):
    return render(request, 'ProjectManager/project-settings.html')
