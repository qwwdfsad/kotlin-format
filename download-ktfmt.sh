#!/usr/bin/env bash
# Download the ktfmt formatter jar into vendor/ (not committed to the repo).
# Pinned to a released version whose output the corpus was generated against.
set -euo pipefail
dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

VERSION="0.63"
SHA256="a015521ddb1c7a80c41edb56b91b4a231439592ffd2e85ac866ff8134c37c112"
URL="https://repo1.maven.org/maven2/com/facebook/ktfmt/${VERSION}/ktfmt-${VERSION}-with-dependencies.jar"
OUT="$dir/vendor/ktfmt.jar"

mkdir -p "$dir/vendor"
if [ -f "$OUT" ] && shasum -a 256 "$OUT" | grep -q "$SHA256"; then
  echo "ktfmt $VERSION already present at vendor/ktfmt.jar"
  exit 0
fi

echo "Downloading ktfmt $VERSION ..."
curl -fSL -o "$OUT" "$URL"

actual="$(shasum -a 256 "$OUT" | cut -d' ' -f1)"
if [ "$actual" != "$SHA256" ]; then
  echo "error: checksum mismatch (got $actual, expected $SHA256)" >&2
  rm -f "$OUT"
  exit 1
fi
echo "Saved vendor/ktfmt.jar (ktfmt $VERSION, sha256 ok)"
