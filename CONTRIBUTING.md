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

Use lowercase, hyphenated names for Markdown files. Keep a change narrow enough to review and update any local README that links to new or renamed material.

## Check the result

Read the rendered Markdown as well as the source. A command block needs enough context to show its platform, privilege and whether it changes state. A runbook needs a recovery check and an escalation boundary; a checklist item needs an observable result.

Create an isolated environment and run the repository checks from the repository root:

```console
python3 -m venv .venv-validation
.venv-validation/bin/python -m pip install -r tests/requirements.txt
.venv-validation/bin/python tests/validate-repository.py
.venv-validation/bin/python tests/smoke-tools.py --strict
```

Strict smoke testing covers healthy, warning, malformed-data and timeout paths. It fails when a required test tool is unavailable. Before publication, inspect the complete diff for private data and run the maintained Gitleaks release gate against both the current files and Git history:

```console
.venv-validation/bin/python tests/validate-release.py --gitleaks /path/to/gitleaks
```

Examples in documentation and tests must be visibly synthetic. A mocked provider test checks decision logic, not native provider behaviour. Include the tested platform and any untested branch in the change description rather than broadening a claim from a parser or mock test alone.
