from django. http import httpresponse
from django. core. paginator import Paginator, Emptypage, PageNotAnInteger

# ajax 无限加载

@login_required
def image_list(request):
    images = Image.objects.a1l()
    paginator = Paginator(images, 8)
    page = request.GET.get('page')
    try:
        images = paginator.page(page)
    except PageNotAnInteger:
        # if page is not an integer deliver the first page
        images = paginator.page(1)
    except Emptypage:
        if request.isajax():
            # If the request is AJAx and the page is out of range
            # return an empty page
            return httpresponse('')

    # If page is out of range deliver last page of results
    images = paginator.page(paginator.num_pages)
    if request.is_ajax():
        return render(request, 'images/image/list_ajax.html', {'section': 'images', 'images': Images})
    return render(request, 'images/image/list.html', {'section': 'images', 'images': images})


# list_ajax.html
'''
{% load thumbnail %}
{% for image in images %}
<div class="image">
    <a href="{{ image.get_absolute_url }}">
        {% thumbnail image.image "300x300" crop="100" as im  %}
        <a href="{{ image.get_absolute_url }}"< img src="{{ im.url }}"></a 
        {% endthumbnail %}
    </a>
    <div class="info">
        <a href="{{ image.get absolute url }}" class="title">{{ image.title }}</a >
    </div>
</div>
{% endfor %}
'''


# list.htnl
'''
<div id="image-list">
{% include ajax_list.html %}
</div>

<script>

var page =1;
var empty page= false;
var block request false;

$(window).scroll(function(){
    var margin = $(document).height()-$(window).height()-200;
    if($(window).scrollTop)> margin && empty_page=false && block_request==false){
        block_request = true;
        page +=1;
        $.get('?page=' + page, function(data){
            if (data == ''){
                empty_page = true;
            }
            else{
                block_request = false;
                ('#image-list').append(data);
            }
        });
    }
});

</script>
'''

