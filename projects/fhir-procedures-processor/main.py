import json
import boto3
import os
from fhir.resources.R4B.procedure import Procedure

s3 = boto3.client('s3')
destination_bucket = os.environ['DESTINATION_BUCKET']

def flatten_procedure(procedure: Procedure):
  """
  Returns a flattened dictionary with key-value pairs as strings
  """
  flattened = {
    'id': procedure.id,
    'status': procedure.status,
    'code': procedure.code.coding[0].code if procedure.code and procedure.code.coding else None,
    'code_display': procedure.code.coding[0].display if procedure.code and procedure.code.coding else None,
    'patient': procedure.subject.reference if procedure.subject else None,
    'encounter': procedure.encounter.reference if procedure.encounter else None,
    'performedPeriod_start': procedure.performedPeriod.start if procedure.performedPeriod else None,
    'performedPeriod_end': procedure.performedPeriod.end if procedure.performedPeriod else None,
    'location': procedure.location.display if procedure.location else None,
  }
  if flattened['patient']:
    flattened['patient'] = flattened['patient'].split(":")[-1]
    
  if flattened['encounter']:
    flattened['encounter'] = flattened['encounter'].split(":")[-1]
    
  if flattened['location']:
    flattened['location'] = flattened['location'].split(":")[-1]

  return {k: v for k, v in flattened.items() if v is not None}

def handler(event, context):
    print(json.dumps(event))
    for record in event['Records']:
        messageBody = json.loads(record['body'])
        procedureJSONString = json.loads(messageBody['Message'])
        print(procedureJSONString)
        procedure = Procedure.model_validate_json(procedureJSONString)
        flattened_procedure = flatten_procedure(procedure)
        s3.put_object(
            Bucket=destination_bucket,
            Key=f"Procedures/{flattened_procedure['id']}.json",
            Body=json.dumps(flattened_procedure, default=str)
        )
    return {
        'statusCode': 200,
        'body': 'Processed successfully'
    }
