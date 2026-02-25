# IONOS FinOps Examples

This directory contains example Terraform configurations to demonstrate IONOS FinOps capabilities.

## Examples

### 1. Simple Infrastructure (`simple_infrastructure.tf`)

A basic infrastructure setup including:
- 2 servers (web and app)
- Additional data volume
- Load balancer
- Public IP block
- PostgreSQL database cluster

**Estimated Monthly Cost**: ~€150-200

**To calculate costs:**

```bash
cd examples
ionos-finops breakdown --path simple_infrastructure.tf
```

### 2. Using IONOS FinOps

#### Calculate costs from a directory

```bash
ionos-finops breakdown --path /path/to/terraform
```

#### Calculate costs from a Terraform plan

```bash
terraform plan -out=plan.tfplan
ionos-finops breakdown --plan-file plan.tfplan
```

#### Output as JSON

```bash
ionos-finops breakdown --path . --format json
```

#### Output as HTML report

```bash
ionos-finops breakdown --path . --format html --output report.html
```

#### Use custom region

```bash
ionos-finops breakdown --path . --region us/las
```

### 3. Custom Pricing Configuration

Create a `.ionos-finops.yml` file:

```yaml
default_region: de/fra
currency: EUR

custom_pricing:
  compute:
    vcpu_hourly: 0.012
    ram_gb_hourly: 0.006
  storage:
    storage_ssd_gb_hourly: 0.00012
```

Then run:

```bash
ionos-finops breakdown --path . --config .ionos-finops.yml
```

## Resource Types Supported

- `ionos_server` - Virtual servers
- `ionos_cube_server` - Cube servers
- `ionos_vcpu_server` - vCPU servers
- `ionos_volume` - Block storage volumes
- `ionos_s3_bucket` - S3 object storage
- `ionos_loadbalancer` - Load balancers
- `ionos_ipblock` - IP address blocks
- `ionos_pg_cluster` - PostgreSQL clusters
- `ionos_mongo_cluster` - MongoDB clusters

## Notes

- Pricing data is based on IONOS Cloud's public pricing
- Actual costs may vary based on usage patterns and contract terms
- Network bandwidth costs are typically included in base pricing
- Some resources (NICs, firewalls) have no additional cost
