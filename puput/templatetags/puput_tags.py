# -*- coding: utf-8 -*-

from django.conf import settings
from django.template import Library, loader

from endless_pagination.templatetags.endless import show_pages, paginate

from ..models import Category, Tag

register = Library()


@register.inclusion_tag('puput/tags/entries_list.html', takes_context=True)
def recent_entries(context, limit=None):
    blog_page = context['blog_page']
    entries = blog_page.get_entries().order_by('-date')
    if limit:
        entries = entries[:limit]
    return {'request': context['request'], 'entries': entries}


@register.inclusion_tag('puput/tags/entries_list.html', takes_context=True)
def popular_entries(context, limit=None):
    blog_page = context['blog_page']
    entries = blog_page.get_entries().order_by('-num_comments', '-date')
    if limit:
        entries = entries[:limit]
    return {'request': context['request'], 'entries': entries}


@register.inclusion_tag('puput/tags/tags_list.html', takes_context=True)
def tags_list(context, limit=None, tags_qs=None):
    blog_page = context['blog_page']
    if tags_qs:
        tags = tags_qs.all()
    else:
        tags = Tag.objects.with_uses(blog_page)
    if limit:
        tags = tags[:limit]
    return {'blog_page': blog_page, 'request': context['request'], 'tags': tags}


@register.inclusion_tag('puput/tags/categories_list.html', takes_context=True)
def categories_list(context, categories_qs=None):
    blog_page = context['blog_page']
    if categories_qs:
        categories = categories_qs.all()
    else:
        categories = Category.objects.with_uses(blog_page).filter(parent=None)
    return {'blog_page': blog_page, 'request': context['request'], 'categories': categories}


@register.inclusion_tag('puput/tags/archives_list.html', takes_context=True)
def archives_list(context):
    blog_page = context['blog_page']
    archives = blog_page.get_entries().datetimes('date', 'day', order='DESC')
    return {'blog_page': blog_page, 'request': context['request'], 'archives': archives}


@register.simple_tag()
def comments():
    """
    Display comments depending which system have been configured in settings.py
    """
    template_name = ""
    if hasattr(settings, 'DISQUS_API_KEY') and hasattr(settings, 'DISQUS_WEBSITE_SHORTNAME'):
        template_name = 'puput/comments/disqus.html'
    if template_name:
        template = loader.get_template(template_name)
        return template.render()
    return ""

# Avoid to import endless_pagination in installed_apps and in the templates
register.tag('show_paginator', show_pages)
register.tag('paginate', paginate)
