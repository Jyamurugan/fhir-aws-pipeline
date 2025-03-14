# FHIR Bundle Processor

This project is a FHIR pipeline deployable to AWS Lambda using UV as the build tool.

## Overview

The FHIR Bundle Processor takes a JSON object from S3, validates it, and then splits the FHIR bundle into the following components:
- Patient
- Claims
- Diagnosis
- Visits
- Procedures
- Medications

Each component is then published to an SNS queue, which is provided as an environment variable `DESTINATION_TOPIC_ARN`.

## Local Testing

All events for local testing are stored under the `events` folder.

## Deployment

To deploy this project to AWS Lambda, use UV as the build tool.

## Environment Variables

- `DESTINATION_TOPIC_ARN`: The ARN of the SNS topic where the split components will be published.
