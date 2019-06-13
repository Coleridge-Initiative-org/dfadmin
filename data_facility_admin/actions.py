''' Custom actions for DFAdmin admin website. '''
from .models import User
from data_facility_admin.helpers import KeycloakHelper, EmailHelper


def user_unlock(modeladmin, request, queryset):
    ''' Unlock selected users. '''
    queryset.update(status=User.STATUS_UNLOCKED_BY_ADMIN)
user_unlock.short_description = "Unlock selected users"


def user_disable(modeladmin, request, queryset):
    ''' Unlock selected users. '''
    queryset.update(status=User.STATUS_DISABLED)
user_disable.short_description = "Disable selected users (Use instead of Delete)"


def user_activate(modeladmin, request, queryset):
    ''' Unlock selected users. '''
    queryset.filter(status=User.STATUS_PENDING_APPROVAL).update(status=User.STATUS_NEW)
user_activate.short_description = "Activate selected users (Status will be New)"


def user_send_welcome_email(modeladmin, request, queryset):
    ''' Unlock selected users. '''
    users = queryset.all()
    KeycloakHelper().send_welcome_email(users, reset_pwd=True, reset_otp=True)
user_send_welcome_email.short_description = "Re-send the welcome email. (Reset Password + OTP)"


def user_reset_pwd_only(modeladmin, request, queryset):
    ''' Unlock selected users. '''
    users = queryset.all()
    KeycloakHelper().send_welcome_email(users, reset_pwd=True, reset_otp=False)
user_reset_pwd_only.short_description = "Reset User Password (only)"


def user_reset_otp_only(modeladmin, request, queryset):
    ''' Unlock selected users. '''
    users = queryset.all()
    KeycloakHelper().send_welcome_email(users, reset_otp=True, reset_pwd=False)
user_reset_otp_only.short_description = "Reset User OTP (only)"


def user_send_rules_of_behavior(modeladmin, request, queryset):
    ''' Unlock selected users. '''
    users = queryset.all()
    EmailHelper.send_updated_rules_of_behavior_email(users)
user_send_rules_of_behavior.short_description = "Send ADRF Rules of Behavior email"

