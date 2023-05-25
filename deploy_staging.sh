!#/bin/bash
python3 setup_staging.py sdist bdist_wheel
python3 -m twine upload dist/* --skip-existing
