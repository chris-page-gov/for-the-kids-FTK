# A reusable early-years handover

Wholly fictional OKF 0.2 demonstration. No real service connection or sharing approval.

# Rehearsal scope

Synthetic demonstration only.

One fictional handover. No real child data, service connection or sharing approval.

## Source facts

```json
{
  "id": "policy-demo",
  "purpose": "Synthetic contract rehearsal only",
  "controller": "Fictional demonstration controller",
  "lawful_basis_ref": "urn:example:synthetic-no-real-personal-data",
  "allowed_roles": [
    "synthetic-reviewer"
  ],
  "restrictions": [
    "No operational use; not a real sharing approval"
  ],
  "retention_policy_ref": "urn:example:fixture-retention",
  "review_due": "2026-10-09",
  "onward_sharing": "requires-review"
}
```

Source: wigan-handover.json#/policies/0
SHA-256: e9b3102333966f90d76e847630b91e2664630b563af5fc7b25e0841c82c50ed6


---

# Example Child

Synthetic demonstration only.

Wholly fictional child, aged 27 months at the review.

## Source facts

```json
{
  "id": "child",
  "source_ref": "source-demo",
  "source_record_id": "fictional/child",
  "policy_ref": "policy-demo",
  "recorded_at": "2026-09-09T11:00:00Z",
  "assertion_status": "recorded",
  "person_key": "fictional-child",
  "date_of_birth": "2024-06-09",
  "birth_precision": "day"
}
```

Source: wigan-handover.json#/records/Person/0
SHA-256: e9b3102333966f90d76e847630b91e2664630b563af5fc7b25e0841c82c50ed6


---

# Example parent

Synthetic demonstration only.

Fictional parent. Parental responsibility is reported in the source, not independently verified.

## Source facts

```json
{
  "id": "parent",
  "source_ref": "source-demo",
  "source_record_id": "fictional/parent",
  "policy_ref": "policy-demo",
  "recorded_at": "2026-09-09T11:00:00Z",
  "assertion_status": "recorded",
  "person_key": "fictional-parent",
  "birth_precision": "unknown"
}
```

Source: wigan-handover.json#/records/Person/1
SHA-256: e9b3102333966f90d76e847630b91e2664630b563af5fc7b25e0841c82c50ed6


---

# Example nursery

Synthetic demonstration only.

Fictional sending setting and owner of leaflet dispatch.

## Source facts

```json
{
  "id": "nursery",
  "source_ref": "source-demo",
  "source_record_id": "fictional/nursery",
  "policy_ref": "policy-demo",
  "recorded_at": "2026-09-09T11:00:00Z",
  "assertion_status": "recorded",
  "name": "Example nursery — fictional",
  "type": {
    "system": "urn:example:ftk:concepts",
    "code": "early-years-setting",
    "display": "early years setting",
    "version": "demo-1"
  }
}
```

Source: wigan-handover.json#/records/Organisation/0
SHA-256: e9b3102333966f90d76e847630b91e2664630b563af5fc7b25e0841c82c50ed6


---

# Example health-visiting service

Synthetic demonstration only.

Fictional receiving service.

## Source facts

```json
{
  "id": "health-service",
  "source_ref": "source-demo",
  "source_record_id": "fictional/health-service",
  "policy_ref": "policy-demo",
  "recorded_at": "2026-09-09T11:00:00Z",
  "assertion_status": "recorded",
  "name": "Example health-visiting service — fictional",
  "type": {
    "system": "urn:example:ftk:concepts",
    "code": "health-visiting",
    "display": "health visiting",
    "version": "demo-1"
  }
}
```

Source: wigan-handover.json#/records/Organisation/1
SHA-256: e9b3102333966f90d76e847630b91e2664630b563af5fc7b25e0841c82c50ed6


---

# Example health visitor

Synthetic demonstration only.

Fictional owner of the agreed support discussion.

## Source facts

```json
{
  "id": "health-visitor",
  "source_ref": "source-demo",
  "source_record_id": "fictional/health-visitor",
  "policy_ref": "policy-demo",
  "recorded_at": "2026-09-09T11:00:00Z",
  "assertion_status": "recorded",
  "display_name": "Example health visitor (fictional)",
  "organisation_ref": "health-service",
  "role": {
    "system": "urn:example:ftk:concepts",
    "code": "health-visitor",
    "display": "health visitor",
    "version": "demo-1"
  }
}
```

Source: wigan-handover.json#/records/Practitioner/1
SHA-256: e9b3102333966f90d76e847630b91e2664630b563af5fc7b25e0841c82c50ed6


---

# Early-years progress check

Synthetic demonstration only.

Completed review on 9 September 2026. Completion of a review does not establish delivery of support.

## Source facts

```json
{
  "id": "ey-check",
  "source_ref": "source-demo",
  "source_record_id": "fictional/ey-check",
  "policy_ref": "policy-demo",
  "recorded_at": "2026-09-09T11:00:00Z",
  "assertion_status": "recorded",
  "person_ref": "child",
  "type": {
    "system": "urn:example:ftk:concepts",
    "code": "early-years-progress-check",
    "display": "early years progress check",
    "version": "demo-1"
  },
  "status": "completed",
  "completed_on": "2026-09-09",
  "expected_from": "2026-06-09",
  "expected_to": "2026-12-09",
  "age_months_at_review": 27,
  "age_basis": "chronological",
  "integration_method": "secure-digital",
  "shared_with_family": true,
  "field_states": [
    {
      "field": "shared_with_family_on",
      "reason": "not-recorded"
    }
  ]
}
```

Source: wigan-handover.json#/records/Assessment/0
SHA-256: e9b3102333966f90d76e847630b91e2664630b563af5fc7b25e0841c82c50ed6


---

# What matters to the family

Synthetic demonstration only.

Please help us agree what to try at home. This is a practitioner summary of a fictional parent priority.

## Source facts

```json
{
  "id": "family-priority",
  "source_ref": "source-demo",
  "source_record_id": "fictional/family-priority",
  "policy_ref": "policy-demo",
  "recorded_at": "2026-09-09T11:00:00Z",
  "assertion_status": "recorded",
  "person_ref": "child",
  "speaker_ref": "parent",
  "kind": "priority",
  "statement": "Please help us agree what to try at home.",
  "representation": "practitioner-summary",
  "captured_on": "2026-09-09"
}
```

Source: wigan-handover.json#/records/Voice/0
SHA-256: e9b3102333966f90d76e847630b91e2664630b563af5fc7b25e0841c82c50ed6


---

# Nursery to health-visiting handover

Synthetic demonstration only.

Recorded as received. Its next service action remains agreed, not completed.

## Source facts

```json
{
  "id": "handover",
  "source_ref": "source-demo",
  "source_record_id": "fictional/handover",
  "policy_ref": "policy-demo",
  "recorded_at": "2026-09-09T11:00:00Z",
  "assertion_status": "recorded",
  "person_ref": "child",
  "kind": "handover",
  "type": {
    "system": "urn:example:ftk:concepts",
    "code": "age-two-review-handover",
    "display": "age two review handover",
    "version": "demo-1"
  },
  "sender_ref": "nursery",
  "recipient_ref": "health-service",
  "status": "received",
  "sent_at": "2026-09-09T09:00:00Z",
  "received_at": "2026-09-09T10:00:00Z",
  "receipt_reference": "SYNTHETIC-RECEIPT-001",
  "next_action_ref": "discuss-support"
}
```

Source: wigan-handover.json#/records/Referral/0
SHA-256: e9b3102333966f90d76e847630b91e2664630b563af5fc7b25e0841c82c50ed6


---

# Discuss a support option

Synthetic demonstration only.

Agreed discussion, owned by the Example health visitor, due 16 September 2026.

## Source facts

```json
{
  "id": "discuss-support",
  "source_ref": "source-demo",
  "source_record_id": "fictional/discuss-support",
  "policy_ref": "policy-demo",
  "recorded_at": "2026-09-09T11:00:00Z",
  "assertion_status": "recorded",
  "person_ref": "child",
  "referral_ref": "handover",
  "description": "Discuss an appropriate support option with the family",
  "owner_ref": "health-visitor",
  "status": "agreed",
  "due_on": "2026-09-16"
}
```

Source: wigan-handover.json#/records/Action/0
SHA-256: e9b3102333966f90d76e847630b91e2664630b563af5fc7b25e0841c82c50ed6


---

# Send an information leaflet

Synthetic demonstration only.

Completed leaflet dispatch. It does not establish support received.

## Source facts

```json
{
  "id": "send-information",
  "source_ref": "source-demo",
  "source_record_id": "fictional/send-information",
  "policy_ref": "policy-demo",
  "recorded_at": "2026-09-09T11:00:00Z",
  "assertion_status": "recorded",
  "person_ref": "child",
  "description": "Send the requested information leaflet",
  "owner_ref": "nursery",
  "status": "completed",
  "completed_at": "2026-09-09T10:30:00Z",
  "completion_evidence_refs": [
    "leaflet-sent"
  ]
}
```

Source: wigan-handover.json#/records/Action/1
SHA-256: e9b3102333966f90d76e847630b91e2664630b563af5fc7b25e0841c82c50ed6


---

# Leaflet dispatch evidence

Synthetic demonstration only.

Recorded dispatch event. Support receipt is not evidenced.

## Source facts

```json
{
  "id": "leaflet-sent",
  "source_ref": "source-demo",
  "source_record_id": "fictional/leaflet-sent",
  "policy_ref": "policy-demo",
  "recorded_at": "2026-09-09T11:00:00Z",
  "assertion_status": "recorded",
  "person_ref": "child",
  "type": {
    "system": "urn:example:ftk:concepts",
    "code": "information-sent",
    "display": "information sent",
    "version": "demo-1"
  },
  "occurred_on": "2026-09-09",
  "occurred_at": "2026-09-09T10:30:00Z",
  "status": "occurred",
  "summary": "Only leaflet dispatch is complete; support receipt is not evidenced."
}
```

Source: wigan-handover.json#/records/Event/0
SHA-256: e9b3102333966f90d76e847630b91e2664630b563af5fc7b25e0841c82c50ed6


---

# Try the agreed activity

Synthetic demonstration only.

Agreed parent activity. No due date or completion is recorded.

## Source facts

```json
{
  "id": "parent-activity",
  "source_ref": "source-demo",
  "source_record_id": "fictional/parent-activity",
  "policy_ref": "policy-demo",
  "recorded_at": "2026-09-09T11:00:00Z",
  "assertion_status": "recorded",
  "person_ref": "child",
  "description": "Try the activity agreed with the key person",
  "owner_ref": "parent",
  "status": "agreed"
}
```

Source: wigan-handover.json#/records/Action/2
SHA-256: e9b3102333966f90d76e847630b91e2664630b563af5fc7b25e0841c82c50ed6


# Directed relationships

- practitioner/health-visitor [works for] organisation/health-service; source json-pointer:/records/Practitioner/1/organisation_ref; assertion https://example.invalid/ftk/handover/assertion/93a6ae10b226824de649aa32
- review/progress-check [is about] person/child; source json-pointer:/records/Assessment/0/person_ref; assertion https://example.invalid/ftk/handover/assertion/0948f6fdc45dba5cd48c7edf
- voice/family-priority [is about] person/child; source json-pointer:/records/Voice/0/person_ref; assertion https://example.invalid/ftk/handover/assertion/02b9e6012e0d7b2dac0ec7dd
- voice/family-priority [is attributed to] person/parent; source json-pointer:/records/Voice/0/speaker_ref; assertion https://example.invalid/ftk/handover/assertion/6ae146d71db1e3a5ef6e07f4
- handover/nursery-to-health [is about] person/child; source json-pointer:/records/Referral/0/person_ref; assertion https://example.invalid/ftk/handover/assertion/807e16361cad29f5950740d8
- handover/nursery-to-health [was sent by] organisation/nursery; source json-pointer:/records/Referral/0/sender_ref; assertion https://example.invalid/ftk/handover/assertion/62226a5a1365c16263a69374
- handover/nursery-to-health [has recorded recipient] organisation/health-service; source json-pointer:/records/Referral/0/recipient_ref; assertion https://example.invalid/ftk/handover/assertion/db9c5706b7fcba597713a336
- handover/nursery-to-health [has next action] action/discuss-support; source json-pointer:/records/Referral/0/next_action_ref; assertion https://example.invalid/ftk/handover/assertion/9c73c5fc398064edeb796ea5
- action/discuss-support [is about] person/child; source json-pointer:/records/Action/0/person_ref; assertion https://example.invalid/ftk/handover/assertion/f5eafcf40f665d2574b48b45
- action/discuss-support [is owned by] practitioner/health-visitor; source json-pointer:/records/Action/0/owner_ref; assertion https://example.invalid/ftk/handover/assertion/8de6f5502189c102c770003e
- action/discuss-support [follows handover] handover/nursery-to-health; source json-pointer:/records/Action/0/referral_ref; assertion https://example.invalid/ftk/handover/assertion/1ae5fa9d908de6b2d5dad75e
- action/send-information [is about] person/child; source json-pointer:/records/Action/1/person_ref; assertion https://example.invalid/ftk/handover/assertion/b78c250a503ff9737418b6db
- action/send-information [is owned by] organisation/nursery; source json-pointer:/records/Action/1/owner_ref; assertion https://example.invalid/ftk/handover/assertion/8a0d7f568e2ef91424fd9f6b
- action/send-information [cites completion evidence] event/leaflet-sent; source json-pointer:/records/Action/1/completion_evidence_refs/0; assertion https://example.invalid/ftk/handover/assertion/38ef63c801972231446f7ea2
- event/leaflet-sent [is about] person/child; source json-pointer:/records/Event/0/person_ref; assertion https://example.invalid/ftk/handover/assertion/428a0b9b884aaad454124723
- action/parent-activity [is about] person/child; source json-pointer:/records/Action/2/person_ref; assertion https://example.invalid/ftk/handover/assertion/82d6cffca041d5555ab819b8
- action/parent-activity [is owned by] person/parent; source json-pointer:/records/Action/2/owner_ref; assertion https://example.invalid/ftk/handover/assertion/b03575cb9b0251f6f9d132cb

# Comparison boundary
The existing Bristol and Wigan examples are locality-labelled variants of the same fictional scenario. This comparison does not demonstrate real adapters or council interoperability.