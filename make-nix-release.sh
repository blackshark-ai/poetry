#!/bin/sh

set -ex

RUNTIMES[0]="${PYTHON38:+-P "3.8:$PYTHON38"}"

test -n "$PYTHON" || PYTHON="python3"

if [ "$OSTYPE" == "linux-gnu" ]; then
  $PYTHON get-poetry.py -y
  POETRY="$PYTHON $HOME/.poetry/bin/poetry"
  RUNTIMES[1]="${PYTHON39:+-P "3.9:$PYTHON39"}"
else
  $PYTHON -m pip install poetry -U --pre
  POETRY="$PYTHON -m poetry"
fi

$POETRY config virtualenvs.in-project true
$POETRY install --no-dev
$POETRY run python sonnet make release ${RUNTIMES[@]}
