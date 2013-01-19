#!/usr/bin/env bash

if [[ -z `which punt` ]]; then
  echo "you need to install punt"
  echo "   > pip install punt"
else
  punt -w test -w plywood 'py.test -q -x'
fi
