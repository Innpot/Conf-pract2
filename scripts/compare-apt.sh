#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
work=$(mktemp -d)
trap 'rm -r -- "$work"' EXIT
trap 'exit 1' HUP INT TERM

# Keep APT configuration and state separate from the host.
mkdir "$work/lists" "$work/archives"
: > "$work/status"
cat > "$work/sources.list" <<'EOF'
deb [arch=amd64 signed-by=/usr/share/keyrings/ubuntu-archive-keyring.gpg] https://archive.ubuntu.com/ubuntu noble main
EOF
cat > "$work/apt.conf" <<EOF
Dir::Etc::main "/dev/null";
Dir::Etc::parts "-";
Dir::Etc::sourcelist "$work/sources.list";
Dir::Etc::sourceparts "-";
Dir::State::status "$work/status";
Dir::State::lists "$work/lists";
Dir::Cache::archives "$work/archives";
Dir::Cache::pkgcache "";
Dir::Cache::srcpkgcache "";
APT::Architecture "amd64";
Acquire::Languages "none";
EOF
export APT_CONFIG="$work/apt.conf"
export LC_ALL=C
apt-get update

if [ "$#" -eq 0 ]; then
    set -- hello
fi
for package in "$@"; do
    sed "s/^package = .*/package = $package/" examples/ubuntu.ini \
        > "$work/compare.ini"
    printf '\n=== %s: DFS postorder ===\n' "$package"
    ./run.sh --config "$work/compare.ini" --order
    printf '\n=== apt-get: simulated install order (Inst lines) ===\n'
    apt-get -s --no-install-recommends install "$package"
    printf '\n=== PlantUML ===\n'
    ./run.sh --config "$work/compare.ini" --plantuml-only
    printf '\n=== apt-cache: Graphviz DOT ===\n'
    apt-cache dotty "$package"
done
