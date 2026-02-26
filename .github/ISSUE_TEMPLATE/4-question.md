---
name: Question / Help
description: Ask a question or get help
title: "[QUESTION]: "
labels: ["question"]
assignees: []

body:
  - type: markdown
    attributes:
      value: |
        Have a question about IONOS FinOps? We're here to help! Please provide as much detail as possible.

  - type: textarea
    id: question
    attributes:
      label: Your Question
      description: What would you like to know?
      placeholder: What's your question?
    validations:
      required: true

  - type: dropdown
    id: question-type
    attributes:
      label: Question Type
      description: What type of question is this?
      options:
        - Installation / Setup
        - Usage / How-to
        - Terraform integration
        - Pricing data
        - CI/CD integration
        - Development / Contributing
        - Other
    validations:
      required: true

  - type: textarea
    id: context
    attributes:
      label: Context
      description: Please provide context about your situation
      placeholder: |
        What are you trying to accomplish?
        What have you tried so far?
        What's your setup like?

  - type: textarea
    id: terraform-config
    attributes:
      label: Terraform Configuration (if applicable)
      description: Share relevant Terraform configuration
      placeholder: |
        ```hcl
        resource "ionos_server" "example" {
          # Your configuration here
        }
        ```
      render: markdown

  - type: textarea
    id: command-output
    attributes:
      label: Command Output (if applicable)
      description: Share any relevant command output or error messages
      placeholder: |
        ```
        $ ionos-finops breakdown --path .
        [Output here]
        ```
      render: markdown

  - type: textarea
    id: environment
    attributes:
      label: Environment Information
      description: Your environment details
      placeholder: |
        - IONOS FinOps version: 0.1.0
        - Python version: 3.11
        - OS: macOS 13.0
        - Terraform version: 1.5.0

  - type: checkboxes
    id: terms
    attributes:
      label: Before You Ask
      description: Please confirm the following
      options:
        - label: I have read the README documentation
          required: true
        - label: I have searched existing issues for similar questions
          required: true
        - label: I have checked the project wiki (if available)
          required: false
