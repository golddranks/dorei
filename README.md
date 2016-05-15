# doRei
日本語学習者の為の例文検索サービス

Copyright Pyry Kontio. No any particular license at the moment.

## How to deploy:

Install a Python 3 virtual environment:
```
virtualenv -p python3 dorei_env
cd dorei_env
source bin/activate
```

Download the package:
```
git clone git@github.com:golddranks/dorei.git
```

Install the package in the environment.
```
python dorei/setup.py install
```

Most likely, a package called `prefixtree` is going to fight back, because it's essentially unmaintained. You can download it and install it manually. Remove the two top lines (`from distribute_setup import use_setuptools` and `use_setuptools()`) from it's setup.py and it should give in.

Try again until you have dorei and it's dependencies installed.

Launch dorei.
```
cd dorei
pserve development.ini
```
