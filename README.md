# IRRexplorer CLI

A command-line interface to query and explore IRR & BGP data from IRRexplorer.net in real-time.

## Overview

IRRexplorer CLI provides a simple way to access and analyze Internet Routing Registry (IRR) and BGP data through the command line. It interfaces with the IRRexplorer v2 service to help network operators and administrators debug routing data and verify filtering strategies.

## Features

- Query prefix information
- Lookup ASN details
- Real-time data access from IRRexplorer.net
- Easy-to-use command-line interface
- Async support for efficient data retrieval

## Installation

```bash
pip install irrexplorer-cli
```

## Usage

Query Prefix Information
```bash
irrexplorer prefix 192.0.2.0/24
```

Query ASN Information
```bash
irrexplorer asn AS64496
```

The `-f` or `--format` flag allows you to specify the output format:

* `json`: Output results in JSON format
* `csv`: Output results in CSV format
* Default format is human-readable text

## Requirements

* Python 3.13+
* httpx
* typer
* rich

## Development

1. Clone the repository:
```bash
git clone https://github.com/kiraum/irrexplorer-cli.git
```

2. Create/activate venv:
```bash
python3 -m venv venv
. venv/bin/activate
```

3. Install dependencies:
```bash
pip install --upgrade uv
uv pip sync requirements.lock
```

4. Run pre-commit tests before to push:
```bash
pre-commit run --all-files
```

## Data Sources

The CLI tool queries data from IRRexplorer.net, which includes:

* IRR objects and relations (route(6) and as-sets)
* RPKI ROAs and validation status
* BGP origins from DFZ
* RIRstats

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License

See [LICENSE](LICENSE) file for details.

## Credits

This tool interfaces with IRRexplorer v2, a project maintained by Stichting NLNOG and DashCare BV.
