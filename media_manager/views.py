import os
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from authentication.decorators import allowed_users
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db.models import Q
from .models import MediaFile
from .forms import MediaFileForm
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.clickjacking import xframe_options_exempt
from django.http import HttpResponseForbidden, JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.http import Http404
from django.utils.text import slugify
from django.views.decorators.http import require_GET
# add upload button anywhere with below tags
# <input type="text" id="brochure_url" name="brochure" placeholder="Select a file" readonly>
# <button class="button" type="button" data-media-picker data-target="#brochure_url">Pick File</button>

def superuser_required(view_func):
    return user_passes_test(lambda u: u.is_active and u.is_superuser)(view_func)

@superuser_required
@xframe_options_exempt
@require_GET
def media_library(request):
    query = request.GET.get('q', '')
    page_num = request.GET.get('page', 1)

    files = MediaFile.objects.all()
    if query:
        files = files.filter(Q(title__icontains=query) | Q(file__icontains=query))

    paginator = Paginator(files, 12)
    page_obj = paginator.get_page(page_num)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # Return JSON data for AJAX calls
        data = []
        for f in page_obj:
            data.append({
                'id': f.id,
                'title': f.title,
                'url': f.get_url(),
                'uploaded_at': f.uploaded_at.strftime('%Y-%m-%d %H:%M'),
            })
        return JsonResponse({
            'files': data,
            'page': page_obj.number,
            'num_pages': paginator.num_pages,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
        })

    # For normal page load, render HTML template
    return render(request, 'media_manager/media_library.html', {
        'files': page_obj,
        'query': query,
    })


@superuser_required
@xframe_options_exempt
def upload_media(request):
    if request.method == 'POST':
        form = MediaFileForm(request.POST, request.FILES)
        if form.is_valid():
            media = form.save()
            # If request is AJAX or iframe picker we can return JSON with the new URL
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('ajax'):
                return JsonResponse({'id': media.id, 'url': media.get_url(), 'title': media.title})
            return redirect('media_manager:media_library')
    else:
        form = MediaFileForm()
    return render(request, 'media_manager/upload_media.html', {'form': form})


@superuser_required
@require_POST
def delete_media(request, media_id):
    try:
        media = MediaFile.objects.get(pk=media_id)
        media.file.delete(save=False)  # delete file from storage
        media.delete()  # delete db entry
        return JsonResponse({'success': True})
    except MediaFile.DoesNotExist:
        raise Http404("File not found")


@superuser_required
@require_POST
def rename_media(request, media_id):
    new_title = request.POST.get('title', '').strip()
    if not new_title:
        return JsonResponse({'success': False, 'error': 'Title required'}, status=400)

    try:
        media = MediaFile.objects.get(pk=media_id)
        media.title = new_title
        media.save()
        return JsonResponse({'success': True, 'title': new_title})
    except MediaFile.DoesNotExist:
        raise Http404("File not found")


def media_list_api(request):
    """Simple JSON API for listing media (used if you want to build a JS picker)."""
    q = request.GET.get('q', '')
    files = MediaFile.objects.all()
    if q:
        files = files.filter(Q(title__icontains=q) | Q(file__icontains=q))
    data = [{'id': f.id, 'title': f.title or f.file.name, 'url': f.get_url()} for f in files[:200]]
    return JsonResponse({'results': data})