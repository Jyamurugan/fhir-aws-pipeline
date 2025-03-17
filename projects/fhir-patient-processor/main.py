import json
import boto3
import os
from fhir.resources.R4B.patient import Patient

s3 = boto3.client('s3')
destination_bucket = os.environ['DESTINATION_BUCKET']

def flatten_patient(patient: Patient):
    """
    Returns a flattened dictionary with key-value pairs as strings
    """
    flattened = {
        'id': patient.id,
        'gender': patient.gender,
        'birthDate': patient.birthDate,
        'maritalStatus': patient.maritalStatus.text if patient.maritalStatus else None,
        'race': patient.extension[0].valueString if patient.extension and len(patient.extension) > 0 else None,
        'ethnicity': patient.extension[1].valueString if patient.extension and len(patient.extension) > 1 else None,
        'birthPlace': patient.extension[2].valueString if patient.extension and len(patient.extension) > 2 else None
    }

    if patient.name:
        for i, name in enumerate(patient.name):
            flattened[f'name_{name.use}_given'] = ' '.join(name.given) if name.given else ''
            flattened[f'name_{name.use}_family'] = name.family if name.family else ''

    if patient.address:
        for i, addr in enumerate(patient.address):
            flattened[f'address_{i}_line'] = ' '.join(addr.line) if addr.line else ''
            flattened[f'address_{i}_city'] = addr.city if addr.city else ''
            flattened[f'address_{i}_state'] = addr.state if addr.state else ''
            flattened[f'address_{i}_postalCode'] = addr.postalCode if addr.postalCode else ''
            flattened[f'address_{i}_country'] = addr.country if addr.country else ''

    if patient.telecom:
        for i, telecom in enumerate(patient.telecom):
            if telecom.system == 'phone':
                flattened[f'phone_{i}'] = telecom.value if telecom.value else ''

    return {k: v for k, v in flattened.items() if v is not None}

def handler(event, context):
    print(json.dumps(event))
    for record in event['Records']:
        messageBody = json.loads(record['body'])
        patientJSONString = json.loads(messageBody['Message'])
        print(patientJSONString)
        patient = Patient.model_validate_json(patientJSONString)
        flattened_patient = flatten_patient(patient)
        s3.put_object(
            Bucket=destination_bucket,
            Key=f"Patients/{flattened_patient['id']}.json",
            Body=json.dumps(flattened_patient, default=str)
        )
    return {
        'statusCode': 200,
        'body': 'Processed successfully'
    }
