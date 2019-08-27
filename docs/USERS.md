# Managing Users
## Required Information

### Users
Required Fields:
* First Name
* Last Name
* Email (unique)
* Status

#### User Status
  * **Pending Approval:** Accounts on this status will not be created on the system. 
  * **New:** DFAdmin to create an account on ADRF. DFAdmin will change the status to active after account creation. 
  * **Active:** Users that can access the system. 
    * Do not select this status when changing the user. The system automatically change the user to this status.
  * **Locked:** The user account is locked and will not be able to authenticate. To unlock the user, set the status to unlocked.
  * **Locked by too many failed attempts:** This is an automatic status and the admin should not use it. After the defined time, the user will return automatically to active. 
  * **Locked by inactivity:** This is an automatic status, the admin should not use this status. To unlock the user, set the status to unlocked.
  * **Unlocked:** Admins should use this status to return a user to active. This can be used (1) before the automatic time, when they're locked by too many failed attempts; or (2) when the user is locked by inactivity.
  * **Disabled:** This status should be used instead of removing a user. 


## Tasks

### Creating an account

To create a user, follow the 

### Bulk Creation of user accounts
Users can be created in bulk for classes or when a new group of users are onboarding the system.

### Removing Users
Users can not be deleted from DFAdmin. When this is necessary, change the user status to `Disabled` instead.
