from django.shortcuts import render, redirect
from django.utils.timezone import make_aware
from django.utils.dateparse import parse_datetime
from django.http import Http404
from todo.models import Task

def index(request):
    if request.method == 'POST':
        task = Task(
            title=request.POST['title'],
            due_at=make_aware(parse_datetime(request.POST['due_at'])),
            priority=int(request.POST['priority'])
        )
        task.save()
        return redirect('index')  # リダイレクトを追加

    order_by = request.GET.get('order', 'posted_at')
    if order_by == 'due':
        uncompleted_tasks = Task.objects.filter(completed=False).order_by('due_at')
        completed_tasks = Task.objects.filter(completed=True).order_by('due_at')
    elif order_by == 'priority':
        uncompleted_tasks = Task.objects.filter(completed=False).order_by('-priority')
        completed_tasks = Task.objects.filter(completed=True).order_by('-priority')
    else:
        uncompleted_tasks = Task.objects.filter(completed=False).order_by('-posted_at')
        completed_tasks = Task.objects.filter(completed=True).order_by('-posted_at')

    context = {
        'uncompleted_tasks': uncompleted_tasks,
        'completed_tasks': completed_tasks,
    }
    return render(request, 'todo/index.html', context)

def detail(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404("Task does not exist")

    context = {
        'task': task,
    }

    return render(request, 'todo/detail.html', context)

def delete(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404("Task does not exist")
    task.delete()
    return redirect(index)

def update(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404("Task does not exist")
    if request.method == 'POST':
        task.title = request.POST['title']
        task.due_at = make_aware(parse_datetime(request.POST['due_at']))
        task.priority = int(request.POST['priority'])
        task.save()
        return redirect(detail, task_id)

    context = {
        'task': task
    }
    return render(request, "todo/edit.html", context)

def close(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404("Task does not exist")
    task.completed = True
    task.save()
    return redirect(index)
