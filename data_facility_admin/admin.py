"""Admin interface configuration"""

from ajax_select.admin import AjaxSelectAdmin
from ajax_select import make_ajax_form
from django.contrib import admin
from rest_framework.authtoken.models import Token
from simple_history.admin import SimpleHistoryAdmin
from .models import *
from .actions import *


admin.site.site_header = 'Data Facility Admin'
admin.site.site_title = 'Data Facility Admin'
admin.site.index_title = 'Data Facility Site Administration'
# admin.site.site_url = 'Data Facility Admin' # TODO: add to change the link on 'VIEW SITE'.


# ------------------------ All inlines should come first. ------------------------
class UserDfRoleInline(admin.TabularInline):
    """Inline Manager for model DfRole"""
    model = UserDfRole
    extra = 0
    min_num = 0
    can_delete = False


class UserTrainingInline(admin.TabularInline):
    """Inline Manager for model UserTraining"""
    model = UserTraining
    extra = 0


class ProjectMembershipInline(admin.TabularInline):
    """Inline Manager for model ProjectMembership"""
    model = ProjectMember
    extra = 0
    min_num = 0
    can_delete = False
    # form = make_ajax_form(ProjectMember, {
    #     'member': 'users',
    #     'project': 'projects',
    # })


class DatasetAccessInline(admin.StackedInline):
    """Inline Manager for model DatasetAccess"""
    model = DatasetAccess
    extra = 0
    can_delete = False


class DataAgreementSignatureInline(admin.TabularInline):
    """Inline Manager for model DataAgreementSignature"""
    model = DataAgreementSignature
    extra = 0


class DatasetAgreementInline(admin.StackedInline):
    """Inline Manager for model DataAgreement"""
    model = DataAgreement
    extra = 0


class SignedTermsOfUseInline(admin.TabularInline):
    """Inline Manager for model SignedTermsOfUse"""
    model = SignedTermsOfUse
    extra = 0


class DataStewardInline(admin.TabularInline):
    """Inline Manager for model DataSteward"""
    model = DataSteward
    can_delete = False
    extra = 0


class ProjectToolInline(admin.TabularInline):
    """Inline Manager for model ProjectTool"""
    model = ProjectTool
    extra = 0
    readonly_fields = ['system_info']
    # prepopulated_fields = {"request_id": ("?",)}


class TermsOfUseInline(admin.TabularInline):
    """Inline Manager for model TermsOfUse"""
    model = TermsOfUse
    extra = 0


class DatasetInline(admin.TabularInline):
    """Inline Manager for model Dataset"""
    model = Dataset
    extra = 0
    can_delete = False


@admin.register(DataProvider)
class DataProviderAdmin(SimpleHistoryAdmin):
    """Admin Manager for model DataProvider"""
    list_display = ('name', 'datasets_count')
    search_fields = ('name',)
    inlines = [DatasetInline]


@admin.register(ProfileTag)
class ProfileTagAdmin(SimpleHistoryAdmin):
    """Admin Manager for model ProfileTag"""
    list_display = ('text', 'description')
    search_fields = ('text', 'description')


@admin.register(DfRole)
class DfRoleAdmin(SimpleHistoryAdmin):
    """Admin Manager for model DfRole"""
    list_display = ('name', 'description', 'ldap_name', 'active_usernames')
    search_fields = ('name', 'description')
    readonly_fields = ['ldap_id', 'ldap_name']
    inlines = [UserDfRoleInline]


@admin.register(DataAgreementSignature)
class DataAgreementSignatureAdmin(SimpleHistoryAdmin):
    """Admin Manager for model DataAgreementSignature"""
    list_display = ('user', 'data_agreement', 'status', 'accepted', 'date')
    search_fields = ('user__first_name', 'user__last_name', 'data_agreement__title', 'status',
                     'accepted', 'date')
    list_filter = ['status', 'accepted', 'date']


@admin.register(DataAgreement)
class DataAgreementAdmin(SimpleHistoryAdmin):
    """Admin Manager for model DataAgreement"""
    list_display = ('dataset', 'title', 'version', 'delete_on_expiration')
    search_fields = ('dataset__dataset_id', 'dataset__name', 'title', 'text', 'version')
    list_filter = ['version', 'delete_on_expiration', 'deletion_method']


@admin.register(DataSteward)
class DataStewardAdmin(SimpleHistoryAdmin):
    """Admin Manager for model DataSteward"""
    list_display = ('dataset', 'user', 'start_date', 'end_date')
    search_fields = ('dataset_title', 'dataset__dataset_id', 'user')
    list_filter = ['start_date', 'end_date']


@admin.register(DatabaseSchema)
class DatabaseSchemaAdmin(SimpleHistoryAdmin):
    """Admin Manager for model DatabaseSchema"""
    list_display = ('name', 'public')
    search_fields = ('name',)
    list_filter = ['public']

from django.contrib import admin
from django.contrib.postgres import fields
from django_json_widget.widgets import JSONEditorWidget

@admin.register(Dataset)
class DatasetAdmin(SimpleHistoryAdmin):
    """Admin Manager for model Dataset"""
    formfield_overrides = {
        fields.JSONField: {'widget': JSONEditorWidget},
    }

    list_display = ('dataset_id', 'name', 'active_stewards', 'data_classification', 'public', 'database_schema')
    search_fields = ('dataset_id', 'name', 'data_classification', 'ldap_name',
                     'ldap_id', 'public', 'database_schema__name')
    list_filter = ['data_classification', 'shareable', 'data_provider', 'public']
    inlines = [DatasetAgreementInline, DataStewardInline, DatasetAccessInline]
    readonly_fields = ['ldap_id', 'ldap_name']


@admin.register(TermsOfUse)
class TermsOfUseAdmin(SimpleHistoryAdmin):
    """Admin Manager for model TermsOfUse"""
    list_display = ('text', 'version', 'release_date')
    search_fields = ('text', 'version', 'release_date')
    list_filter = ['version', 'release_date']


@admin.register(Keyword)
class KeywordAdmin(SimpleHistoryAdmin):
    """Admin Manager for model Terms"""
    list_display = ('name', 'description')
    search_fields = ('name', 'description')
    list_filter = ['dataset']


@admin.register(DataClassification)
class KeywordAdmin(SimpleHistoryAdmin):
    """Admin Manager for model Terms"""
    list_display = ('name', 'description')
    search_fields = ('name', 'description')


@admin.register(Training)
class TrainingAdmin(SimpleHistoryAdmin):
    """Admin Manager for model Training"""
    list_display = ('name', 'description', 'date', 'url')
    search_fields = ('name', 'description', 'date', 'url')
    list_filter = ['date', ]
    preserve_filters = True
    inlines = [UserTrainingInline, ]


@admin.register(User)
class UserAdmin(SimpleHistoryAdmin):
    """Admin Manager for model User"""
    list_display = ('username', 'full_name', 'affiliation', 'signed_terms_at',
                    'ldap_last_auth_time', 'status', 'profile_tags',
                    'ldap_last_pwd_change')
    search_fields = ('first_name', 'last_name', 'email', 'affiliation', 'orc_id',
                     'job_title', 'sponsor', 'ldap_name', 'ldap_id')
    list_filter = ['status', 'signed_terms_at', 'ldap_last_auth_time', 'affiliation',
                   'userdfrole__role', 'ldap_last_pwd_change', 'tags' ]
    readonly_fields = ['ldap_id', 'ldap_lock_time', 'ldap_last_auth_time', 
                       'ldap_last_pwd_change']
    history_list_display = ['status']
    if not settings.ADRF_ENABLE_CUSTOM_USERNAME:
        readonly_fields += ['ldap_name']

    actions = [user_unlock,
               user_disable,
               user_activate,
               user_send_welcome_email,
               user_send_rules_of_behavior]
    preserve_filters = True
    # To facilitate reporting only.
    # list_max_show_all = 600
    # list_per_page = 600
    inlines = [UserDfRoleInline, UserTrainingInline, DataAgreementSignatureInline,
               SignedTermsOfUseInline, DataStewardInline, ProjectMembershipInline]

    def get_actions(self, request):
        # Disable delete
        actions = super(UserAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

    def has_delete_permission(self, request, obj=None):
        # Disable delete
        return False


@admin.register(Project)
class ProjectAdmin(SimpleHistoryAdmin):
    """Admin Manager for model Project"""
    search_fields = ('name', 'ldap_name', 'abstract', 'methodology', 'outcomes',
                     'status', 'environment', 'type', 'ldap_name', 'ldap_id')
    list_display = ('name', 'owner', 'status', 'environment', 'members', 'members_count',
                    'created_at',)
    list_filter = ['environment', 'status', 'has_irb', 'type']
    inlines = [ProjectMembershipInline, DatasetAccessInline, ProjectToolInline]
    readonly_fields = ['ldap_id', 'ldap_name']
    # form = make_ajax_form(Project, {
    #     'owner': 'users',
    #     'parent_project': 'projects',
    # })


@admin.register(ProjectRole)
class ProjectRoleAdmin(SimpleHistoryAdmin):
    """Admin Manager for model ProjectRole"""
    search_fields = ('name', 'system_role', 'description', 'ldap_name', 'ldap_id')
    list_display = ('name', 'system_role', 'description')
    list_filter = ['system_role']


@admin.register(ProjectTool)
class ProjectToolAdmin(SimpleHistoryAdmin):
    """Admin Manager for model ProjectTool"""
    search_fields = ('project', 'tool_name', 'other_name', 'additional_info')
    list_display = ('project', 'name', 'additional_info')
    list_filter = ['tool_name']


@admin.register(ProjectMember)
class ProjectMembershipAdmin(SimpleHistoryAdmin):
    """Admin Manager for model ProjectMembership"""
    # search_fields = ('project__name',)
    # list_display = ('project', 'member', 'dbms_role')
    # list_filter = ['dbms_role']

    def get_model_perms(self, request):
        """
        Return empty perms dict thus hiding the model from admin index.
        """
        return {}

    def get_actions(self, request):
        # Disable delete
        actions = super(ProjectMembershipAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

    def has_delete_permission(self, request, obj=None):
        # Disable delete
        return False


@admin.register(DatasetAccess)
class DatasetAccessAdmin(SimpleHistoryAdmin):
    """Admin Manager for model DatasetAccess"""
    search_fields = ('project__name', 'request_id', 'dataset__name', 'dataset__dataset_id')
    list_display = ('project', 'dataset_id', 'request_id', 'created_at', 'updated_at')
    list_filter = ['dataset_id', 'project', 'requested_at', 'granted_at',
                   'expire_at', 'load_to_database']

    def get_actions(self, request):
        # Disable delete
        actions = super(DatasetAccessAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

    def has_delete_permission(self, request, obj=None):
        # Disable delete
        return False
