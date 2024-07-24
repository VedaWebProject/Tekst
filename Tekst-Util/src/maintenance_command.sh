container=${args[--container-name]}
dev=${args[--dev]}

# if in dev mode, run python using poetry's virtual env
[[ $dev ]] && run_python="poetry run python" || run_python="python"

if [[ $container ]]; then
    docker exec -e TEKST_DEV_MODE=$dev -i $container $run_python -m tekst maintenance
else
    cd_to_script_parent_dir
    cd ../Tekst-API
    TEKST_DEV_MODE=$dev $run_python -m tekst maintenance
fi
