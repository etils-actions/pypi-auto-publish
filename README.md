# pypi-auto-publish

Trigger a PyPI and GitHub release everytime the package version is increased.

This support any [PEP 518](https://www.python.org/dev/peps/pep-0518/) compliant projects (flit, setuptools, poetry,...).

This action:

* Auto-detect when the package version is increased (in the `pyproject.toml`, `module.__version__` when using flit, `setup`,...)
* Trigger a PyPI release of the project (build and publish)
* Auto-extract release notes from the `CHANGELOG.md` (if `parse-changelog` is `true`)
* Create the associated tag (e.g. `v1.0.0`) and GitHub release.

Example of usage:

```yaml
name: Auto-publish

on: [push, workflow_dispatch]

jobs:
  # Auto-publish when version is increased
  publish-job:
    # Only publish on `main` branch
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    permissions:  # Don't forget permissions
      contents: write

    steps:
    - uses: etils-actions/pypi-auto-publish@v1
      with:
        pypi-token: ${{ secrets.PYPI_API_TOKEN }}
        gh-token: ${{ secrets.GITHUB_TOKEN }}
        parse-changelog: true
```

You can also chain this job with your unittests to only trigger release if tests passes (`needs: my-test-job`).

## Inputs

* `pypi-token`: The PyPI token to publish the package. If missing, PyPI release is skipped.
* `gh-token`: GitHub action token. If missing, GitHub release is skipped.
* `parse-changelog`: If `true`, extract GitHub release notes from the `CHANGELOG.md` (assuming [keep a changelog
](https://keepachangelog.com/) format)
* `path` (Optional): Directory of the project (containing the `pyproject.toml`). Default to `.`.
* `pkg-name` (Optional): Package name (auto-detected).
* `git-ref` (Optional): Git ref (e.g. SHA or tag). If `git-ref: skip`, the repository is
  not checked out (this can be used to manually checkout and update the repo before publishing).

## Outputs

* `version`: The detected version of the project (e.g. `'1.0.0'`)
* `is-released`: Whether a new release was triggered (`'true'` / `'false'`)
