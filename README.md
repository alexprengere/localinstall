LocalInstall
============

Local installer of Python packages.
This requires *pip*.

Python API
----------
Expose function to install and import locally.

This piece of code is used to install on the fly
a package locally. It can be useful to use third party
modules on environment where you can deploy code but do
have direct ssh access to install stuff. For example to
run streaming jobs in Python on a Hadoop cluster:
```python
from local_install import install
pytz = install('pytz')
NO_PYTZ = pytz is None
```

CLI
---
```bash
python local_install.py pytz
python local_install.py pytz --target toto
```
