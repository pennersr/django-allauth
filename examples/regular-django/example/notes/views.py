from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from example.decorators import app_permission

from .models import Note


@app_permission("notes")
def note_list(request):
    if request.method == "POST":
        title = request.POST.get("title")
        body = request.POST.get("body", "")
        if title:
            Note.objects.create(title=title, body=body)
        return redirect("notes_list")

    notes = Note.objects.order_by("-created_at")
    context = {
        "notes": notes,
    }
    return render(request, "notes/note_list.html", context)


@app_permission("notes")
@require_http_methods(["POST"])
def note_delete(request, pk):
    note = get_object_or_404(Note, pk=pk)
    note.delete()
    return redirect("notes_list")
