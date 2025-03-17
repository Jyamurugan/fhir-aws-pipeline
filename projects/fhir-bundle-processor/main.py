import json
import os
import boto3
import logging
from fhir.resources.R4B.bundle import Bundle

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

sns_client = boto3.client('sns')
topic_arn = os.environ['DESTINATION_TOPIC_ARN']

def handler(event, context):
    try:
        # Parse the S3 event
        s3_event = event['Records'][0]['s3']
        bucket_name = s3_event['bucket']['name']
        object_key = s3_event['object']['key']
        logger.info(f"Received event for bucket: {bucket_name}, key: {object_key}")

        # Get the FHIR bundle from S3
        s3_client = boto3.client('s3')
        response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
        bundle_data = response['Body'].read().decode('utf-8')
        logger.info("Successfully retrieved FHIR bundle from S3")

        # Parse the FHIR bundle
        try:
            bundle = Bundle.model_validate_json(bundle_data)
            logger.info("Successfully parsed FHIR bundle")
        except Exception as e:
            logger.error(f"Error parsing FHIR bundle: {str(e)}", exc_info=True)
            return {
            'statusCode': 400,
            'body': 'Error parsing FHIR bundle'
            },

        # Extract resources
        resources = {
            'Patient': [],
            'Claim': [],
            'Condition': [],
            'Encounter': [],
            'Procedure': [],
            'Medication': []
        }

        for entry in bundle.entry:
            resource = entry.resource
            resource_type = resource.__resource_type__
            if resource_type in resources:
                resources[resource_type].append(resource.json())
        logger.info("Successfully extracted resources from FHIR bundle")

        # Publish resources to SNS
        for resource_type, resource_list in resources.items():
            for resource in resource_list:
                sns_client.publish(
                    TopicArn=topic_arn,
                    Message=json.dumps(resource),
                    MessageAttributes={
                        'ResourceType': {
                            'DataType': 'String',
                            'StringValue': resource_type
                        }
                    }
                )
        logger.info("Successfully published resources to SNS")

        return {
            'statusCode': 200,
            'body': 'Event received and processed'
        }

    except Exception as e:
        logger.error(f"Error processing event: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': 'Error processing event'
        }