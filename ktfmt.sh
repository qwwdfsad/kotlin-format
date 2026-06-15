#!/usr/bin/env bash
# Format Kotlin with ktfmt in Kotlin-language style (4-space indent, 100 columns).
#
#   ./ktfmt.sh path/to/File.kt        # format file(s) in place
#   ./ktfmt.sh -                      # read stdin, write formatted Kotlin to stdout
#   echo 'fun f()=1' | ./ktfmt.sh -
#
# The jar is not committed; fetch it once with ./download-ktfmt.sh. Requires a JDK (11+).
set -euo pipefail
dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
jar="$dir/vendor/ktfmt.jar"
if [ ! -f "$jar" ]; then
  echo "error: vendor/ktfmt.jar not found. Run ./download-ktfmt.sh first." >&2
  exit 1
fi
exec java -jar "$jar" --kotlinlang-style "$@"
