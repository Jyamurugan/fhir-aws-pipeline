import json
import boto3
import os
from fhir.resources.R4B.claim import Claim

s3 = boto3.client('s3')
destination_bucket = os.environ['DESTINATION_BUCKET']

def flatten_claim(claim: Claim):
    """
    Returns a flattened dictionary with key-value pairs as strings
    """
    flattened = {
        'id': claim.id,
        'status': claim.status,
        'type': claim.type.coding[0].code if claim.type and claim.type.coding else None,
        'use': claim.use,
        'patient': claim.patient.reference if claim.patient else None,
        'created': claim.created,
        'insurer': claim.insurer.coverage.display if claim.insurer else None,
        'provider': claim.provider.display if claim.provider else None,
        'priority': claim.priority.coding[0].code if claim.priority and claim.priority.coding else None,
        'total': claim.total.value if claim.total else '',
        'currency': claim.total.currency if claim.total else '',
        'diagnosis_reference': claim.diagnosis[0].diagnosisReference.reference if claim.diagnosis and len(claim.diagnosis) > 0 else None,
        'procedure_reference': claim.procedure[0].procedureReference.reference if claim.procedure and len(claim.procedure) > 0 else None,
        'facility': claim.facility.display if claim.facility and claim.facility else None,
    }
    if flattened['diagnosis_reference']:
        flattened['diagnosis_reference'] = flattened['diagnosis_reference'].split(":")[-1]
    if flattened['procedure_reference']:
        flattened['procedure_reference'] = flattened['procedure_reference'].split(":")[-1]

    if claim.item:
        for i, item in enumerate(claim.item):
            flattened[f'item_{i}_sequence'] = item.sequence
            flattened[f'item_{i}_productOrService'] = item.productOrService.coding[0].code if item.productOrService and item.productOrService.coding else None
            flattened[f'item_{i}_servicedDate'] = item.servicedDate if item.servicedDate else ''
            flattened[f'item_{i}_unitPrice'] = item.unitPrice.value if item.unitPrice else ''
            flattened[f'item_{i}_net'] = item.net.value if item.net else ''

    return {k: v for k, v in flattened.items() if v is not None}

def handler(event, context):
    print(json.dumps(event))
    for record in event['Records']:
        messageBody = json.loads(record['body'])
        claimJSONString = json.loads(messageBody['Message'])
        print(claimJSONString)
        claim = Claim.model_validate_json(claimJSONString)
        flattened_claim = flatten_claim(claim)
        s3.put_object(
            Bucket=destination_bucket,
            Key=f"Claims/{flattened_claim['id']}.json",
            Body=json.dumps(flattened_claim, default=str)
        )
    return {
        'statusCode': 200,
        'body': 'Processed successfully'
    }
