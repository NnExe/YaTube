from django.core.paginator import Paginator
from django.conf import settings


def my_paginator(posts, page_number):
    paginator = Paginator(posts, settings.POSTS_PER_PAGE)
    return paginator.get_page(page_number)
