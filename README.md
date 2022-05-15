# pypi-auto-publish

Build &amp; publish to PyPI everytime the package version is increased.

This support any [PEP 518](https://www.python.org/dev/peps/pep-0518/) compliant projects (flit, setuptools, poetry,...).

Example of usage:

```yaml
name: Auto-publish

# Allow to trigger the workflow manually (e.g. when deps changes)
on: [push, workflow_dispatch]

jobs:
  # Auto-publish when version is increased
  publish-job:
    # Only try to publish if branch is `main`
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    timeout-minutes: 30

    steps:
    - uses: etils-actions/pypi-auto-publish@main
      with:
        pypi-token: ${{ secrets.PYPI_API_TOKEN }}
```

You can also chain this job with your unittests to only trigger release if tests passes.

## Inputs

* `pypi-token`: Required: the PyPI token to publish the package
* `pkg-name` (Optional): Package name (auto-detected).

## Outputs

None.
