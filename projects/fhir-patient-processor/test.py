import json
from fhir.resources.R4B.claim import Claim

claim = """
{
      "resourceType": "Claim",
      "id": "802c9b6e-8b93-c088-4846-93e938dba290",
      "status": "active",
      "type": {
        "coding": [ {
          "system": "http://terminology.hl7.org/CodeSystem/claim-type",
          "code": "professional"
        } ]
      },
      "use": "claim",
      "patient": {
        "reference": "urn:uuid:dbc4a3f7-9c69-4435-3ce3-4e1988ab6b91",
        "display": "Ada662 Sari509 Balistreri607"
      },
      "billablePeriod": {
        "start": "1976-09-18T21:57:47+00:00",
        "end": "1976-09-18T22:12:47+00:00"
      },
      "created": "1976-09-18T22:12:47+00:00",
      "provider": {
        "reference": "Organization?identifier=https://github.com/synthetichealth/synthea|e2a8b444-9b8f-36ff-84c4-05ee98589482",
        "display": "WHITLEY WELLNESS LLC"
      },
      "priority": {
        "coding": [ {
          "system": "http://terminology.hl7.org/CodeSystem/processpriority",
          "code": "normal"
        } ]
      },
      "facility": {
        "reference": "Location?identifier=https://github.com/synthetichealth/synthea|16162e2e-393c-3162-8e09-a84a60d825c4",
        "display": "WHITLEY WELLNESS LLC"
      },
      "diagnosis": [ {
        "sequence": 1,
        "diagnosisReference": {
          "reference": "urn:uuid:fed419a9-b9b2-130d-2cc0-8623220c0d9b"
        }
      } ],
      "insurance": [ {
        "sequence": 1,
        "focal": true,
        "coverage": {
          "display": "NO_INSURANCE"
        }
      } ],
      "item": [ {
        "sequence": 1,
        "productOrService": {
          "coding": [ {
            "system": "http://snomed.info/sct",
            "code": "410620009",
            "display": "Well child visit (procedure)"
          } ],
          "text": "Well child visit (procedure)"
        },
        "encounter": [ {
          "reference": "urn:uuid:2fae0e14-5528-1dc9-e682-5bd60bf7e018"
        } ]
      }, {
        "sequence": 2,
        "diagnosisSequence": [ 1 ],
        "productOrService": {
          "coding": [ {
            "system": "http://snomed.info/sct",
            "code": "160968000",
            "display": "Risk activity involvement (finding)"
          } ],
          "text": "Risk activity involvement (finding)"
        }
      } ],
      "total": {
        "value": 704.20,
        "currency": "USD"
      }
    }
"""

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

flattened_claim = flatten_claim(Claim.model_validate_json((claim)))

print(json.dumps(flattened_claim, default=str, indent=2))