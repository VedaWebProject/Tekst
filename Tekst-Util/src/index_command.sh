container=${args[--container-name]}
dev=${args[--dev]}

if [[ $container ]]; then
    docker exec -i $container TEKST_DEV_MODE=$dev python -m tekst index
else
    cd Tekst-API
    TEKST_DEV_MODE=$dev python -m tekst index
fi
