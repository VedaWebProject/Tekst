load_common_args

if [[ $container ]]; then
    docker exec -i $container /usr/bin/mongodump --uri $uri --gzip --archive > $file
else
    /usr/bin/mongodump --uri $uri --gzip --archive > $file
fi
