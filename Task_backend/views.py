# Create your views here.

import json
import sys

from django.core import serializers
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader, RequestContext
from django.contrib.auth.decorators import login_required

from Task_backend.models import Task
from Task_backend.task import get_task_tree, change_task_status, \
                              change_task_tree_status, get_oldest_parent
from Tag_backend.tag import find_tags
from Tools.constants import *
from Tools.dates import get_datetime_object

def get_serialized_tasks(request):
    all_tasks = Task.objects.all()
    data = serializers.serialize('json', all_tasks, indent = 4)
    return HttpResponse(data, mimetype='application/json')

#@login_required
def get_tasks(request):
    tasks = []
    folder_dict = {
        'All': -1,
        'Active': IS_ACTIVE,
        'Done': IS_DONE,
        'Dismissed': IS_DISMISSED,
    }
    
    if request.GET.has_key('folder'):
        folder_state = folder_dict[request.GET['folder']]
    else:
        folder_state = IS_ACTIVE
    if request.GET.has_key('due'):
        date_filter = True
        due_date = request.GET['due']
    
    if folder_state == -1:
        task_tree = get_task_tree(request.user, \
                              Task.objects.filter(user = request.user), 0, [])
    else:
        task_tree = get_task_tree(request.user, \
                              Task.objects.filter(user = request.user, \
                                                  status = folder_state), 0,[])
    #template = loader.get_template('task_row.html')
    #context = RequestContext(request, {'task_tree':json.dumps(task_tree)})
    #return HttpResponse(template.render(context))
    return HttpResponse(json.dumps(task_tree, indent = 4), \
                        mimetype='application/json')

@login_required
def show_title(request):
    template = loader.get_template('task_row.html')
    context = RequestContext(request, {'username': request.user.username, \
                                       'name': request.user.first_name})
    return HttpResponse(template.render(context))

def modify_status(request):
    new_status = request.GET['status']
    
    if new_status < 0:
        new_status = 0
    elif new_status > 2:
        new_status = 2
    
    print >>sys.stderr, "In view, new_status = " + str(new_status)
    task_id = request.GET['task_id']
    folder = request.GET['folder']
    
    task = change_task_status(request.user, task_id, new_status)
    change_task_tree_status(task, new_status)
    task_tree = get_task_tree(request.user, get_oldest_parent(task), 0, [])
    return HttpResponseRedirect('/tasks/get/?folder=' + folder)
    #return HttpResponse(json.dumps(task_tree, indent = 4), \
                        #mimetype='application/json')

def modify_date(request):
    task_id = request.GET['task_id']
    folder = request.GET['folder']
    
    if request.GET.has_key('start_date'):
        new_date_object = get_datetime_object(request.GET['start_date'])
        task = change_task_date(request.user, task_id, \
                                new_date_object, IS_START_DATE)
    elif request.GET.has_key('due_date'):
        new_date_object = get_datetime_object(request.GET['due_date'])
        task = change_task_date(request.user, task_id, \
                                new_date_object, IS_DUE_DATE)
        if new_date_object != None:
            change_task_tree_due_date(task, new_date_object)
    return HttpResponseRedirect('/tasks/get/?folder=' + folder)

def delete_task(request):
    task_id = request.GET['task_id']
    folder = request.GET['folder']
    
    
    return HttpResponseRedirect('/tasks/get/?folder=' + folder)
