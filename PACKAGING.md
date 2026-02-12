Packaging guide
================

Local macOS build
------------------

1. Ensure Python 3 is installed.
2. From project root run:

```bash
./scripts/build_local_mac.sh
```

This produces a single-file executable in `dist/`.

Cross-build (Windows) and CI
----------------------------

Building a Windows executable from macOS locally is unreliable. Use the supplied GitHub Actions workflow to produce both macOS and Windows executables.

Trigger the workflow by pushing a tag like `v1.0.0` or from the Actions UI (`Build executables`). Artifacts are attached from the `dist/` folder.

Notes about bundled assets
-------------------------

- The build uses PyInstaller's `--add-data` to include the `assets/` and `data/` folders in the onefile bundle.
- At runtime PyInstaller extracts bundled files into a temporary folder available as `sys._MEIPASS`.
- If your code accesses files by relative paths (for example `assets/...`) you may need to use a helper to resolve paths when bundled. Example:

```python
import os
import sys

def resource_path(relative_path):
    base = getattr(sys, '_MEIPASS', os.path.abspath('.'))
    return os.path.join(base, relative_path)

path = resource_path('assets/images/foo.png')
```

If you want, I can add a small `packaging` helper and update the code to use `resource_path` where necessary.
