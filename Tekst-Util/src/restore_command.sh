container=${args[--container-name]}
file=${args[--file]}
uri=${args[--mongodb-uri]}
delete=${args[--delete]}

if [[ $container ]]; then
    container_file="/tmp/tekst-db.backup"
    docker cp $file $container:$container_file
    docker exec -i $container /usr/bin/mongorestore --uri $uri --drop --gzip --archive=$container_file
    success=$?
    docker exec -i $container rm -f $container_file
else
    /usr/bin/mongorestore --uri $uri --drop --gzip --archive=$file
    success=$?
fi

if [[ $success -eq 0 ]]; then
    if [[ $delete ]]; then
        rm -f $file
    fi
    echo "Restore successful."
else
    echo "Restore failed."
fi
