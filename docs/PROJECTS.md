# Managing Projects

## Creating a Project

To create a project, click the `Add Project` button, which can be found at the Project List, or on the `+` button at the home page.

1. Fill up at least the `project name` and `abstract`
2. Select the `Instructors` groups if any
3. Select the appropriate `status` (see Fields for more details)
4. Select the type of project. 


## Adding Members
Members can be added either on the user page or on the project page. The list of members is shown on the Project Members list.

On the Project Details page:
1. Click on Add another project member
2. Select the project role
3. Select the user (users are ordered by `first name` then `last name`). In case of homonyms, the `usernames` are in parenthesis.
4. Set the `start date` and `end date`. Both will come pre-populated with today as `start date`.

Similarly, on the User Details page, a Project Membership can be created/managed by adding a project on the step 1 above.  

## Removing Members
`Project Membership` records can't be removed from DFAdmin for audit purposes. 
To remove a member from a project simply add/change the `end date` for a value in the past.


## Granting Data Access 
Granting access to data is possible adding a `Dataset Access` to the project from the list on the Project Detail page.

1. Select a dataset (ordered by `Name`)
2. Select a `start date` and `end date`.

For More details on Dataset Access, see the models page.


# Project Fields


### Mandatory Fields: 
- Name
- Abstract


#### Instructors
Instructors is used to add a group (`Data Facility Role`) of users All active instructors are added to to the project with a role equivalent to Member (Writer).


#### Status
The project status can be:
- **Pending Approval:** Represents projects that are not yet approved for usage. These projects are ignored and will not be propagated to LDAP neither will show up on the workspace selection. 
- **Active:** Active projects will have database schemas and project folders created. These projects are the only ones that show up on the ADRF Workspace Selection. 
- **Archived:** Archived projects don't have a database schema neither project folders.


#### Project Types
Represent what is the main purpose of the project and can be `Research`, `Class`, `Capstone` or `Data Transfer`.
- **Research / Class / Capstone:** These are normal projects and will be visible to users on the workspace.
- **Data Transfer:** These projects are used for data preparation and processing. 


#### A note on Workspace Visibility
`Data Transfe` projects don't show up on the workspace list (neither on the API `api/v1/projects?member=daniel`) for normal users. These projects show only to Curators (DFRole `ADRF Curators`).


#### Start and End dates
The project start and end date represent when the project should be active and valid.


#### LDAP and other ADRF apps.
Some of the fields shown on the project page are _read-only_ and their use is only interesting to sys admins, such as `ldap_id` and `ldap_name`. 
`ldap_name` defines the project name on ldao and its folder name and space on other tools such as **GitLab** and **Mattermost**. On the **Postgres** database, the project schema does not have the prefix `project-` but only the remainder.

On the future the prefix `project-` should be removed to improve clarity on ADRF. 


### Other fields
All other fields don't have any implication on ADRF functionality and are informational only. 

**Depracated fields:** Some of them were deprecated and will be removed in later versions, such as `workspace path`, `request id` and `Environment`.

