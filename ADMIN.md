# DFAdmin Admin Guide

## Batch create user accounts

In addition to create using accounts and configuring them on the web interface, admins can also create using a script. It is required to have access to the server ro tun such scripts.

This script requires an input CSV with the following columns: `first_name`, `last_name` and `email`, which is the minimal necessary to create accounts. 

Run `python manage.py runscript create_accounts --script-args="-f accounts -r Students -p ada_18_uchi il_des_kcmo il_doc_kcmo kcmo_lehd -c -e 12/01/2018 -t new_class_2019 --member_projects adrf adrf2 "`

Parameters of the above command are explained below.
* `-f` indicates the file with accounts.
* `-p` indicates which projects should be associated with these users. As this was created for the class accounts mainly, users will have role `Student` on those, which grant `read` access only.
* `-r` indicates which `Data Facility Role` will be associated with the new users.
* `-c` indicates that this is a class account creation. In this case, the `team` column is also required for each new user.
* `-e` indicates the expiration date for new account roles. This will revoke access automatically on the given date. (Access is revoked by the `ldap_export` script) The expiration date should have the format `2019-12-23T00:00:00`.
* `-t` indicates a tag to be associated with these users. This is specially helpful to enable filtering and batch activation.
* `--member_projects` indicates which projects the users should be members of. Every project in this list the user will be a member of, the `project_role` can't be changed for this in contrast with `-p`. 

Other options for this command are:
* `--team_name` to indicate the base name for teams
* `--project_membership` Indicates which project membership should be used. Default is `Student (Read)`