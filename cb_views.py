from django.shortcuts import render
from django.http import Http404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Todo
from django.db.models import Q

# Todo ListView
class TodoListView(LoginRequiredMixin, ListView):
    model = Todo
    template_name = 'todo/todo_list.html'
    context_object_name = 'todos'
    paginate_by = 10  # 페이지네이션
    ordering = ['-created_at']  # 최신순으로 정렬

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_superuser:
            # 관리자는 모든 Todo List를 볼 수 있음
            return queryset
        else:
            # 일반 유저는 자신이 작성한 Todo만 볼 수 있음
            return queryset.filter(user=self.request.user)

        # 검색기능을 추가할 수 있음 (쿼리파라미터로 검색)
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) | Q(description__icontains=search_query)
            )
        return queryset


# Todo DetailView
class TodoDetailView(LoginRequiredMixin, DetailView):
    model = Todo
    template_name = 'todo/todo_detail.html'
    context_object_name = 'todo'

    def get_object(self):
        todo = super().get_object()
        if not (self.request.user == todo.user or self.request.user.is_superuser):
            raise Http404('You do not have permission to view this todo.')
        return todo

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['todo_dict'] = self.object.__dict__  # Todo 오브젝트의 dict 반환
        return context


# Todo CreateView
class TodoCreateView(LoginRequiredMixin, CreateView):
    model = Todo
    template_name = 'todo/todo_form.html'
    fields = ['title', 'description', 'due_date']  # 필드 설정

    def form_valid(self, form):
        form.instance.user = self.request.user  # 로그인한 유저 정보 저장
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('todo:todo_detail', kwargs={'pk': self.object.pk})  # 상세 페이지로 리다이렉트


# Todo UpdateView
class TodoUpdateView(LoginRequiredMixin, UpdateView):
    model = Todo
    template_name = 'todo/todo_form.html'
    fields = ['title', 'description', 'due_date']  # 필드 설정

    def get_object(self):
        todo = super().get_object()
        if not (self.request.user == todo.user or self.request.user.is_superuser):
            raise Http404('You do not have permission to edit this todo.')
        return todo

    def get_success_url(self):
        return reverse_lazy('todo:todo_detail', kwargs={'pk': self.object.pk})  # 상세 페이지로 리다이렉트


# Todo DeleteView
class TodoDeleteView(LoginRequiredMixin, DeleteView):
    model = Todo
    template_name = 'todo/todo_confirm_delete.html'

    def get_object(self):
        todo = super().get_object()
        if not (self.request.user == todo.user or self.request.user.is_superuser):
            raise Http404('You do not have permission to delete this todo.')
        return todo

    def get_success_url(self):
        return reverse_lazy('todo:todo_list')  # Todo 목록 페이지로 리다이렉트

