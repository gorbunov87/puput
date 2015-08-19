import operator

from disqusapi import DisqusAPI, APIError

from django.conf import settings
from django.http import Http404, HttpResponse
from django.views.generic import View

from wagtail.wagtailcore import hooks

from .models import EntryPage


class EntryPageServe(View):

    def get(self, request, *args, **kwargs):
        if not request.site:
            raise Http404
        path_components = list(operator.itemgetter(0, -1)(request.path.strip('/').split('/')))
        page, args, kwargs = request.site.root_page.specific.route(request, path_components)

        for fn in hooks.get_hooks('before_serve_page'):
            result = fn(page, request, args, kwargs)
            if isinstance(result, HttpResponse):
                return result
        return page.serve(request, *args, **kwargs)


class EntryPageUpdateCommentsView(View):

    def post(self, request, entry_page_id, *args, **kwargs):
        try:
            entry_page = EntryPage.objects.get(pk=entry_page_id)
            disqus_client = DisqusAPI(secret_key=settings.DISQUS_API_KEY)
            try:
                thread = disqus_client.threads.details(forum=settings.DISQUS_WEBSITE_SHORTNAME,
                                                       thread='ident:{}'.format(entry_page_id))
                entry_page.num_comments = thread['posts']
                entry_page.save()
                return HttpResponse('')
            except APIError:
                raise Http404
        except EntryPage.DoesNotExist:
            raise Http404
