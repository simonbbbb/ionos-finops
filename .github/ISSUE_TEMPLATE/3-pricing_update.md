---
name: Pricing Update
description: Report outdated pricing or suggest pricing data updates
title: "[PRICING]: "
labels: ["pricing"]
assignees: []

body:
  - type: markdown
    attributes:
      value: |
        Thanks for helping keep pricing data current! Please provide details about the pricing discrepancy.

  - type: dropdown
    id: region
    attributes:
      label: Region
      description: Which region has incorrect pricing?
      options:
        - de/fra (Frankfurt)
        - de/ber (Berlin)
        - de/fra2 (Frankfurt 2)
        - gb/lhr (London)
        - gb/wor (Worchester)
        - fr/par (Paris)
        - es/log (Logroño)
        - us/las (Las Vegas)
        - us/ewr (Newark)
        - us/kc (Lenexa)
        - All regions
        - Other
    validations:
      required: true

  - type: dropdown
    id: resource-type
    attributes:
      label: Resource Type
      description: Which resource type has incorrect pricing?
      options:
        - Compute (Servers, Cubes, VCPUs, RAM)
        - Storage (Block Storage, S3)
        - Networking (Load Balancers, IP Addresses)
        - Databases (PostgreSQL, MongoDB, MySQL, MariaDB)
        - Kubernetes (Clusters, Node Pools)
        - Backup
        - Multiple resource types
        - Other
    validations:
      required: true

  - type: textarea
    id: current-pricing
    attributes:
      label: Current Pricing in Tool
      description: What pricing does the tool currently show?
      placeholder: Current pricing values...

  - type: textarea
    id: expected-pricing
    attributes:
      label: Expected Pricing
      description: What should the correct pricing be?
      placeholder: Correct pricing values...
    validations:
      required: true

  - type: textarea
    id: source
    attributes:
      label: Source of Correct Pricing
      description: Where did you find the correct pricing?
      placeholder: e.g., IONOS website pricing calculator, official documentation, billing statement
    validations:
      required: true

  - type: textarea
    id: url
    attributes:
      label: URL Reference
      description: URL where you found the correct pricing
      placeholder: https://www.ionos.com/enterprise-cloud/pricing

  - type: textarea
    id: terraform-example
    attributes:
      label: Terraform Configuration Example
      description: Example Terraform config that shows the pricing discrepancy
      placeholder: |
        ```hcl
        resource "ionos_server" "example" {
          cores = 2
          ram = 4096
          # ...
        }
        ```
      render: markdown

  - type: textarea
    id: additional-context
    attributes:
      label: Additional Context
      description: Any other relevant information
      placeholder: Additional details about the pricing discrepancy

  - type: checkboxes
    id: terms
    attributes:
      label: Confirmation
      description: Please confirm the following
      options:
        - label: I have checked the IONOS website for current pricing
          required: true
        - label: I have verified the pricing discrepancy with actual IONOS resources
          required: true
        - label: I am willing to submit a pull request with the pricing update
          required: false
