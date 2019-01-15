# RELEASE-PREPARATION

 1. **Check for missing migrations**

    Using docker-compose: `docker-compose exec web manage.py makemigrations --check`
    
    Expected output is  `No changes detected`. Otherwise, create missing migrations and test it.
    


2. **Clean DB changes**

    `make dev-db-clear`

3. **Apply all migrations**

    `make db-migrate`

4. **Create git release TAG**

    Use the pattern: release_v1_2018.10.10

5. PUSH release and tags
    `git push` and `git push --tags`
    