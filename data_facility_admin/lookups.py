from ajax_select import register, LookupChannel
from .models import User, Project, ProjectRole
from django.db.models import Q


class FixedLookupChannel(LookupChannel):
    ''' Fix for django-ajax-select to work with Django 1.11 for type cast of pk on
    https://github.com/crucialfelix/django-ajax-selects/blob/d222500cf1562c62334553f1abd800837a6d82bd/ajax_select/lookup_channel.py#L98
    '''
    def get_objects(self, ids):
        if getattr(self.model._meta.pk, "remote_field", False):
            pk_type = self.model._meta.pk.remote_field.field.target_field.to_python
        ids = [pk_type(i) for i in ids]
        return super(FixedLookupChannel, self).get_objects(ids)


@register('users')
class UsersLookup(FixedLookupChannel):

    model = User

    def get_query(self, q, request):
        return self.model.objects.filter(Q(first_name__icontains=q) | Q(last_name__icontains=q) | Q(email__icontains=q))

    def format_item_display(self, item):
        return u"<span class='tag'>%s</span>" % str(item)

    # def can_add(self, user, model):
    #     return permissions.has_perm('can_add', model, user)


@register('projects')
class ProjectsLookup(FixedLookupChannel):

    model = Project

    def get_query(self, q, request):
        return self.model.objects.filter(Q(name__icontains=q) | Q(methodology__icontains=q) | Q(abstract__icontains=q)
                                         | Q(owner__first_name__icontains=q) | Q(owner__last_name__icontains=q)
                                         )

    def format_item_display(self, item):
        return u"<span class='tag'>%s</span>" % str(item)


@register('project_roles')
class ProjectRolesLookup(FixedLookupChannel):

    model = ProjectRole

    def get_query(self, q, request):
        return self.model.objects.filter(Q(name__icontains=q))

    def format_item_display(self, item):
        return u"<span class='tag'>%s</span>" % str(item)
