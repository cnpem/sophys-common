#!/usr/bin/env bash

make clean
sphinx-build source build 2> >(tee .build_stderr_output.txt >&2)

export CRITICAL_ERRORS=$(cat .build_stderr_output.txt | grep "CRITICAL")

if [[ -n $CRITICAL_ERRORS ]]; then
  echo "Found critical errors with the build. Failing instead of proceeding."
  exit 1
fi

exit 0
