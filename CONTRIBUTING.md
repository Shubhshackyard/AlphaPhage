# Contributing to AlphaPhage

Thank you for your interest in contributing to AlphaPhage! This document provides guidelines and instructions for contributing to this real-time narrative mining platform for financial signals.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
  - [Project Structure](#project-structure)
  - [Development Environment Setup](#development-environment-setup)
- [Development Workflow](#development-workflow)
  - [Branching Strategy](#branching-strategy)
  - [Making Changes](#making-changes)
  - [Testing](#testing)
  - [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
  - [Python Code Style](#python-code-style)
  - [JavaScript/React Code Style](#javascriptreact-code-style)
  - [Documentation](#documentation)
- [Project-Specific Guidelines](#project-specific-guidelines)
  - [Microservice Architecture](#microservice-architecture)
  - [Data Flow Considerations](#data-flow-considerations)
  - [Component Dependencies](#component-dependencies)
- [Issue Reporting](#issue-reporting)
- [Feature Requests](#feature-requests)
- [Communication](#communication)

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md). Please read it before contributing.

## Getting Started

### Project Structure

AlphaPhage follows a microservice architecture with these key components:

```
alphaphage/
├── ingestion/         # Twitter scraper and Kafka producer
├── processing/        # Spark streaming jobs for Delta Lake integration
├── nlp_service/       # Text embedding and topic modeling service
├── anomaly_detector/  # Anomaly detection on topic volumes
├── api/               # REST API for accessing data
├── dashboard/         # React frontend for visualization
├── infra/             # Docker and Kubernetes deployment files
└── docs/              # Documentation
```

### Development Environment Setup

1. **Fork and clone the repository**

   ```bash
   git clone https://github.com/YOUR-USERNAME/AlphaPhage.git
   cd AlphaPhage
   ```

2. **Set up the development environment**

   Prerequisites:
   - Python 3.8+
   - Docker and Docker Compose
   - Node.js 16+ (for dashboard)
   - Java 11+ (for Spark)
   
   For local development:
   
   ```bash
   # Create data directories
   mkdir -p data/delta/bronze/narratives
   mkdir -p data/delta/silver/narratives
   mkdir -p data/delta/gold/alerts
   mkdir -p data/models
   mkdir -p data/checkpoints
   
   # Set up environment files
   cp alphaphage/.env.example alphaphage/.env
   # Repeat for each component's .env file
   ```

3. **Use Docker Compose for development**

   ```bash
   cd alphaphage/infra
   docker-compose up
   ```

## Development Workflow

### Branching Strategy

- `main`: Production-ready code
- `develop`: Main development branch
- Feature branches: `feature/your-feature-name`
- Bug fix branches: `fix/issue-description`

### Making Changes

1. **Create a new branch from `develop`**

   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes in the appropriate component**

3. **Commit with clear, descriptive messages**

   ```bash
   git commit -m "feat(component): description of feature"
   ```

   Follow [Conventional Commits](https://www.conventionalcommits.org/) format.

### Testing

Each component should include appropriate tests:

- **Unit tests**: Test individual functions and methods
- **Integration tests**: Test interactions between components
- **End-to-end tests**: Test full workflows

To run tests for a specific component:

```bash
cd alphaphage/component_name
pytest
```

### Pull Request Process

1. **Push your branch to your fork**

   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create a pull request to the `develop` branch**

3. **Ensure your PR includes**:
   - Clear description of changes
   - Reference to any related issues
   - Documentation updates if applicable
   - Test coverage for new functionality

4. **Address feedback from code reviews**

5. **Once approved, a maintainer will merge your PR**

## Coding Standards

### Python Code Style

- Follow [PEP 8](https://peps.python.org/pep-0008/) guidelines
- Use type hints where appropriate
- Document functions and classes with docstrings
- Maximum line length: 100 characters
- Use structured JSON logging for all components

Example:

```python
import logging
import json

logger = logging.getLogger(__name__)

def process_data(input_data: dict) -> dict:
    """
    Process input data and return transformed result.
    
    Args:
        input_data: Dictionary containing the input data
        
    Returns:
        Processed data dictionary
    """
    try:
        # Processing logic here
        result = {"processed": True}
        logger.info(json.dumps({"event": "data_processed", "status": "success"}))
        return result
    except Exception as e:
        logger.error(json.dumps({"event": "data_processing_error", "error": str(e)}))
        raise
```

### JavaScript/React Code Style

- Follow Airbnb JavaScript Style Guide
- Use functional components with hooks
- Use TypeScript for type safety
- Use tailwind CSS for styling
- Document complex functions and components

Example:

```jsx
import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';

/**
 * Component to display topic trends with volume visualization
 */
const TopicTrend = ({ topic, maxVolume }) => {
  // Component logic here
  
  return (
    <div className="bg-white p-4 rounded-lg shadow-md">
      {/* Component JSX here */}
    </div>
  );
};

TopicTrend.propTypes = {
  topic: PropTypes.shape({
    topic_id: PropTypes.number.isRequired,
    topic_label: PropTypes.string.isRequired,
    volume: PropTypes.number.isRequired,
  }).isRequired,
  maxVolume: PropTypes.number.isRequired,
};

export default TopicTrend;
```

### Documentation

- Keep README.md files up to date for each component
- Document architecture decisions in docs/
- Include inline comments for complex logic
- Provide examples for API endpoints

## Project-Specific Guidelines

### Microservice Architecture

- Keep services independent and focused on specific responsibilities
- Use environment variables for configuration
- Maintain backward compatibility when possible
- Include health check endpoints for all services

### Data Flow Considerations

- Be mindful of data serialization formats between services
- Follow the Delta Lake medallion architecture (bronze -> silver -> gold)
- Include proper error handling and logging throughout the pipeline

### Component Dependencies

When adding a new dependency:
1. Justify its addition in your PR description
2. Update the appropriate requirements.txt
3. Consider the impact on container size and build time
4. Favor well-maintained libraries with active communities

## Issue Reporting

When reporting issues, please include:

1. **Description**: Clear description of the problem
2. **Steps to reproduce**: Detailed steps to reproduce the issue
3. **Expected behavior**: What you expected to happen
4. **Actual behavior**: What actually happened
5. **Environment**: Details about your environment (OS, Docker version, etc.)
6. **Logs**: Relevant log output

## Feature Requests

Feature requests are welcome! Please provide:

1. **Description**: Clear description of the proposed feature
2. **Rationale**: Why this feature would be valuable
3. **Implementation ideas**: Optional suggestions for implementation

## Communication

- **Issues and PRs**: For specific code discussions
- **Discussions**: For general questions and ideas
- **Code Reviews**: For feedback on implementation

Thank you for contributing to AlphaPhage!