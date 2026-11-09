#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
work=$(mktemp -d)
trap 'rm -r -- "$work"' EXIT
trap 'exit 1' HUP INT TERM

url=$(sed -n 's/^repository = //p' examples/ubuntu.ini)
curl -fLsS "$url" | xz -dc > "$work/Packages"
test -s "$work/Packages"
: > "$work/status"
mkdir "$work/lists"

apt_index() {
    program=$1
    shift
    LC_ALL=C "$program" \
        -o APT::Architecture=amd64 \
        -o Dir::State::status="$work/status" \
        -o Dir::State::lists="$work/lists" \
        -o Dir::Etc::sourcelist=/dev/null \
        -o Dir::Etc::sourceparts=- \
        -o Dir::Cache::pkgcache= \
        -o Dir::Cache::srcpkgcache= \
        --with-source "$work/Packages" "$@"
}

for package in "${@:-hello}"; do
    sed "s/^package = .*/package = $package/" examples/ubuntu.ini \
        > "$work/compare.ini"
    printf '\n=== %s: DFS postorder ===\n' "$package"
    ./run.sh --config "$work/compare.ini" --order
    printf '\n=== apt-get: simulated install order (Inst lines) ===\n'
    apt_index apt-get -s --no-install-recommends install "$package"
done
