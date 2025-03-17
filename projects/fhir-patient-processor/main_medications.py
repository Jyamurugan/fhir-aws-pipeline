import json
import boto3
import os
from fhir.resources.R4B.medicationrequest import MedicationRequest

"""
{
      "resourceType": "MedicationRequest",
      "id": "6da9c0a3-e64c-dc18-f91d-fd02b118d830",
      "meta": {
        "profile": [ "http://hl7.org/fhir/us/core/StructureDefinition/us-core-medicationrequest" ]
      },
      "status": "stopped",
      "intent": "order",
      "category": [ {
        "coding": [ {
          "system": "http://terminology.hl7.org/CodeSystem/medicationrequest-category",
          "code": "outpatient",
          "display": "Outpatient"
        } ],
        "text": "Outpatient"
      } ],
      "medicationReference": {
        "reference": "urn:uuid:128ba33a-48c1-b225-23fb-bbaafca43cc2"
      },
      "subject": {
        "reference": "urn:uuid:dbc4a3f7-9c69-4435-3ce3-4e1988ab6b91"
      },
      "encounter": {
        "reference": "urn:uuid:558f5e6b-6cda-45ab-5de7-8e1e7159c59e"
      },
      "authoredOn": "2017-10-01T00:53:16+00:00",
      "requester": {
        "reference": "Practitioner?identifier=http://hl7.org/fhir/sid/us-npi|9999990093",
        "display": "Dr. Sharilyn202 Wolff180"
      },
      "reasonReference": [ {
        "reference": "urn:uuid:8cc23f39-fd83-2947-ea77-2b2f18d0c067",
        "display": "Gingivitis (disorder)"
      } ]
    }
"""

s3 = boto3.client('s3')
destination_bucket = os.environ['DESTINATION_BUCKET']

def flatten(medication: MedicationRequest):
    """Flatten MedicationRequest resource into a dictionary."""
    flattened = {
        'id': medication.id,
        'status': medication.status,
        'intent': medication.intent,
        'category': medication.category[0].coding[0].code if medication.category and medication.category[0].coding else None,
        'medicationReference': medication.medicationReference.reference if medication.medicationReference else None,
        'subject': medication.subject.reference if medication.subject else None,
        'encounter': medication.encounter.reference if medication.encounter else None,
        'authoredOn': medication.authoredOn,
        'requester': medication.requester.reference if medication.requester else None,
        'reasonReference': medication.reasonReference[0].reference if medication.reasonReference else None,
    }

    return {k: v for k, v in flattened.items() if v is not None}

def handler(event, context):
    print(json.dumps(event))
    for record in event['Records']:
        messageBody = json.loads(record['body'])
        encounterJSONString = json.loads(messageBody['Message'])
        print(encounterJSONString)
        encounter = MedicationRequest.model_validate_json(encounterJSONString)
        flattened_encounter = flatten(encounter)
        s3.put_object(
            Bucket=destination_bucket,
            Key=f"Medications/{flattened_encounter['id']}.json",
            Body=json.dumps(flattened_encounter, default=str)
        )
    return {
        'statusCode': 200,
        'body': 'Processed successfully'
    }
