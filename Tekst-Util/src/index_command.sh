container=${args[--container-name]}
dev=${args[--dev]}

# if in dev mode, run python using poetry's virtual env
[[ $dev ]] && run_via_poetry="poetry run" || run_via_poetry=""

if [[ $container ]]; then
    docker exec -i $container TEKST_DEV_MODE=$dev $run_via_poetry python -m tekst index
else
    cd Tekst-API
    TEKST_DEV_MODE=$dev $run_via_poetry python -m tekst index
fi
