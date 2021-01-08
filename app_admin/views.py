import django
from django.shortcuts import render
from django.contrib.auth.models import User
from django.http.response import HttpResponse, JsonResponse


def admin_user(request):
    if request.method == 'GET':
        # user_list = User.objects.all()
        return render(request, 'app_admin/admin_user.html', locals())
    elif request.method == 'POST':
        username = request.POST.get('username','')
        if username == '':
            user_data = User.objects.all().values_list(
                'id','last_login','is_superuser','username','email','date_joined','is_active','first_name'
            )
        else:
            user_data = User.objects.filter(username__icontains=username).values_list(
                'id','last_login','is_superuser','username','email','date_joined','is_active','first_name'
            )
        table_data = []
        for i in list(user_data):
            item = {
                'id':i[0],
                'last_login':i[1],
                'is_superuser':i[2],
                'username':i[3],
                'email':i[4],
                'date_joined':i[5],
                'is_active':i[6],
                'first_name':i[7]
            }
            table_data.append(item)
        return JsonResponse({'status':True,'data':table_data})
    else:
        return JsonResponse({'status':False,'data':'方法错误'})
