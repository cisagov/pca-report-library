# pca-report-library #

[![GitHub Build Status](https://github.com/cisagov/pca-report-library/workflows/build/badge.svg)](https://github.com/cisagov/pca-report-library/actions)
[![Coverage Status](https://coveralls.io/repos/github/cisagov/pca-report-library/badge.svg?branch=develop)](https://coveralls.io/github/cisagov/pca-report-library?branch=develop)
[![Total alerts](https://img.shields.io/lgtm/alerts/g/cisagov/pca-report-library.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/cisagov/pca-report-library/alerts/)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/cisagov/pca-report-library.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/cisagov/pca-report-library/context:python)
[![Known Vulnerabilities](https://snyk.io/test/github/cisagov/pca-report-library/develop/badge.svg)](https://snyk.io/test/github/cisagov/pca-report-library)

This package is used for generating PCA reports with LaTeX and supporting
scripts. The following are available commands after from inside the docker:

`pca-report-generator` - Builds PCA LaTeX report and complies the PDF

`pca-report-templates` - Exports the Report Mustache template and Manual data
file template

`pca-report-compiler` -  Compiles a PCA LaTeX report file,  still in development.

`pca-support-scripts` - Exports the pca-data script for pulling data from PCA
database and the pca-template-stats for looking at templates from the PCA
Database. REQUIRES OTHER DOCKERS

## Contributing ##

We welcome contributions!  Please see [`CONTRIBUTING.md`](CONTRIBUTING.md) for
details.

## License ##

This project is in the worldwide [public domain](LICENSE).

This project is in the public domain within the United States, and
copyright and related rights in the work worldwide are waived through
the [CC0 1.0 Universal public domain
dedication](https://creativecommons.org/publicdomain/zero/1.0/).

All contributions to this project will be released under the CC0
dedication. By submitting a pull request, you are agreeing to comply
with this waiver of copyright interest.
