from django.core.paginator import Paginator

NUMBER_OF_POSTS: int = 10  # Количество отображаемых статей


def paginator(posts, request):
    paginator = Paginator(posts, NUMBER_OF_POSTS)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
