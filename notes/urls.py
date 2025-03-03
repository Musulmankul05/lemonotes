from django.contrib.auth.decorators import login_required
from django.urls import path
from . import views

app_name = "notes"

urlpatterns = [
    path('note/<slug:slug>/', login_required(views.NotePageView.as_view()), name="notes"),
    path('note/<slug:slug>/password/', login_required(views.NotePasswordView.as_view()), name='note_password'),
    path('note/update-session/', views.update_session, name='update_session'),
    path('new/', login_required(views.NoteCreateView.as_view()), name="new-note"),
    path('note/<slug:slug>/delete/', views.delete_note, name="delete-note"),
    path('lock/', views.lock_note, name='toggle_private'),
    path('note/<slug:slug>/edit/', login_required(views.NoteEditView.as_view()), name="edit-note"),
    path('settings/note-password/', login_required(views.note_password_change), name="note-pass-change"),
]
