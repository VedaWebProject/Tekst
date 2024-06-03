container=${args[--container-name]}
file=${args[--file]}
uri=${args[--mongodb-uri]}

if [[ $container ]]; then
    docker exec -i $container /usr/bin/mongodump --uri $uri --gzip --archive > $file
else
    /usr/bin/mongodump --uri $uri --gzip --archive > $file
fi
