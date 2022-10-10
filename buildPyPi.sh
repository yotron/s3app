#!/bin/sh
deacivate
rm -rf build
rm -rf dist
python3 -m build
twine upload -r pypi dist/*