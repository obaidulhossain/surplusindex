from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_GET
import json
from django.http import JsonResponse
from authentication.decorators import allowed_users
from django.db.models import OuterRef, Subquery, Count, Q, Case, When, Value, CharField
from .models import*
from django.utils import timezone
import pytz



def format_user_time(dt, user):
    """
    Convert a UTC datetime (from created_at) to the user's timezone and format it nicely.
    """
    # Step 1: get user's timezone
    user_tz_name = getattr(user, "timezone", "Asia/Dhaka")  # default to your local
    user_tz = pytz.timezone(user_tz_name)

    # Step 2: convert UTC -> user timezone
    local_dt = timezone.localtime(dt, user_tz)  # Django handles aware datetimes correctly

    # Step 3: format nicely
    return local_dt.strftime("%b. %d, %Y, %I:%M %p").lower().replace("am", "a.m.").replace("pm", "p.m.")

# Create your views here.
def getAssistance(request):
    params = request.POST if request.method == "POST" else request.GET
    selected_conv = params.get("selected_conv", None)
    if selected_conv:
        conv = Conversation.objects.get(pk=selected_conv)
    else:
        conv = Conversation.objects.filter(client = request.user, status = "open").first()
        if not conv:
            conv = Conversation.objects.create(client=request.user)
    
    con_messages = (
        Messages.objects
        .filter(conversation_id=conv.id)
        .order_by('created_at')
        ).annotate(
            msgtype = Case(
            When(sender=request.user, then=Value('sent')),
            default=Value('received'),
            output_field=CharField()
        )
        )
    for m in con_messages:
        m.message_time = format_user_time(m.created_at, request.user)
    
    last_message_qs = Messages.objects.filter(conversation=OuterRef('pk')).order_by('-created_at')
    conversations = Conversation.objects.filter(client=request.user).annotate(
        last_msg = Subquery(last_message_qs.values('text')[:1]),
        last_sender_id=Subquery(last_message_qs.values('sender_id')[:1]),
        unread = Count('messages', filter=Q(messages__is_seen=False) & ~Q(messages__sender=request.user))
    )




    context = {
        'conversations':conversations,
        'conv':conv,
        'con_messages':con_messages,
    }
    return render(request, 'Assistance/get_assistance.html', context)

@login_required
def fetch_messages(request, conv_id):
    qs = Messages.objects.filter(conversation_id=conv_id).order_by('created_at')
    if qs:
        qs.filter(is_seen=False).exclude(sender=request.user).update(is_seen=True)
    messages = [
    {
        "id": m.id,
        "text": m.text,
        "sender_type": m.sender_type,
        "message_time": format_user_time(m.created_at, request.user)
    }
    for m in qs
    ]
    # messages = (
    #     Messages.objects
    #     .filter(conversation_id=conv_id)
    #     .order_by('created_at')
    #     .values(
    #         'id',
    #         'text',
    #         'sender_type',
    #         'sender_id',
    #         'created_at'
    #     )
    # )

    return JsonResponse({
        "messages": list(messages)
    })


@login_required
@require_POST
def send_message(request):
    data = json.loads(request.body)

    conv_id = data.get("conversation_id")
    text = data.get("message")

    if not text.strip():
        return JsonResponse({"error": "Empty message"}, status=400)

    conversation = Conversation.objects.get(
        id=conv_id,
    )
    if request.user.groups.filter(name="admin").exists():
        sender_type = "admin"
    else:
        sender_type = "user"

    msg = Messages.objects.create(
        conversation=conversation,
        sender=request.user,
        sender_type=sender_type,
        text=text,
    )

    return JsonResponse({
        "id": msg.id,
        "text": msg.text,
        "sender_type": msg.sender_type,
        "message_time": format_user_time(msg.created_at, request.user)
        # "time": msg.created_at.strftime("%H:%M"),
        # "date": msg.created_at.strftime("%d %b %Y"),
        
    })

@login_required
@require_GET
def poll_messages(request, conv_id):
    last_id = request.GET.get("last_id")

    qs = Messages.objects.filter(conversation_id=conv_id)

    if last_id:
        qs = qs.filter(id__gt=last_id).order_by("id")

    # messages = qs.order_by("id").values(
    #     "id",
    #     "text",
    #     "sender_type",
    #     "message_time"
    # )
    messages = [
    {
        "id": m.id,
        "text": m.text,
        "sender_type": m.sender_type,
        "message_time": format_user_time(m.created_at, request.user)
    }
    for m in qs
    ]

    return JsonResponse({"messages": list(messages)})

@login_required
def poll_conversations(request):
    conversations = (
        Conversation.objects
        .filter(client=request.user)
        .annotate(
            unread=Count(
                "messages",
                filter=Q(messages__is_seen=False, messages__sender_type="admin")
            ),
            last_msg=Subquery(
                Messages.objects
                .filter(conversation=OuterRef("pk"))
                .order_by("-id")
                .values("text")[:1]
            ),
            last_sender_id=Subquery(
                Messages.objects
                .filter(conversation=OuterRef("pk"))
                .order_by("-id")
                .values("sender_id")[:1]
            )
        )
        .values("id", "unread", "last_msg", "last_sender_id", "status")
    )

    return JsonResponse({"conversations": list(conversations)})


#-------------------------- Admin section starts from here -------------------------
def ConversationView(request):
    params = request.POST if request.method == "POST" else request.GET
    selected_conv = params.get("selected_conv", None)
    con_messages = None
    conv = None

    if selected_conv:
        conv = Conversation.objects.get(pk=selected_conv)
        con_messages = (
        Messages.objects
        .filter(conversation_id=conv.id)
        .order_by('created_at')
        ).annotate(
            msgtype = Case(
            When(sender=request.user, then=Value('sent')),
            default=Value('received'),
            output_field=CharField()
        )
        )
        for m in con_messages:
            m.message_time = format_user_time(m.created_at, request.user)

    
    
    
    last_message_qs = Messages.objects.filter(conversation=OuterRef('pk')).order_by('-created_at')
    conversations = Conversation.objects.all().annotate(
        last_msg = Subquery(last_message_qs.values('text')[:1]),
        last_sender_id=Subquery(last_message_qs.values('sender_id')[:1]),
        unread = Count('messages', filter=Q(messages__is_seen=False) & ~Q(messages__sender=request.user))
    )




    context = {
        'conversations':conversations,
        'conv':conv,
        'con_messages':con_messages,
    }
    return render(request, "Assistance/conversations.html", context)



@login_required
def fetch_messages_admin(request, conv_id):
    qs = Messages.objects.filter(conversation_id=conv_id).order_by('created_at')
    messages = [
    {
        "id": m.id,
        "text": m.text,
        "sender": m.sender.username.upper(),
        "sender_type": m.sender_type,
        "message_time": format_user_time(m.created_at, request.user)
    }
    for m in qs
    ]

    return JsonResponse({
        "messages": list(messages)
    })


@login_required
@require_POST
def send_message_admin(request):
    data = json.loads(request.body)

    conv_id = data.get("conversation_id")
    text = data.get("message")

    if not text.strip():
        return JsonResponse({"error": "Empty message"}, status=400)

    conversation = Conversation.objects.get(
        id=conv_id,
    )
    if request.user.groups.filter(name="admin").exists():
        sender_type = "admin"
    else:
        sender_type = "user"

    msg = Messages.objects.create(
        conversation=conversation,
        sender=request.user,
        sender_type=sender_type,
        text=text,
    )

    return JsonResponse({
        "id": msg.id,
        "text": msg.text,
        "sender": msg.sender.username.upper(),
        "sender_type": msg.sender_type,
        "message_time": format_user_time(msg.created_at, request.user)
        # "time": msg.created_at.strftime("%H:%M"),
        # "date": msg.created_at.strftime("%d %b %Y"),
        
    })







def ManageConversation(request):
    context = {

    }
    return render(request, "Assistance/manage_conversations.html", context)