---
name: Feature Request
description: Suggest a new feature or enhancement
title: "[FEATURE]: "
labels: ["enhancement"]
assignees: []

body:
  - type: markdown
    attributes:
      value: |
        Thanks for suggesting a new feature! Please provide as much detail as possible.

  - type: textarea
    id: feature-description
    attributes:
      label: Feature Description
      description: A clear and concise description of the feature you'd like
      placeholder: What feature would you like to see?
    validations:
      required: true

  - type: textarea
    id: problem-statement
    attributes:
      label: Problem Statement
      description: What problem does this feature solve?
      placeholder: What problem are you trying to solve?
    validations:
      required: true

  - type: textarea
    id: proposed-solution
    attributes:
      label: Proposed Solution
      description: How would you like this feature to work?
      placeholder: How should this feature work?
    validations:
      required: true

  - type: textarea
    id: alternatives
    attributes:
      label: Alternatives Considered
      description: What alternative solutions have you considered?
      placeholder: What other approaches have you considered?

  - type: textarea
    id: use-cases
    attributes:
      label: Use Cases
      description: How would you use this feature?
      placeholder: Provide specific examples of how you would use this feature

  - type: textarea
    id: terraform-example
    attributes:
      label: Terraform Example (if applicable)
      description: Example Terraform configuration that would use this feature
      placeholder: |
        ```hcl
        resource "ionos_server" "example" {
          # Example configuration
        }
        ```
      render: markdown

  - type: dropdown
    id: feature-type
    attributes:
      label: Feature Type
      description: What type of feature is this?
      options:
        - New resource support
        - Cost calculation enhancement
        - Output format improvement
        - CI/CD integration
        - Performance improvement
        - Documentation
        - Other
    validations:
      required: true

  - type: textarea
    id: additional-context
    attributes:
      label: Additional Context
      description: Any other context about the feature request
      placeholder: Add any other context or screenshots
      render: markdown

  - type: checkboxes
    id: terms
    attributes:
      label: Confirmation
      description: Please confirm the following
      options:
        - label: I have searched existing issues for similar requests
          required: true
        - label: I have provided all the requested information
          required: true
