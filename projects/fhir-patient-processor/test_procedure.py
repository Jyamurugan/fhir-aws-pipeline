import json
from fhir.resources.R4B.procedure import Procedure

test_data = """
{
      "resourceType": "Procedure",
      "id": "207a0593-7e4e-0556-b8ba-f70f7a3e0f44",
      "meta": {
        "profile": [ "http://hl7.org/fhir/us/core/StructureDefinition/us-core-procedure" ]
      },
      "status": "completed",
      "code": {
        "coding": [ {
          "system": "http://snomed.info/sct",
          "code": "710824005",
          "display": "Assessment of health and social care needs (procedure)"
        } ],
        "text": "Assessment of health and social care needs (procedure)"
      },
      "subject": {
        "reference": "urn:uuid:dbc4a3f7-9c69-4435-3ce3-4e1988ab6b91"
      },
      "encounter": {
        "reference": "urn:uuid:eaeb9228-4420-5e9c-b217-4c1a98ff9fe0"
      },
      "performedPeriod": {
        "start": "2015-09-05T21:57:47+00:00",
        "end": "2015-09-05T22:48:16+00:00"
      },
      "location": {
        "reference": "Location?identifier=https://github.com/synthetichealth/synthea|16162e2e-393c-3162-8e09-a84a60d825c4",
        "display": "WHITLEY WELLNESS LLC"
      }
    }
"""

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

flattened_condition = flatten_procedure(Procedure.model_validate_json((test_data)))

print(json.dumps(flattened_condition, default=str, indent=2))