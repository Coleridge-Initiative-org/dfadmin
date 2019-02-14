# import django.dispatch
# from django.db.models.signals import pre_save, post_save
# from data_facility_admin.models import Project, ProjectMember, ProjectRole, User, ProjectTool
#
# project_activated = django.dispatch.Signal(providing_args=["project"])
#
# @receiver(post_save, sender=Project)
# def project_saved(sender, **kwargs):
#     logger.debug('called project_saved - from "{0}" with params: {1}'.format(sender, kwargs))
#     if kwargs['created']
