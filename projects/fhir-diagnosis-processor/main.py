import json
import boto3
import os
from fhir.resources.R4B.condition import Condition

s3 = boto3.client('s3')
destination_bucket = os.environ['DESTINATION_BUCKET']

def flatten_condition(condition: Condition):
    """
    Returns a flattened dictionary with key-value pairs as strings
    """
    flattened = {
        'id': condition.id,
        'clinicalStatus': condition.clinicalStatus.coding[0].code if condition.clinicalStatus and condition.clinicalStatus.coding else None,
        'verificationStatus': condition.verificationStatus.coding[0].code if condition.verificationStatus and condition.verificationStatus.coding else None,
        'category': condition.category[0].coding[0].code if condition.category and condition.category[0].coding else None,
        'severity': condition.severity.coding[0].code if condition.severity and condition.severity.coding else None,
        'code': condition.code.coding[0].code if condition.code and condition.code.coding else None,
        'code_display': condition.code.coding[0].display if condition.code and condition.code.coding else None,
        'bodySite': condition.bodySite[0].coding[0].code if condition.bodySite and condition.bodySite[0].coding else None,
        'bodySite_display': condition.bodySite[0].display if condition.bodySite and condition.bodySite[0].coding else None,
        'patient': condition.subject.reference if condition.subject else None,
        'encounter_reference': condition.encounter.reference if condition.encounter else None,
        'onsetDateTime': condition.onsetDateTime if condition.onsetDateTime else '',
        'abatementDateTime': condition.abatementDateTime if condition.abatementDateTime else '',
        'recordedDate': condition.recordedDate if condition.recordedDate else '',
        'asserter': condition.asserter.reference if condition.asserter else None
    }
    if flattened['patient']:
        flattened['patient'] = flattened['patient'].split(":")[-1]
        
    if flattened['encounter_reference']:
        flattened['encounter_reference'] = flattened['encounter_reference'].split(":")[-1]
        

    return {k: v for k, v in flattened.items() if v is not None}

def handler(event, context):
    print(json.dumps(event))
    for record in event['Records']:
        messageBody = json.loads(record['body'])
        conditionJSONString = json.loads(messageBody['Message'])
        print(conditionJSONString)
        condition = Condition.model_validate_json(conditionJSONString)
        flattened_condition = flatten_condition(condition)
        s3.put_object(
            Bucket=destination_bucket,
            Key=f"Conditions/{flattened_condition['id']}.json",
            Body=json.dumps(flattened_condition, default=str)
        )
    return {
        'statusCode': 200,
        'body': 'Processed successfully'
    }
