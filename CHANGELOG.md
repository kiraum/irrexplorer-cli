# Changelog
All notable changes to irrexplorer-cli will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [0.0.3] - 2024-12-22
### Added
- Screenshots demonstrating CLI usage in README
- Extended timeout handling for API requests
- Improved error logging for API responses

### Fixed
- Empty response handling for prefix and ASN queries
- Security improvements:
  - Pinned third-party GitHub Action versions
  - Added proper workflow permissions

### Changed
- Enhanced documentation with visual examples
- Increased default timeout values for better reliability

[0.0.3 ⋅ Release]: https://github.com/kiraum/irrexplorer-cli/releases/tag/v0.0.3
[0.0.2 ⋅ Diff]: https://github.com/kiraum/irrexplorer-cli/compare/v0.0.2...v0.0.3


## [0.0.2] - 2024-12-21
### Added
- Long description from README.md for PyPI package
- Proper package metadata

[0.0.2 ⋅ Release]: https://github.com/kiraum/irrexplorer-cli/releases/tag/v0.0.2
[0.0.2 ⋅ Diff]: https://github.com/kiraum/irrexplorer-cli/compare/v0.0.1...v0.0.2


## [0.0.1] - 2024-12-21
### Added
- Initial development release
- Command-line interface for IRRexplorer.net queries
- Prefix information lookup functionality
- ASN details lookup functionality
- Multiple output formats (json, csv, text)
- Async support for efficient data retrieval
- Integration with IRRexplorer v2 service
- Support for Python 3.13+
- Documentation and usage examples

### Dependencies
- httpx for HTTP requests
- typer for CLI interface
- rich for text formatting

[0.0.1 ⋅ Release]: https://github.com/kiraum/irrexplorer-cli/releases/tag/v0.0.1
