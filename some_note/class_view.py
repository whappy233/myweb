


# views.py --------------------------------------
from django.views.generic.edit import CreateView

class RestaurantCreate(CreateView):
    model = Restaurant
    template_name = 'myrestaurants/form.html'
    form_class = RestaurantForm

    # Associate form.instance.user with self.request.user
    # form_valid方法作用是添加前端表单字段以外的信息。
    # 在用户在创建餐厅时，我们不希望用户能更改创建用户，于是在前端表单里把user故意除外了(见forms.py)，而选择在后台添加user信息
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(RestaurantCreate, self).form_valid(form)


# forms.py -------------------------------------
from django.forms import ModelForm,  TextInput, URLInput, ClearableFileInput
from .models import Restaurant, Dish

class RestaurantForm(ModelForm):
    class Meta:
        model = Restaurant
        exclude = ('user', 'date',)

        widgets = {
            'name': TextInput(attrs={'class': 'form-control'}),
            'address': TextInput(attrs={'class': 'form-control'}),
            'telephone': TextInput(attrs={'class': 'form-control'}),
            'url': URLInput(attrs={'class': 'form-control'}),
        }

        labels = {
            'name': '名称',
            'address': '地址',
            'telephone': '电话',
            'url': '网站',
        }


# template
'''
{% extends "myrestaurants/base.html" %}

{% block content %}

<form action="" method="POST" enctype="multipart/form-data" >
  {% csrf_token %}

  {% for hidden_field in form.hidden_fields %}
  {{ hidden_field }}
{% endfor %}

{% if form.non_field_errors %}
  <div class="alert alert-danger" role="alert">
    {% for error in form.non_field_errors %}
      {{ error }}
    {% endfor %}
  </div>
{% endif %}

{% for field in form.visible_fields %}
  <div class="form-group">
    {{ field.label_tag }}
    {{ field }}
    {% if field.help_text %}
      <small class="form-text text-muted">{{ field.help_text }}</small>
    {% endif %}
  </div>
{% endfor %}
  <input type="submit" value="提交"/>
</form>

{% endblock %}

'''