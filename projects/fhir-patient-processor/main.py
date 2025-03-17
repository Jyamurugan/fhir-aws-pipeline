import json
import boto3
import os

s3 = boto3.client('s3')
destination_bucket = os.environ['DESTINATION_BUCKET']

def flatten_patient(patient):
    def get_value(dictionary, keys, default=""):
        for key in keys:
            dictionary = dictionary.get(key, {})
        return dictionary if dictionary else default

    return {
        "resourceType": "Patient",
        "id": patient.get("id", ""),
        "name": f"{get_value(patient, ['name', 0, 'given', 0])} {get_value(patient, ['name', 0, 'given', 1])} {get_value(patient, ['name', 0, 'family'])}",
        "gender": patient.get("gender", ""),
        "birthDate": patient.get("birthDate", ""),
        "address": f"{get_value(patient, ['address', 0, 'line', 0])}, {get_value(patient, ['address', 0, 'city'])}, {get_value(patient, ['address', 0, 'state'])}, {get_value(patient, ['address', 0, 'postalCode'])}, {get_value(patient, ['address', 0, 'country'])}",
        "phone": get_value(patient, ['telecom', 0, 'value']),
        "maritalStatus": get_value(patient, ['maritalStatus', 'text']),
        "race": get_value(patient, ['extension', 0, 'extension', 1, 'valueString']),
        "ethnicity": get_value(patient, ['extension', 1, 'extension', 1, 'valueString']),
        "birthPlace": f"{get_value(patient, ['extension', 4, 'valueAddress', 'city'])}, {get_value(patient, ['extension', 4, 'valueAddress', 'state'])}, {get_value(patient, ['extension', 4, 'valueAddress', 'country'])}"
    }

def handler(event, context):
    for record in event['Records']:
        patient = json.loads(record['body'])
        flattened_patient = flatten_patient(patient)
        s3.put_object(
            Bucket=destination_bucket,
            Key=f"flattened/{flattened_patient['id']}.json",
            Body=json.dumps(flattened_patient)
        )
    return {
        'statusCode': 200,
        'body': 'Processed successfully'
    }
