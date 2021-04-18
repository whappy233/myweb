# django 便捷函数 django.shortcuts

## render()
> render(request, template_name, context=None,content_type=None, status=None, using=None)

- context: 要添加到模板上下文的值的字典default:{}
- content_type: 用于结果文档的 MIME 类型。默认'text/html' 。
- status: 响应的状态码默认为 200。
- using: 用于加载模板的模板引擎的 NAME

#### 例如
下面的示例使用 MIME 类型呈现模板 myapp/index.html application/xhtml+xml ：

```python
from django.shortcuts import render
def my_view(request):
    # View code here...
    return render(request, 'myapp/index.html', {
        'foo': 'bar',
    }, content_type='application/xhtml+xml')
```
此示例相当于：

```python
from django.http import HttpResponse
from django.template import loader
def my_view(request):
    # View code here...
    t = loader.get_template('myapp/index.html')
    c = {'foo': 'bar'}
    return HttpResponse(t.render(c, request), content_type='application/xhtml+xml')
```

## redirect()
> redirect(to, *args, permanent=False, **kwargs)

参数可以是:
- 一个模型：模型的 get_absolute_url() 函数将被调用。
- 视图名，可能带有的参数：reverse() 将被用于反向解析名称。
- 一个绝对或相对 URL，将按原样用作重定向位置。

默认情况下，redirect() 返回临时重定向。所有以上形式都接受 permanent 参数；如果设置为 True 会返回一个永久重定向
```python
return redirect(obj, permanent=True)
```
你可以通过多种方法使用 redirect() 函数。

- 传递对象，对象的 get_absolute_url() 方法将被调用来指向重定向地址：
    ```python
    def my_view(request):
        ...
        obj = MyModel.objects.get(...)
        return redirect(obj)
    ```

- 传递视图名和一些可选的位置或关键字参数；URL 将使用 reverse() 方法来反向解析：
    ```python
    def my_view(request):
        ...
        return redirect('这里传递视图名', foo='bar')
    ```

- 传递硬编码 URL 来重定向：
    ```python
    def my_view(request):
        ...
        return redirect('/some/url/')
    ```

- 这也适用于完整的 URL ：
    ```python
    def my_view(request):
        ...
        return redirect('https://example.com/')
    ```


## get_object_or_404()
> get_object_or_404(klass, *args, **kwargs)

> 在给定的模型管理器( model manager) 上调用 get() ，但它会引发 Http404 而不是模型的 DoesNotExist 异常。

> 如果查询结果有多个对象，那么会引发 MultipleObjectsReturned 异常

示例:
```python
# model
get_object_or_404(MyModel, pk=1)

# queryset
queryset = Book.objects.filter(title__startswith='M')
get_object_or_404(queryset, pk=1)

# model 同上功能
get_object_or_404(Book, title__startswith='M', pk=1)

# 使用自定义的模型管理器
get_object_or_404(Book.dahl_objects, title='Matilda')

# 你也可以使用关联管理器( related managers )
author = Author.objects.get(name='Roald Dahl')
get_object_or_404(author.book_set, title='Matilda')
```

## get_list_or_404()
> get_list_or_404(klass, *args, **kwargs)

> klass: 从中获取列表的 Model ，Manager 或 QuerySet 实例

> 返回给定模型管理器上 filter() 转换为列表的结果，如果结果列表为空，则引发 Http404

下面的例子展示从 MyModel 中获取所有 published=True 的对象：

```python
from django.shortcuts import get_list_or_404
def my_view(request):
    my_objects = get_list_or_404(MyModel, published=True)
```
此示例相当于：

```python
from django.http import Http404
def my_view(request):
    my_objects = list(MyModel.objects.filter(published=True))
    if not my_objects:
        raise Http404("No MyModel matches the given query.")
```