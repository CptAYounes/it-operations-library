# Technical documentation standards

Operational documentation should help a reader make a safe decision or reproduce a result. Its quality is measured by use, not length.

## State purpose and boundary

A document should make clear:

- the question or condition it addresses;
- intended platform/version and audience;
- prerequisites, access and authority;
- actions that can interrupt service, change security or risk data;
- vendor/local-policy areas that cannot be universal;
- expected result, validation and escalation point.

Use neutral wording for study or lab procedures. Do not imply customer, production or enterprise experience that the evidence does not support.

## Write commands as controlled actions

Label the shell/OS and explain non-obvious options. Put read-only inspection before mutation. Use documentation ranges/names and synthetic identifiers in public examples. Never include credentials, tokens, product keys, complete private infrastructure, customer records or unredacted diagnostic output.

For a state-changing command, document:

1. what it changes and scope;
2. required authority and prerequisites;
3. backup/recovery or rollback;
4. expected output/state;
5. stop conditions;
6. post-change validation.

Do not present a destructive one-liner as a casual shortcut.

## Preserve diagnostic reasoning

Separate reported symptom, direct observation, hypothesis, action and confirmed cause. Add timestamps/timezones where sequence matters. Record failed checks; they prevent repeated work. State uncertainty rather than forcing a clean narrative.

## Structure by task

- a **reference** can use tables and short explanations;
- a **procedure** needs ordered steps and validation;
- a **runbook** should be concise under pressure with escalation;
- a **checklist** contains independently verifiable items;
- a **template** captures evidence without pre-filling a conclusion.

Do not force every file into one outline or repeat the same explanation across sections; link to the deeper source.

## Review and maintenance

Verify commands on the stated platform where practical, otherwise use authoritative vendor documentation and avoid a tested claim. Review links, versions, ownership and safety after changes. Remove conflicting obsolete advice rather than leaving several “final” versions.

A reviewer should ask: Is the starting state clear? Could the reader perform the check safely? Is success observable? Are claims and first-person experience truthful? Could the output leak information? Is there a point to stop and escalate?

Use meaningful Git history so corrections are traceable. A document with an unknown owner or stale dependency should be marked for review or removed; false confidence is worse than a visible gap.
