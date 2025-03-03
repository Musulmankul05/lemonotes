from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import ListView
from django.views.generic.base import TemplateView
from django.views.generic.edit import UpdateView, CreateView
from django.http import Http404, JsonResponse

from notes.forms import NoteForm, NoteEditForm, NotePasswordForm, NotePasswordCheckForm
from notes.models import Note
import json


@csrf_exempt
def update_session(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        state = data.get('state')
        if state == 'hidden':
            request.session['access_granted'] = False
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'fail'}, status=400)


class NotesView(ListView):
    template_name = "index.html"
    context_object_name = "notes"
    model = Note

    def get_queryset(self):
        queryset = Note.objects.filter(user=self.request.user)
        return queryset.order_by('-pinned', '-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class NotePageView(TemplateView):
    template_name = "note.html"

    def dispatch(self, request, *args, **kwargs):
        slug = kwargs.get('slug')

        # Получаем заметку
        try:
            self.note = Note.objects.get(slug=slug)
        except Note.DoesNotExist:
            raise Http404("Note does not exist")

        if self.note.private and not request.session.get('access_granted'):
            return redirect("notes:note_password", slug=slug)

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['note'] = self.note
        return context


@login_required
def delete_note(request, slug):
    note = Note.objects.get(slug=slug)
    if not note.user == request.user:
        raise Http404("Invalid page")
    print(slug)
    note = Note.objects.get(user=request.user, slug=slug)
    note.delete()
    return redirect('index')


class NoteCreateView(CreateView):
    template_name = 'note_create.html'
    model = Note
    form_class = NoteForm
    success_url = 'index'

    def get_form_kwargs(self):
        kwargs = super(NoteCreateView, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        previous_url = self.request.META.get('HTTP_REFERER', '/')
        context['previous_url'] = previous_url
        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form()

        if form.is_valid():
            print("Form is valid.")
            note = form.save()
            if note:
                return redirect(self.success_url)
        else:
            print("Form is not valid.")
            print(form.errors)


class NotePasswordView(TemplateView):
    template_name = 'note_password.html'

    def dispatch(self, request, *args, **kwargs):
        slug = kwargs.get('slug')

        # Получаем заметку
        try:
            note = Note.objects.get(slug=slug)
        except Note.DoesNotExist:
            raise Http404("Note does not exist")

        # Если пользователь пытается получить доступ к другой заметке, очищаем сессию
        if note.user != request.user:
            raise Http404("Invalid page")

        # Если заметка не приватная, сразу перенаправляем на неё
        if not note.private:
            return redirect('notes:notes', slug=note.slug)

        # Обработка формы
        if request.method == 'POST':
            form = NotePasswordCheckForm(request.POST)
            if form.is_valid():
                password = form.cleaned_data['password']
                if note.password == password:
                    request.session['access_granted'] = True
                    return redirect('notes:notes', slug=note.slug)
                else:
                    form.add_error('password', 'Неверный пароль')
        else:
            form = NotePasswordCheckForm()

        return render(request, self.template_name, {'form': form, 'note': note})


class NoteEditView(UpdateView):
    template_name = "note_edit.html"
    model = Note
    form_class = NoteEditForm

    def dispatch(self, request, *args, **kwargs):
        note = kwargs.get('slug')
        try:
            note = Note.objects.get(slug=note)
        except Note.DoesNotExist:
            raise Http404("Note does not exist")

        if note.user != request.user:
            raise Http404("Note does not exist")

        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def get_initial(self):
        initial = super(NoteEditView, self).get_initial()
        note = self.get_object()

        initial['title'] = Note.decrypt_text_static(note.title)
        initial['content'] = Note.decrypt_text_static(note.content)
        return initial

    def get_success_url(self):
        note_uuid = self.kwargs['slug']
        return '/note/' + str(note_uuid)

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        previous_url = self.request.META.get('HTTP_REFERER', '/')
        context['previous_url'] = previous_url
        context['note'] = Note.objects.get(slug=self.kwargs['slug'])
        return context


def lock_note(request):
    note_id = None
    if request.method == 'POST':
        data = json.loads(request.body)
        uuid = data.get('post_id')
        is_private = data.get('is_private')

        post = get_object_or_404(Note, uuid=uuid)
        post.private = is_private
        post.save()
        return redirect('notes:notes', note_id=note_id)
    return redirect('/note/' + str(note_id))


def note_password_change(request):
    if request.method == 'POST':
        form = NotePasswordForm(request.POST)
        if form.is_valid():
            for i in Note.objects.filter(user=request.user):
                i.set_password(form.cleaned_data['password2'])
        else:
            print(form.errors)
    else:
        form = NotePasswordForm()
    return render(request, 'note_password_change.html', {'form': form})


@require_POST
def pin_note(request, slug):
    note = get_object_or_404(Note, slug=slug)
    note.pinned = not note.pinned
    note.save()
    return JsonResponse({'pinned': note.pinned})
