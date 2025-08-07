#!/bin/bash

pytest --cov=app --cov-report=html

report_path="$(pwd)/htmlcov/index.html"

if [ -f "$report_path" ]; then
  echo "Coverage report generated at:"
  echo "$report_path"
else
  echo "Coverage report not found. Please check if pytest ran successfully."
fi
