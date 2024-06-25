```markdown
# MoJ DNS Management

This repository manages DNS records for the Ministry of Justice using [octoDNS](https://github.com/octodns/octodns). It provides a streamlined, code-based approach to DNS management, ensuring consistency and enabling version control for our DNS records.

## Repository Structure
```
.
├── .github/                # GitHub Actions workflows
├── hostedzones/            # DNS zone files
├── .gitignore
├── LICENSE
├── Makefile
├── README.md
├── config.yaml             # octoDNS configuration
└── requirements.txt        # Python dependencies
```

## How It Works

1. DNS records are stored as YAML files in the `hostedzones/` directory. Each file represents a single hosted zone and contains all records for that zone.

2. Changes are proposed via Pull Requests.

3. A CI/CD pipeline runs `octodns-sync` in dry-run mode for each PR, allowing for review of proposed changes.

4. Upon merging to the `main` branch, changes are automatically applied to our Route53 hosted zones.

## Making Changes

1. Clone this repository.
2. Create a new branch for your changes.
3. Edit the appropriate zone file in the `hostedzones/` directory.
4. Ensure changes are made in alphabetical order within the file.
5. Commit your changes and create a Pull Request.

Example of adding a new A record to `example.com.yaml`:

```yaml
---
'':
  type: A
  values:
    - 192.0.2.1
api:
  type: CNAME
  value: api.example.net.
# New record (note alphabetical order)
blog:
  type: A
  values:
    - 203.0.113.10
www:
  type: CNAME
  value: example.com.

## Configuration

The `config.yaml` file is set up dynamically to encompass all hosted zones in the mojdsd AWS account. We use the `lenient` option due to historical non-uniform record creation.

## CI/CD Pipeline

- Pull Requests: Triggers a dry-run of `octodns-sync` to preview changes.
- Merge to `main`: Applies changes to Route53 using `octodns-sync --doit`. Changes typically take about 2 minutes to propagate.

## AWS IAM User

The AWS IAM user required for this DNS management system is not created or managed within this repository. Instead, it is provisioned and maintained in the separate [operations-engineering repository](https://github.com/ministyofjustice/operations-engineering).

This approach centralises our IAM user management and ensures that the DNS management system uses credentials that are consistently managed alongside our other operational resources.

## Requirements to Run Locally

- Python 3.x
- AWS IAM user with appropriate Route53 permissions

:warning: **Caution:** We strongly recommend you don't run `octodns-sync --doit` locally. Instead, use the CI/CD pipeline to apply changes.

To install dependencies:

```bash
pip install -r requirements.txt
```

## Contributing

1. Fork the repository

2. Create your feature branch (git checkout -b feature/AmazingFeature)

3. Commit your changes (git commit -m 'Add some AmazingFeature')

4. Push to the branch (git push origin feature/AmazingFeature)

5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
```
