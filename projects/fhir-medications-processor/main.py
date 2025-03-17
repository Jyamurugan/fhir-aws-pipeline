import json
import boto3
import os
from fhir.resources.R4B.medication import Medication

"""
{
      "resourceType": "Medication",
      "id": "128ba33a-48c1-b225-23fb-bbaafca43cc2",
      "meta": {
        "profile": [ "http://hl7.org/fhir/us/core/StructureDefinition/us-core-medication" ]
      },
      "code": {
        "coding": [ {
          "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
          "code": "1535362",
          "display": "sodium fluoride 0.0272 MG/MG Oral Gel"
        } ],
        "text": "sodium fluoride 0.0272 MG/MG Oral Gel"
      },
      "status": "active"
    }
"""

s3 = boto3.client('s3')
destination_bucket = os.environ['DESTINATION_BUCKET']

def flatten_encounter(encounter: Encounter):
    """Flatten Encounter resource into a dictionary."""
    flattened = {
        'id': encounter.id,
        'status': encounter.status,
        'class_code': encounter.class_fhir.code if encounter.class_fhir else None,
        'class_system': encounter.class_fhir.system if encounter.class_fhir else None,
        'type_code': encounter.type[0].coding[0].code if encounter.type and encounter.type[0].coding else None,
        'type_display': encounter.type[0].coding[0].display if encounter.type and encounter.type[0].coding else None,
        'patient': encounter.subject.reference if encounter.subject else None,
        'period_start': encounter.period.start if encounter.period else None,
        'period_end': encounter.period.end if encounter.period else None,
        'reason_code': encounter.reasonCode[0].coding[0].code if encounter.reasonCode and encounter.reasonCode[0].coding else None,
        'reason_display': encounter.reasonCode[0].coding[0].display if encounter.reasonCode and encounter.reasonCode[0].coding else None,
        'location': encounter.location[0].location.display if encounter.location and encounter.location[0].location else None,
        'serviceProvider': encounter.serviceProvider.display if encounter.serviceProvider else None,
    }
    
    if flattened['patient']:
        flattened['patient'] = flattened['patient'].split(":")[-1]

    return {k: v for k, v in flattened.items() if v is not None}

def handler(event, context):
    print(json.dumps(event))
    for record in event['Records']:
        messageBody = json.loads(record['body'])
        encounterJSONString = json.loads(messageBody['Message'])
        print(encounterJSONString)
        encounter = Medication.model_validate_json(encounterJSONString)
        flattened_encounter = flatten_encounter(encounter)
        s3.put_object(
            Bucket=destination_bucket,
            Key=f"Encounters/{flattened_encounter['id']}.json",
            Body=json.dumps(flattened_encounter, default=str)
        )
    return {
        'statusCode': 200,
        'body': 'Processed successfully'
    }
