# Backups

The following examples leverage the MongoDB utilities `mongodump` and `mongorestore` for creating and restoring a database backup file, respectively.

!!! example "Variables used in example commands"
    - `$container`: The name of the MongoDB Docker container
    - `$uri`: The [MongoDB connection string URI](https://www.mongodb.com/docs/manual/reference/connection-string/) (from inside the container if you're using Docker)
    - `$file`: The file to read/write the backup from/to
    - `$db`: The name of the database you used in your configuration

!!! warning "Important"
    You might have to use elevated privileges (e.g. via `sudo`) for executing the commands listed below!


## Backing up the database

!!! tip
    If you want to include the current date into the name of your backup file, just use `$(date -I)` as part of `$file`, e.g. `... > "my_important_backup_from_$(date -I).backup"`!

If MongoDB runs in a container:

```sh
docker exec -i $container /usr/bin/mongodump --uri $uri --db=$db --gzip --archive > $file
```

If MongoDB runs bare-metal:

```sh
/usr/bin/mongodump --uri $uri --db=$db --gzip --archive > $file
```


## Restoring the database

!!! warning "Important"
    In case your backup was created while using an older version of Tekst than the one you are using currently, you might have to run database migrations to make the "old" data from the backup compatible with the current version of Tekst. Please refer to [Upgrades](./upgrades.md) to learn how to do that!

If MongoDB runs in a container:

```sh
# define in-container filename for backup file
container_file="/tmp/tekst-db.backup"

# copy file to container
docker cp $file $container:$container_file

# restore backup
docker exec -i $container /usr/bin/mongorestore --uri $uri --drop --gzip --archive=$container_file

# delete backup file from container
docker exec -i $container rm -f $container_file
```

If MongoDB runs bare-metal:

```sh
/usr/bin/mongorestore --uri $uri --drop --gzip --archive=$file
```
