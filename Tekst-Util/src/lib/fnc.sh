cd_to_script_parent_dir() {
    script_parent_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
    cd "$script_parent_dir"
}
