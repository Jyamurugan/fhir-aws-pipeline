

import json
from fhir.resources.R4B.encounter import Encounter

test_data = """
{
      "resourceType": "Encounter",
      "id": "cdfee715-e2bb-3918-892c-e1cac7b6db42",
      "meta": {
        "profile": [ "http://hl7.org/fhir/us/core/StructureDefinition/us-core-encounter" ]
      },
      "identifier": [ {
        "use": "official",
        "system": "https://github.com/synthetichealth/synthea",
        "value": "cdfee715-e2bb-3918-892c-e1cac7b6db42"
      } ],
      "status": "finished",
      "class": {
        "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
        "code": "AMB"
      },
      "type": [ {
        "coding": [ {
          "system": "http://snomed.info/sct",
          "code": "185349003",
          "display": "Encounter for check up (procedure)"
        } ],
        "text": "Encounter for check up (procedure)"
      } ],
      "subject": {
        "reference": "urn:uuid:dbc4a3f7-9c69-4435-3ce3-4e1988ab6b91",
        "display": "Mrs. Ada662 Sari509 Balistreri607"
      },
      "participant": [ {
        "type": [ {
          "coding": [ {
            "system": "http://terminology.hl7.org/CodeSystem/v3-ParticipationType",
            "code": "PPRF",
            "display": "primary performer"
          } ],
          "text": "primary performer"
        } ],
        "period": {
          "start": "2015-09-19T21:57:47+00:00",
          "end": "2015-09-20T01:53:25+00:00"
        },
        "individual": {
          "reference": "Practitioner?identifier=http://hl7.org/fhir/sid/us-npi|9999990093",
          "display": "Dr. Sharilyn202 Wolff180"
        }
      } ],
      "period": {
        "start": "2015-09-19T21:57:47+00:00",
        "end": "2015-09-20T01:53:25+00:00"
      },
      "reasonCode": [ {
        "coding": [ {
          "system": "http://snomed.info/sct",
          "code": "66383009",
          "display": "Gingivitis (disorder)"
        } ]
      } ],
      "location": [ {
        "location": {
          "reference": "Location?identifier=https://github.com/synthetichealth/synthea|4a965fe6-ab2b-3740-bb4b-ce27c570e2ed",
          "display": "THE SHRINERS HOSPITAL FOR CHILDREN"
        }
      } ],
      "serviceProvider": {
        "reference": "Organization?identifier=https://github.com/synthetichealth/synthea|9adfae03-673d-365d-9052-f705098fa3e4",
        "display": "THE SHRINERS HOSPITAL FOR CHILDREN"
      }
    }
"""
def flatten(encounter: Encounter):
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

flattened_condition = flatten(Encounter.model_validate_json((test_data)))

print(json.dumps(flattened_condition, default=str, indent=2))