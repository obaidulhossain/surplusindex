from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.urls import reverse
from django.http import JsonResponse
from . models import *
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from authentication.decorators import allowed_users
import datetime
from datetime import date, timedelta
from django.views.decorators.csrf import csrf_exempt
import json
from propertydata.models import *
from si_user.models import *
from realestate_directory.models import *
from django.utils.timezone import now
from django.db.models import Prefetch, Count, Q
from django.views.decorators.http import require_POST
from .mailers import send_cycle_leads
from django.core.mail import EmailMessage,send_mail
from email.utils import formataddr
from django.conf import settings
from django.db.models import F
from . resources import *
from django.core.paginator import Paginator
from AllSettings.models import*
import calendar
from .utils import *

# Create your views here.
#-----------------------Project Manager---------------------
@login_required(login_url="login")
@allowed_users(['admin'])
def ProjectManager(request):
    current_year = datetime.date.today().year
    years = range(current_year - 2, current_year + 3)  # two years back & two ahead
    project_instance = None
    cycle_instance = None
    tasks = None
    leads = None
    case_searched = None
    contacts = None
    skiptraced = None
    published = None

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
            leads = Foreclosure.objects.filter(state=project_instance.name, sale_date__range=(cycle_instance.sale_from,cycle_instance.sale_to))
            case_searched = leads.filter(case_search_status="completed")
            contacts = Contact.objects.filter(defendant_for_foreclosure__sale_date__range=(cycle_instance.sale_from,cycle_instance.sale_to)).distinct()
            skiptraced = contacts.filter(skiptraced=True)
            published = leads.filter(published=True)
            
    load_cycles = UpdateCycle.objects.filter(project=project_instance, year=selected_year)

    plans = SubscriptionPlan.objects.all()


    
    
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
        'leads':leads,
        'case_searched':case_searched,
        'contacts':contacts,
        'skiptraced':skiptraced,
        'published':published,
        'plans':plans,



    }

    return render(request, 'ProjectManager/project-manager.html', context)

@login_required(login_url="login")
@allowed_users(['admin'])
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

@login_required(login_url="login")
@allowed_users(['admin'])
def CreateProject(request):
    if request.method == "POST":
        Name = request.POST.get('pr_name')
        Description = request.POST.get('pr_description')
        State = request.POST.get('pr_state')
        Saletype = request.POST.get('pr_saletype')
        Plan = request.POST.get('pr_plan')
        try:
            Plan_Instance = SubscriptionPlan.objects.get(pk=Plan)
        except SubscriptionPlan.DoesNotExist:
            messages.error(request, "Invalid subscription plan selected.")
            return redirect('project_manager')
        
        if Name:  # Prevent creating empty project
            Project, created = Projects.objects.get_or_create(
                state=State,
                sale_type=Saletype,
                plan=Plan_Instance,
                defaults={
                    "name":Name,
                    "description":Description,
                }
            )
            
            messages.success(request, "Project Instance Created")
        else:
            messages.error(request, "Project name cannot be empty.")
        
    return redirect('project_manager')


@login_required(login_url="login")
@allowed_users(['admin'])
def UpdateProject(request):
    if request.method == "POST":
        project_id = request.POST.get('project_id')
        Name = request.POST.get('pr_name')
        Description = request.POST.get('pr_description')
        State = request.POST.get('pr_state')
        UpdateInterval = int(request.POST.get('pr_pfui'))
        Saletype = request.POST.get('pr_saletype')
        Plan = request.POST.get('pr_plan')
        Status = request.POST.get('pr_status', False)
        try:
            Plan_Instance = SubscriptionPlan.objects.get(pk=Plan)
        except SubscriptionPlan.DoesNotExist:
            messages.error(request, "Invalid subscription plan selected.")
            return redirect('project_settings')
        if project_id:
            project_instance = Projects.objects.get(pk=project_id)
            project_instance.name = Name
            project_instance.state = State
            project_instance.sale_type = Saletype
            project_instance.description = Description
            project_instance.post_foreclosure_update_interval = UpdateInterval
            project_instance.plan = Plan_Instance
            project_instance.active = Status
            project_instance.save()
        
            messages.success(request, "Project Instance Updated")
        else:
            messages.error(request, "No Project Selected")
        
    return redirect(f"{reverse('project_settings')}?project_id={project_instance.pk}")


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

@login_required(login_url="login")
@allowed_users(['admin'])
def get_tasks(request, cycle_id):
    # Get the cycle instance
    try:
        cycle = UpdateCycle.objects.get(pk=cycle_id)
    except UpdateCycle.DoesNotExist:
        return JsonResponse({"error": "Cycle not found", "tasks": []}, status=404)
    
    # Get tasks for the cycle
    tasks = Tasks.objects.filter(cycle_id=cycle_id).select_related("project").prefetch_related("assigned_to").order_by("delivery_date")
    
    return redirect(f"{reverse('project_manager')}?project={cycle.project.pk}&cycle-year={cycle.year}&cycle={cycle.pk}")




@login_required(login_url="login")
@allowed_users(['admin'])
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
            cycle_start = cycle_instance.cycle_start
            weekday_date = cycle_start + timedelta(days=int(task.weekday)) - timedelta(days=1)
            delivery_date = weekday_date + timedelta(days=int(task.task_duration))
            #cycle_end = cycle_start + timedelta(days=6)
            # delivery_date = task.cycle.cycle_start.weekday(task.template.weekday) + timedelta(days=task.task_duration)
            reporting_date = delivery_date + timedelta(days=1)
            #status = "backlog" if cycle_end < date.today() else "active"
           
            tasks_to_create.append(Tasks(
                cycle=cycle_instance,
                project=project_instance,
                template = task,
                task_name=task.task_name,
                task_group=task.task_group,
                date_assigned = weekday_date,
                delivery_date = delivery_date,
                reporting_date = reporting_date,
                description = task.job_detail,
                status = "created",
            ))

        try:
            # bulk create for efficiency
            Tasks.objects.bulk_create(tasks_to_create, ignore_conflicts=True)
            cycle_instance.status = "running"
            cycle_instance.save()
            messages.success(request, f'Tasks created for {project_instance.name} Week : {cycle_instance.week}')
        except Exception as e:
            messages.error(request, f'Task creation not successful: {e}')
            print("❌ Error creating task:", e)

    return redirect(f"{reverse('project_manager')}?project={selected_project}&cycle-year={selected_year}&cycle={selected_cycle}")

#-----------------------Dashboard---------------------


@login_required(login_url="login")
@allowed_users(['admin'])
def ProjectDashboard(request):
    user = request.user
    params = request.POST if request.method == "POST" else request.GET
    # ✅ SAVE FILTERS FOR DOWNLOAD
    request.session["dashboard_filters"] = params.dict()

    selectedState = params.get('stateFilter', '')
    selectedCounty = params.get('countyFilter', '')
    selectedSaletype = params.get('saletypeFilter', '')
    published = params.get('published','')

    saledateOrder = params.get('sale_date_order', 'sale_date')
    surplusStatusND = params.get('status_nd', '')
    surplusStatusPS = params.get('status_ps', '')
    surplusStatusNPS = params.get('status_nps', '')
    surplusStatusFA = params.get('status_fa', '')
    surplusStatusMF = params.get('status_mf', '')
    surplusStatusFC = params.get('status_fc', '')
    surplusStatusNS = params.get('status_ns', '')
    saleStatusACTIVE = params.get('sale_status_active', '')
    saleStatusSOLD = params.get('sale_status_sold', '')
    saleStatusUNSOLD = params.get('sale_status_unsold', '')
    saleStatusSOLDTOPLT = params.get('sale_status_soldtoplaintiff', '')
    saleStatusBANKRUPTCY = params.get('sale_status_bankruptcy', '')
    saleStatusCANCELED = params.get('sale_status_canceled', '')

    saleFROM = params.get('sale_from','')
    saleTO = params.get('sale_to','')
    
    saledateYear = params.get('sale_date_year', '')
    if saledateYear.isdigit():
        saledateYear = int(saledateYear)
    
    saledateMonth = params.get('sale_date_month', '')
    if saledateMonth.isdigit():
        saledateMonth = int(saledateMonth)


# -------------Base querysets----------------------------
    # leads_queryset = (
    #     Foreclosure.objects.all()
    #     )
    leads_queryset = (
        Foreclosure.objects
        .annotate(
            total_defendants=Count('defendant', distinct=True),
            unskiptraced_defendants=Count(
                'defendant',
                filter=Q(defendant__skiptraced=False),
                distinct=True
            ),
        )
    )


# -------------Filters-----------------------------------
    filters = {}
    if selectedState:
        filters["state__iexact"] = selectedState
    if selectedCounty:
        filters["county__iexact"] = selectedCounty
    if selectedSaletype:
        filters["sale_type__iexact"] = selectedSaletype
    if published.lower() == "true":
        filters["published"] = True
    elif published.lower() == "false":
        filters["published"] = False
    if saleFROM:
        filters["sale_date__gte"] = saleFROM
    if saleTO:
        filters["sale_date__lte"] = saleTO
    if saledateYear:
        filters["sale_date__year"] = saledateYear
    if saledateMonth:
        filters["sale_date__month"] = saledateMonth
 
    leads_queryset = leads_queryset.filter(**filters)

# --------------- Surplus Status --------------------------------------------------
    surplus_filters = []
    if surplusStatusND:
        surplus_filters.append(surplusStatusND)
    if surplusStatusPS:
        surplus_filters.append(surplusStatusPS)
    if surplusStatusNPS:
        surplus_filters.append(surplusStatusNPS)
    if surplusStatusFA:
        surplus_filters.append(surplusStatusFA)
    if surplusStatusMF:
        surplus_filters.append(surplusStatusMF)
    if surplusStatusFC:
        surplus_filters.append(surplusStatusFC)
    if surplusStatusNS:
        surplus_filters.append(surplusStatusNS)

    if surplus_filters:
        leads_queryset = leads_queryset.filter(surplus_status__in=surplus_filters)
    #-------------------------------------------------------------------------------

# ----------------- Sale Status -------------------------------------------------
    sale_filters = []
    if saleStatusACTIVE:
        sale_filters.append(saleStatusACTIVE)
    if saleStatusSOLD:
        sale_filters.append(saleStatusSOLD)
    if saleStatusCANCELED:
        sale_filters.append(saleStatusCANCELED)
    if saleStatusUNSOLD:
        sale_filters.append(saleStatusUNSOLD)
    if saleStatusSOLDTOPLT:
        sale_filters.append(saleStatusSOLDTOPLT)
    if saleStatusBANKRUPTCY:
        sale_filters.append(saleStatusBANKRUPTCY)

    if sale_filters:
        leads_queryset = leads_queryset.filter(sale_status__in=sale_filters)

    #-------------------------------------------------------------------------------

    # -------------Dropdown Data-------------------------------------------------------------------------------------
    states = Foreclosure.objects.values_list("state", flat=True).order_by("state").distinct()
    if selectedState:
        counties = Foreclosure.objects.filter(state__iexact = selectedState).values_list("county", flat=True).order_by("county").distinct()
        if selectedCounty:
            saletypes = Foreclosure.objects.filter(state__iexact = selectedState, county__iexact = selectedCounty).values_list("sale_type", flat=True).order_by("sale_type").distinct()
        else:
            saletypes = Foreclosure.objects.filter(state__iexact = selectedState).values_list("sale_type", flat=True).order_by("sale_type").distinct()
    else:
        counties = None
        saletypes = None

#--------------Orders-------------------------------------
    if saledateOrder:
        leads_queryset = leads_queryset.order_by("county", saledateOrder)
    else:
        leads_queryset = leads_queryset.order_by("county", "-sale_date")
#     # ---------------------------------------------------------------------------------------------------------------



    total_leads = leads_queryset.count()
    current_year = datetime.date.today().year
    years = range(current_year - 5, current_year + 2)
    months = [(i, calendar.month_name[i]) for i in range(1, 13)]
    client_settings, created = ClientSettings.objects.get_or_create(user=user)
    context = {

        'client_settings':client_settings,
        'current_user':user,
        'leads':leads_queryset,
        'selectedState':selectedState,
        'selectedCounty':selectedCounty,
        'selectedSaletype':selectedSaletype,
        'published':published,
        'states':states,
        'counties':counties,
        'saletypes':saletypes,
        'total_leads':total_leads,
        'saledateOrder':saledateOrder,
        'years':years,
        'months':months,
        'saleFROM':saleFROM,
        'saleTO':saleTO,
        'saledateYear':saledateYear,
        'saledateMonth':saledateMonth,
        'surplusStatusND':surplusStatusND,
        'surplusStatusPS':surplusStatusPS,
        'surplusStatusNPS':surplusStatusNPS, 
        'surplusStatusFA':surplusStatusFA,
        'surplusStatusMF':surplusStatusMF,
        'surplusStatusFC':surplusStatusFC,
        'surplusStatusNS':surplusStatusNS,
        'saleStatusACTIVE':saleStatusACTIVE,
        'saleStatusSOLD':saleStatusSOLD,
        'saleStatusCANCELED':saleStatusCANCELED,
        'saleStatusUNSOLD':saleStatusUNSOLD,
        'saleStatusSOLDTOPLT':saleStatusSOLDTOPLT,
        'saleStatusBANKRUPTCY':saleStatusBANKRUPTCY,
    }
    return render(request, 'ProjectManager/project-dashboard.html', context)
    
    




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
    views = TaskViews.objects.all()
    context = {
        'projects': projects,
        'selected_project': selected_project,
        'project_instance': project_instance,
        'taskloader':taskloader,
        'da_list':da_list,
        'admin_list':admin_list,
        'selected_task':selected_task,
        'task_instance':task_instance,
        'views':views,
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
        task_view = request.POST.get('task_view')
        if task_view:
            view_instance = TaskViews.objects.get(pk=task_view)
            if not task_name:
                task_name = view_instance.taskname
            if not weekday:
                weekday = view_instance.weekday
            if not task_duration:
                task_duration = view_instance.duration
            if not task_group:
                task_group = view_instance.group


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
                    task_instance.taskview = view_instance
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
                        taskview = view_instance,
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

def TaskViewInstance(request):
    if request.method == "POST":
        view_name = request.POST.get('view_name')
        task_name = request.POST.get('task_name')
        weekday = request.POST.get('weekday')
        task_duration = request.POST.get('task_duration')
        task_group = request.POST.get('task_group')
        try:
            view, created = TaskViews.objects.update_or_create(
                viewname = view_name,
                defaults={
                    'taskname' : task_name,
                    'weekday' : weekday,
                    'duration' : task_duration,
                    'group' : task_group,
                    })
            if created:
                messages.success(request, 'Task view instance created')
            else:
                messages.success(request, 'Task view instance updated')
        except Exception as e:
            messages.error(request, f'Task instance creation not successful: {e}')
            print("❌ Error creating task:", e)
    
    return redirect('task_manager')
    

#-----------------------Active Tasks---------------------



def ActiveTasks(request):
    user = request.user
    active_tasks = Tasks.objects.filter(assigned_to=user).order_by('delivery_date')
    context = {
        'active_tasks':active_tasks,
    }
    return render(request, 'ProjectManager/active-tasks.html',context)

#--------------------------Task Viewer ---------------------

def TaskViewer(request):
    user = request.user
    active_tasks = Tasks.objects.filter(assigned_to=user).order_by('delivery_date')

    task_instance = None
    if request.method == "POST":
        selected_task = request.POST.get('task')
        
    else:
        selected_task = request.GET.get('task')
        
    leads = None
    new_leads = None
    case_searched = None
    contacts = None
    skiptraced = None
    published = None
    events = None
    status = "stopped"
    post_foreclosure_case_search_leads = None
    post_foreclosure_searched = None
    post_foreclosure_case_completed = None
    post_foreclosure_case_checklist = None
    all_tasks = None
    tasks_completed = None
    delivery_reports = None
    delivery_success = None
    today = date.today()
    if selected_task:
        task_instance = Tasks.objects.get(pk=selected_task)
        all_tasks = Tasks.objects.filter(cycle=task_instance.cycle).order_by("delivery_date")
        tasks_completed = all_tasks.filter(status="completed")
        leads = Foreclosure.objects.filter(state__iexact=task_instance.project.state, sale_date__range=(task_instance.cycle.sale_from,task_instance.cycle.sale_to))
        new_leads = leads.filter(created_at__range=(task_instance.cycle.cycle_start,task_instance.cycle.cycle_end))
        published = leads.filter(published=True)
        case_searched = leads.filter(case_search_status="completed")

        contacts = Contact.objects.filter(
            defendant_for_foreclosure__sale_date__range=(task_instance.cycle.sale_from,task_instance.cycle.sale_to),
            defendant_for_foreclosure__state__iexact=task_instance.project.state,
            ).distinct()
        skiptraced = contacts.filter(skiptraced=True)
        if task_instance.template.taskview.viewname == "Post Foreclosure Update":
            post_foreclosure_case_search_leads = task_instance.post_foreclosure_cases.all()
            interval = task_instance.project.post_foreclosure_update_interval
            post_foreclosure_case_checklist = post_foreclosure_case_search_leads.filter(changed_at__lt=task_instance.cycle.cycle_start - timedelta(days=interval))
            post_foreclosure_case_completed = post_foreclosure_case_search_leads.filter(changed_at__gte=task_instance.cycle.cycle_start - timedelta(days=1))
            if task_instance.post_foreclosure_case_volume:
                post_foreclosure_searched = int(task_instance.post_foreclosure_case_volume) - post_foreclosure_case_search_leads.count()
        active_subscriptions = StripeSubscription.objects.filter(plan=task_instance.project.plan, current_period_end__gte=task_instance.cycle.cycle_end)
        users = [sub.user for sub in active_subscriptions]
        all_events = foreclosure_Events.objects.filter(state__iexact=task_instance.project.state).order_by('event_next')
        post_events = foreclosure_Events.objects.filter(state__iexact=task_instance.project.state, post_event_next__lt=today).order_by('post_event_next')
        events = foreclosure_Events.objects.filter(state__iexact=task_instance.project.state, event_next__range=(task_instance.cycle.sale_from,task_instance.cycle.sale_to)).order_by("event_next")
        status = task_instance.get_current_status(request.user)
        delivery_reports = DeliveryReport.objects.filter(task=task_instance).order_by("created_at")
        delivery_success = delivery_reports.filter(report="Successful")
    context = {
        'active_tasks':active_tasks,
        'selected_task':selected_task,
        'task_instance':task_instance,
        'all_tasks':all_tasks,
        'tasks_completed':tasks_completed,
        'leads':leads,
        'new_leads':new_leads,
        'case_searched':case_searched,
        'contacts':contacts,
        'skiptraced':skiptraced,
        'published':published,
        'all_events':all_events,
        'post_events':post_events,
        'events':events,
        'status':status,
        'post_foreclosure_case_search_leads':post_foreclosure_case_search_leads,
        'post_foreclosure_case_completed':post_foreclosure_case_completed,
        'post_foreclosure_case_checklist':post_foreclosure_case_checklist,
        'post_foreclosure_searched':post_foreclosure_searched,
        'delivery_reports':delivery_reports,
        'delivery_success':delivery_success,

    }
    return render(request, 'ProjectManager/task-viewer.html',context)

def VerifyAllSkiptraced(request):
    if request.method == "POST":
        selected_task = request.POST.get('task_id')
        task_instance = Tasks.objects.get(pk=selected_task)
        leads = Foreclosure.objects.filter(state__iexact=task_instance.project.state, sale_date__range=(task_instance.cycle.sale_from,task_instance.cycle.sale_to))
        saved, problem = 0, 0
        for lead in leads:
            try:
                if lead.case_search_status == "Completed" and lead.defendant.filter(skiptraced=True).exists():
                    lead.case_search_status = "Verified"
                    lead.save(update_fields=["case_search_status"])
                    saved += 1
            except:
                problem += 1
        messages.info(request, f"{saved} skiptraced case marked as verified and problem verifying {problem}")
    else:
        messages.info(request, "Post Method Required")
        return redirect(f"{reverse('task_viewer')}?task={task_instance.id}")
    return redirect(f"{reverse('task_viewer')}?task={task_instance.id}")




def VerifyAll(request):
    if request.method == "POST":
        selected_task = request.POST.get('task_id')
        task_instance = Tasks.objects.get(pk=selected_task)
        leads = Foreclosure.objects.filter(state__iexact=task_instance.project.state, sale_date__range=(task_instance.cycle.sale_from,task_instance.cycle.sale_to))
        saved, problem = 0, 0
        for lead in leads:
            try:
                if lead.case_search_status == "Completed":
                    lead.case_search_status = "Verified"
                    lead.save(update_fields=["case_search_status"])
                    saved += 1
            except:
                problem += 1
        messages.info(request, f"{saved} marked as verified and problem verifying {problem}")
    else:
        messages.info(request, "Post Method Required")
        return redirect(f"{reverse('task_viewer')}?task={task_instance.id}")
    return redirect(f"{reverse('task_viewer')}?task={task_instance.id}")


def PublishAllSkiptraced(request):
    if request.method == "POST":
        selected_task = request.POST.get('task_id')
        task_instance = Tasks.objects.get(pk=selected_task)
        leads = Foreclosure.objects.filter(state__iexact=task_instance.project.state, sale_date__range=(task_instance.cycle.sale_from,task_instance.cycle.sale_to))
        saved, problem = 0, 0
        for lead in leads:
            try:
                if lead.case_search_status == "Verified" and lead.published == False :
                    lead.published = True
                    lead.save(update_fields=["published"])
                    saved += 1
            except:
                problem += 1
        messages.info(request, f"{saved} Published and Error Publishing {problem}")
    else:
        messages.info(request, "Post Method Required")
        return redirect(f"{reverse('task_viewer')}?task={task_instance.id}")
    return redirect(f"{reverse('task_viewer')}?task={task_instance.id}")


def PublishAll(request):
    if request.method == "POST":
        selected_task = request.POST.get('task_id')
        task_instance = Tasks.objects.get(pk=selected_task)
        leads = Foreclosure.objects.filter(state__iexact=task_instance.project.state, sale_date__range=(task_instance.cycle.sale_from,task_instance.cycle.sale_to))
        saved, problem = 0, 0
        for lead in leads:
            try:
                if lead.published == False:
                    lead.published = True
                    lead.save(update_fields=["published"])
                    saved += 1
            except:
                problem += 1
        messages.info(request, f"{saved} Published and Error Publishing {problem}")
    else:
        messages.info(request, "Post Method Required")
        return redirect(f"{reverse('task_viewer')}?task={task_instance.id}")
    return redirect(f"{reverse('task_viewer')}?task={task_instance.id}")


@require_POST
def deliver_cycle_leads(request, task_id):
    task_instance = get_object_or_404(Tasks, id=task_id)
    

    active_subscriptions = StripeSubscription.objects.filter(
        plan=task_instance.project.plan,
        current_period_end__gte=task_instance.cycle.cycle_end
    )
    if not active_subscriptions.exists():
        messages.info(request, f"No Active Subscription found for {task_instance.project.plan.name}")
        return redirect(f"{reverse('task_viewer')}?task={task_instance.id}")

    # 2. Leads within cycle date range
    leads = Foreclosure.objects.filter(
        state__iexact=task_instance.project.state,
        published=True,
        sale_date__range=(task_instance.cycle.sale_from, task_instance.cycle.sale_to)
    )
    if not leads.exists():
        messages.info(request, f"No  leads found in {task_instance.project.state} for sale date range {task_instance.cycle.sale_from} - {task_instance.cycle.sale_to}")
        return redirect(f"{reverse('task_viewer')}?task={task_instance.id}")
    
    # email_sender = settings.DEFAULT_FROM_EMAIL
    email_sender = formataddr(("SurplusIndex", settings.DEFAULT_FROM_EMAIL))

    users = [sub.user for sub in active_subscriptions]

    for sub in active_subscriptions:
        user = sub.user
        user_name = user.get_full_name() or user.username
        
        subject = f"Leads Report for Cycle {task_instance.cycle.week} Updated"
        body = (
            f"Hello {user_name},\n\n"
            f"Please find the Pre-Foreclosure leads set for sale in auction between sale date range"
            f"{task_instance.cycle.sale_from.strftime('%Y-%m-%d')} and "
            f"{task_instance.cycle.sale_to.strftime('%Y-%m-%d')}.\n"
            f"Leads are available in My Surplus Data section in your SurplusIndex account.\n\n"
            f"Best regards,\n"
            f"SurplusIndex Team"
        )

        # 1. Prepare bulk Status inserts
        existing_statuses = set(
            Status.objects.filter(lead__in=leads, client=user)
            .values_list("lead_id", flat=True)
        )
        new_statuses = [
            Status(lead=lead, client=user)
            for lead in leads
            if lead.id not in existing_statuses
        ]
        if new_statuses:
            Status.objects.bulk_create(new_statuses, ignore_conflicts=True)

            report, created = DeliveryReport.objects.get_or_create(
            task=task_instance,
            user=user,
            defaults={"delivered": len(new_statuses)}
            )

            if not created:
                DeliveryReport.objects.filter(pk=report.pk).update(
                    delivered=F("delivered") + len(new_statuses)
                    )
            report.refresh_from_db()
            # Send mail to this user    
            try:
                send_mail(subject, body, email_sender, [user.email], fail_silently=False)
                # email = EmailMessage(
                #     subject=subject,
                #     body=body,
                #     from_email=email_sender,
                #     to=[user.email],
                # )
                # email.send(fail_silently=False)
                messages.info(request, f"Successfully sent email to {user.email}")
                report.report = "Successful"
            except Exception as e:
                messages.error(request, f"Failed to send email to {user.email}: {e}")
                report.report = f"Failed to send email to {user.email}: {e}"
            report.save()
        else:
            messages.info(request, f"All the leads are already delivered")
    # Bulk add users to purchased_by for all leads
    for lead in leads:
        lead.purchased_by.add(*users)

    return redirect(f"{reverse('task_viewer')}?task={task_instance.id}")



def start_task(request, task_id):
    task = get_object_or_404(Tasks, id=task_id)
    if task.template.taskview.viewname == "Post Foreclosure Update":
        interval = task.project.post_foreclosure_update_interval
        leads_queryset = Foreclosure.objects.filter(state__iexact=task.project.state, sale_status='Sold', changed_at__lt=now().date() - timedelta(days=interval)).exclude(surplus_status='Fund Claimed').exclude(surplus_status='No Surplus')
        if task.post_foreclosure_cases.count() < 1:
            task.post_foreclosure_cases.add(*leads_queryset)
            task.post_foreclosure_case_volume = task.post_foreclosure_cases.count()
        

    if task.template.taskview.viewname == "Initiate Deliveries":
        active_subscriptions = StripeSubscription.objects.filter(plan=task.project.plan,current_period_end__gte=task.cycle.cycle_end)
        task.active_subscribers.add(*active_subscriptions)
        task.save()
        

       

    # Resume = just create a new tracker
    TimeTracker.objects.create(task=task, user=request.user, start_time=now())
    task.tracker_status = "started"
    task.status = "assigned"
    task.save()

    return redirect(f"{reverse('task_viewer')}?task={task.id}")


def pause_task(request, task_id):
    task = get_object_or_404(Tasks, id=task_id)
    tracker = task.time_logs.filter(user=request.user, end_time__isnull=True,).last()
    
    if tracker:
        tracker.end_time = now()
        
        tracker.save()

        # update cumulative time captured
        task.time_captured += tracker.duration()
        task.tracker_status = "paused"
        task.save()

    return redirect(f"{reverse('task_viewer')}?task={task.id}")


def stop_task(request, task_id):
    task = get_object_or_404(Tasks, id=task_id)
    tracker = task.time_logs.filter(user=request.user, end_time__isnull=True).last()
    if tracker:
        tracker.end_time = now()
        tracker.is_paused = False
        tracker.save()

        task.time_captured += tracker.duration()
    task.tracker_status = "stopped"
    task.save()

    return redirect(f"{reverse('task_viewer')}?task={task.id}")

def MarkasDelivered(request):
    if request.method == "POST":
        task = request.POST.get('task_id')
        pf_list = request.POST.get('pf_list', None)
        if task:
            task_instance = Tasks.objects.get(id=task)
            task_instance.cycle.pf_list = pf_list
            task_instance.cycle.save()
            task_instance.status = "delivered"
            task_instance.save()
            messages.success(request, 'Task marked as dlivered')
    return redirect(f"{reverse('task_viewer')}?task={task_instance.id}")

def DeliverUploadTask(request):
    if request.method == "POST":
        task = request.POST.get('task_id')
        if task:
            task_instance = Tasks.objects.get(id=task)
            leads = Foreclosure.objects.filter(state__iexact=task_instance.project.state, sale_date__range=(task_instance.cycle.sale_from,task_instance.cycle.sale_to))
            task_instance.lead_volume = leads.count()
            task_instance.status = "delivered"
            task_instance.save()
            messages.success(request, 'Task marked as Delivered')
    return redirect(f"{reverse('task_viewer')}?task={task_instance.id}")

def DeliverCasesearchTask(request):
    if request.method == "POST":
        task = request.POST.get('task_id')
        if task:
            task_instance = Tasks.objects.get(id=task)
            leads = Foreclosure.objects.filter(state__iexact=task_instance.project.state, sale_date__range=(task_instance.cycle.sale_from,task_instance.cycle.sale_to), case_search_status="completed")
            contacts = Contact.objects.filter(defendant_for_foreclosure__sale_date__range=(task_instance.cycle.sale_from,task_instance.cycle.sale_to)).distinct()
            if task_instance.contact_volume != "" or task_instance.contact_volume != None:
                task_instance.contact_volume = contacts.count()
            task_instance.case_searched = leads.count()
            task_instance.status = "delivered"
            task_instance.save()
            messages.success(request, 'Task marked as Delivered')
    return redirect(f"{reverse('task_viewer')}?task={task_instance.id}")

def DeliverSkiptraceTask(request):
    if request.method == "POST":
        task = request.POST.get('task_id')
        if task:
            task_instance = Tasks.objects.get(id=task)
            contacts = Contact.objects.filter(defendant_for_foreclosure__sale_date__range=(task_instance.cycle.sale_from,task_instance.cycle.sale_to)).distinct()
            if task_instance.contact_volume != "" or task_instance.contact_volume != None:
                task_instance.contact_volume = contacts.count()
            skiptraced = contacts.filter(skiptraced=True)
            task_instance.skiptraced = skiptraced.count()
            task_instance.status = "delivered"
            task_instance.save()
            messages.success(request, 'Task marked as Delivered')
    return redirect(f"{reverse('task_viewer')}?task={task_instance.id}")

def DeliverPublishTask(request):
    if request.method == "POST":
        task = request.POST.get('task_id')
        if task:
            task_instance = Tasks.objects.get(id=task)
            leads = Foreclosure.objects.filter(state__iexact=task_instance.project.state, sale_date__range=(task_instance.cycle.sale_from,task_instance.cycle.sale_to))
            published = leads.filter(published=True)
            task_instance.published = published.count()
            task_instance.status = "delivered"
            task_instance.save()
            messages.success(request, 'Task marked as Delivered')
    return redirect(f"{reverse('task_viewer')}?task={task_instance.id}")




def DeliverPostForeclosureCasesearchTask(request):
    if request.method == "POST":
        task = request.POST.get('task_id')
        if task:
            task_instance = Tasks.objects.get(id=task)
            interval = task_instance.project.post_foreclosure_update_interval
            leads_queryset = Foreclosure.objects.filter(state__iexact=task_instance.project.state, sale_status='Sold', changed_at__lt=now().date() - timedelta(days=interval)).exclude(surplus_status='Fund Claimed').exclude(surplus_status='No Surplus')
            task_instance.post_foreclosure_cases.remove(*leads_queryset)
            task_instance.post_foreclosure_case_searched = task_instance.post_foreclosure_cases.count()
            task_instance.status = "delivered"
            task_instance.save()
            messages.success(request, 'Task marked as Delivered')
    return redirect(f"{reverse('task_viewer')}?task={task_instance.id}")

def DeliverUpdateCycle(request):
    if request.method == "POST":
        task = request.POST.get('task_id')
        if task:
            task_instance = Tasks.objects.get(id=task)
            all_tasks = Tasks.objects.filter(cycle=task_instance.cycle).exclude(template__taskview__viewname = "Update Cycle")
            for tasks in all_tasks:
                if tasks.status != "completed":
                    messages.error(request, 'Delivery Not Successful! Please make sure all the tasks have been completed')
                    return redirect(f"{reverse('task_viewer')}?task={task_instance.id}")
                
            task_instance.status = "completed"
            task_instance.cycle.status = "completed"
            task_instance.cycle.save()
            task_instance.save()
            messages.success(request, 'Task marked as Completed')
    return redirect(f"{reverse('task_viewer')}?task={task_instance.id}")

def SaveNote(request):
    if request.method == "POST":
        task = request.POST.get('task_id')
        note = request.POST.get('notes')
        if task:
            task_instance = Tasks.objects.get(id=task)
            task_instance.note = note
            task_instance.save()
            messages.success(request, 'Note Saved!')
    return redirect(f"{reverse('task_viewer')}?task={task_instance.id}")


#-----------------------Delivered Tasks---------------------




def DeliveredTasks(request):
    return render(request, 'ProjectManager/delivered-tasks.html')




#-----------------------Project Settings---------------------




def ProjectSettings(request):
    projects = Projects.objects.all()
    plans = SubscriptionPlan.objects.all()
    params = request.POST if request.method == "POST" else request.GET
    selected_project = params.get('project_id', '')
    
    project_instance = None
    if selected_project:
        project_instance = Projects.objects.get(pk=selected_project)

    context = {
        "projects":projects,
        "plans":plans,
        "selected_project":selected_project,
        "project_instance":project_instance,

    }
    return render(request, 'ProjectManager/project-settings.html', context)




# -----------------------------Make Delivery of Project_Cycle data to clients---------------------------


# --------------------------------------------------------------------------------



@login_required(login_url="login")
@allowed_users(['admin'])
def download_dashboard_leads(request):
    params = request.session.get("dashboard_filters", {})
    queryset = get_filtered_foreclosure_queryset(params)


    resource = DashboardCloneExportResource(queryset)
    filename, buffer, _ = resource.export_to_excel("dashboard_filtered_leads")

    response = HttpResponse(
        buffer.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response

