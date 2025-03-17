import json
from fhir.resources.R4B.condition import Condition

condition = """{
      "resourceType": "Condition",
      "id": "1a928eaf-9794-92dc-4976-7622f29c8055",
      "meta": {
        "profile": [ "http://hl7.org/fhir/us/core/StructureDefinition/us-core-condition-encounter-diagnosis" ]
      },
      "clinicalStatus": {
        "coding": [ {
          "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
          "code": "active"
        } ]
      },
      "verificationStatus": {
        "coding": [ {
          "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status",
          "code": "confirmed"
        } ]
      },
      "category": [ {
        "coding": [ {
          "system": "http://terminology.hl7.org/CodeSystem/condition-category",
          "code": "encounter-diagnosis",
          "display": "Encounter Diagnosis"
        } ]
      } ],
      "code": {
        "coding": [ {
          "system": "http://snomed.info/sct",
          "code": "224299000",
          "display": "Received higher education (finding)"
        } ],
        "text": "Received higher education (finding)"
      },
      "subject": {
        "reference": "urn:uuid:dbc4a3f7-9c69-4435-3ce3-4e1988ab6b91"
      },
      "encounter": {
        "reference": "urn:uuid:08fd968f-bf87-723d-ce42-2b844106e4d1"
      },
      "onsetDateTime": "1977-09-24T22:47:39+00:00",
      "recordedDate": "1977-09-24T22:47:39+00:00"
    }
"""

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

flattened_condition = flatten_condition(Condition.model_validate_json((condition)))

print(json.dumps(flattened_condition, default=str, indent=2))