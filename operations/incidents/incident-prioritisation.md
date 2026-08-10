# Incident prioritisation

Priority decides coordination, response urgency and communication. It should reflect current impact and time sensitivity, not the technical novelty of the fault or the seniority of the reporter.

## Assess impact

Consider:

- number and type of users/services affected;
- complete loss, severe degradation or reduced redundancy;
- critical function unavailable;
- data integrity, confidentiality or safety risk;
- geographical or dependency spread;
- financial, contractual or regulatory consequence under local policy;
- availability of a tested workaround.

## Assess urgency

Urgency rises when impact is growing, a deadline or recovery window is approaching, redundancy has been lost, a workaround is fragile, or delay will make recovery/data loss worse. A low current user count can still be urgent before a peak period or backup/retention boundary.

## Example decision model

Local definitions take precedence, but a model might look like this:

| Priority | Working description | Response behaviour |
|---|---|---|
| Critical | Widespread critical service loss; safety/security/data risk; or no safe redundancy with imminent impact | Immediate coordination, senior/owner escalation and frequent updates |
| High | Material service impact, multiple users/systems or unstable workaround | Prompt owner response and active incident management |
| Medium | Limited impact or degradation with a stable workaround | Scheduled active investigation and normal updates |
| Low | Minor issue, informational defect or no present service impact | Queue and plan without displacing higher-impact work |

These are not service-level promises and should not be copied into an organisation without agreed definitions.

## Avoid common distortions

- A noisy alert is not automatically high impact.
- A single executive user should not silently replace the agreed impact model; handle business criticality explicitly.
- “Server down” can describe a redundant node with no service impact or the only host for a critical function.
- A security concern may require a separate priority/escalation path even when availability is normal.
- A long-running incident should not remain at its original priority if impact expands or stabilises.

## Record the basis

Write a short, factual reason:

> High: checkout requests are failing for all test transactions in two regions; no working path is confirmed and error rate is still increasing.

Include evidence time and assumptions. Reassess after scope, workaround, redundancy or risk changes, and record who changed priority and why. Priority can decrease after stable mitigation while root-cause work continues, provided remaining risk has clear ownership.
