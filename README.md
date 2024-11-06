# &#127760; MoJ DNS Management

[![repo standards badge](https://img.shields.io/endpoint?labelColor=231f20&color=005ea5&style=for-the-badge&label=MoJ%20Compliant&url=https%3A%2F%2Foperations-engineering-reports.cloud-platform.service.justice.gov.uk%2Fapi%2Fv2%2Fcompliant-repository%2Fdns&logo=data:image/png;base64,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)](https://operations-engineering-reports-prod.cloud-platform.service.justice.gov.uk/public-report/dns)

This repository manages the Ministry of Justice DNS records using [octoDNS](https://github.com/octodns/octodns). It provides a streamlined, code-based approach to DNS management, ensuring consistency and enabling version control for our DNS records.

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


## Configuration

The `config.yaml` file is set up dynamically to encompass all hosted zones in the mojdsd AWS account (An AWS account owned by Operations Engineering). We use the `lenient` option due to historical non-uniform record creation.

## CI/CD Pipeline

- Pull Requests: Triggers a dry-run of `octodns-sync` to preview changes.
- Merge to `main`: Applies changes to Route53 using `octodns-sync --doit`. Changes typically take about 2 minutes to propagate.

### CI/CD AWS IAM User

The AWS IAM user required for the pipelines in this repository is not created or managed within this repository. Instead, it is provisioned and maintained in the main [operations-engineering repository](https://github.com/ministryofjustice/operations-engineering).

This approach centralises our IAM user management and ensures that the DNS management system uses credentials that are consistently managed alongside our other operational resources.

## AWS Credentials

This project requires AWS credentials to interact with Route53. The Makefile will attempt to use AWS credentials from the following sources, in order:

1. Environment variables (`AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`)
2. AWS CLI configuration

If neither of these sources provides valid credentials, commands that require AWS access will fail with an error message.

To set your AWS credentials, you can either:

1. Export them as environment variables:
   ```
   export AWS_ACCESS_KEY_ID=your_access_key_id
   export AWS_SECRET_ACCESS_KEY=your_secret_access_key
   ```

2. Configure them using the AWS CLI:
   ```
   aws configure
   ```

Ensure your AWS credentials have the necessary permissions to manage Route53 hosted zones.

## Making Changes

1. Clone this repository:
   ```bash
   git clone https://github.com/your-org/dns.git
   cd dns
   ```

2. Install dependencies:
   ```bash
   make install
   ```

3. Create a new branch for your changes:
   ```bash
   git checkout -b your-branch-name
   ```

4. Edit the appropriate zone file:
   ```bash
   make edit-zone zone=example.com
   ```
   This will open the zone file in your default editor. If the file doesn't exist, it will be created.

5. Ensure changes are made in alphabetical order within the file.

6. Validate your changes:

:memo: **Note:** This may look a little messy, but you're looking for errors rather than warnings.
   ```bash
   make validate-zones
   ```

7. Perform a dry-run to see what changes would be made:
   ```bash
   make sync-dry-run
   ```

8. If you want to compare your local changes with the live configuration:
   ```bash
   make compare-zone zone=example.com
   ```

9. Commit your changes and create a Pull Request:
   ```bash
   git add .
   git commit -m "Your descriptive commit message"
   git push origin your-branch-name
   ```

10. Create a Pull Request on GitHub.

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
```

## Viewing Current Configuration

To view the current live configuration for a zone:

```bash
make dump-zone zone=example.com
```

This will dump the current Route53 configuration for `example.com` to a file in the `tmp/` directory.

## Applying Changes

:warning: **Caution:** We strongly recommend you don't apply changes locally. Instead, use the CI/CD pipeline to apply changes.

If you need to apply changes locally (which should be done with extreme caution), you can use:

```bash
make sync-apply
```

This will apply all pending changes to Route53. Always perform a `make sync-dry-run` first to review the changes that will be made.


## Makefile Commands

This repository includes a Makefile to simplify common operations. You can use the following commands:

```bash
make                    # Show help message with available commands
make help               # Same as above, shows help message
make install            # Set up the Python environment
make edit-zone zone=<zone> # Edit a hosted zone file
make validate-zones     # Validate all zone files
make sync-dry-run       # Perform a dry-run sync for all zones
make sync-apply         # Apply changes to all zones
make list-zones         # List all zones
make dump-zone zone=<zone> # Dump the current live configuration for a zone
make compare-zone zone=<zone> # Compare a zone file with its live configuration
make clean              # Clean up generated files
```

To see a full list of available commands and their descriptions, simply run `make` or `make help`.

## Identifying GitHub Pages Delegations

This repository includes functionality to identify DNS records associated with GitHub Pages. These delegations are automatically identified and logged, and a Pull Request is created weekly if changes are detected.

### Weekly Automation

A GitHub Action runs every Sunday at midnight (UTC) to identify GitHub Pages delegations across the DNS records. If any changes are detected in the delegations, a Pull Request is automatically created with the updated `.github_pages` file. This file lists all GitHub Pages delegations in the format `<record>.<hostedzone>`.

### Manual Identification

To manually identify GitHub Pages delegations, you can use the following Makefile command:
```bash
make print_github_delegation
```
This command outputs the current list of GitHub Pages delegations in the .github_pages file.

### Example .github_pages Output

The .github_pages file contains entries in the format <record>.<hostedzone>. For example:

```
cjsm.justice.gov.uk
hmpps-architecture-blueprint.service.justice.gov.uk
runbooks.operations-engineering.service.justice.gov.uk
```

### Updating the GitHub Pages Records

If you need to update the GitHub Pages records manually:

1. Run the following command to identify changes:
```bash
make print-github-delegations
```

2. Commit and push any changes to the .github_pages file:
```bash
git add .github_pages
git commit -m "Update GitHub Pages delegations"
git push
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
