---
name: Bug Report
description: Report a bug or unexpected behavior
title: "[BUG]: "
labels: ["bug"]
assignees: []

body:
  - type: markdown
    attributes:
      value: |
        Thanks for taking the time to fill out this bug report! Please provide as much detail as possible.

  - type: textarea
    id: description
    attributes:
      label: Bug Description
      description: A clear and concise description of what the bug is
      placeholder: What happened?
    validations:
      required: true

  - type: textarea
    id: reproduction-steps
    attributes:
      label: Steps to Reproduce
      description: Steps to reproduce the behavior
      placeholder: |
        1. Run '...'
        2. Click on '....'
        3. See error
    validations:
      required: true

  - type: textarea
    id: expected-behavior
    attributes:
      label: Expected Behavior
      description: What you expected to happen
      placeholder: What should have happened?
    validations:
      required: true

  - type: textarea
    id: actual-behavior
    attributes:
      label: Actual Behavior
      description: What actually happened
      placeholder: What actually happened instead?
    validations:
      required: true

  - type: textarea
    id: terraform-files
    attributes:
      label: Terraform Files
      description: Please provide sanitized Terraform files that reproduce the issue
      placeholder: |
        ```hcl
        resource "ionos_server" "example" {
          # Your configuration here
        }
        ```
      render: markdown

  - type: textarea
    id: ionos-finops-version
    attributes:
      label: IONOS FinOps Version
      description: Version of ionos-finops you're using
      placeholder: e.g., 0.1.0
    validations:
      required: true

  - type: textarea
    id: terraform-provider-version
    attributes:
      label: IONOS Terraform Provider Version
      description: Version of the IONOS Terraform provider
      placeholder: e.g., 2.5.0
    validations:
      required: true

  - type: textarea
    id: python-version
    attributes:
      label: Python Version
      description: Python version you're using
      placeholder: e.g., Python 3.11
    validations:
      required: true

  - type: textarea
    id: operating-system
    attributes:
      label: Operating System
      description: Your operating system
      placeholder: e.g., macOS 13.0, Ubuntu 22.04
    validations:
      required: true

  - type: textarea
    id: logs
    attributes:
      label: Logs / Error Messages
      description: Please copy and paste any relevant log output or error messages
      placeholder: |
        Paste your logs here
        ```
        ```
      render: markdown

  - type: textarea
    id: additional-context
    attributes:
      label: Additional Context
      description: Any other context about the problem
      placeholder: Add any other context about the problem here
      render: markdown

  - type: checkboxes
    id: terms
    attributes:
      label: Confirmation
      description: Please confirm the following
      options:
        - label: I have searched existing issues for similar problems
          required: true
        - label: I have provided all the requested information
          required: true
