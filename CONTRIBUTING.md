# Contributing

Corrections and focused improvements are welcome. Please keep contributions practical, technically supportable and within the repository's IT operations scope.

## Before proposing a change

- reproduce or verify the behaviour being documented;
- distinguish general guidance from vendor- or distribution-specific behaviour;
- put safe, read-only checks before actions that change state;
- include a way to validate recovery after a corrective action;
- avoid credentials, customer details, unique device identifiers and private network information;
- keep examples synthetic unless the underlying evidence is safe to publish.

Scripts should use the standard library or built-in shell facilities where practical. They must validate input, bound network operations with timeouts, report useful failures and remain read-only by default.

Use lowercase, hyphenated names for Markdown files. Keep a change narrow enough to review and update any local README that links to renamed or added material.
