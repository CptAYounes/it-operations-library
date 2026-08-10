# Patching checklist

Use with the organisation's change and vendor procedures. A checked box records a decision or result; it does not grant permission to make the change.

## Define the change

- [ ] Identify the systems, software, current versions and target versions.
- [ ] Read the vendor release notes, prerequisites and known issues.
- [ ] Determine security severity, operational urgency and exposure.
- [ ] Check application, driver, firmware and cluster compatibility.
- [ ] Identify dependencies, service owners and user impact.
- [ ] Confirm the maintenance window and change authority.

## Prepare

- [ ] Record a pre-change health baseline and any existing alarms.
- [ ] Confirm monitoring, console or out-of-band access is available.
- [ ] Verify the relevant backup and its most recent restore-test status.
- [ ] Obtain the update from an approved source and verify integrity where a digest or signature is provided.
- [ ] Confirm sufficient storage, power stability and expected restart time.
- [ ] Define validation checks, backout trigger, decision owner and recovery steps.
- [ ] Notify affected people through the approved channel.
- [ ] Pause if another active fault or change makes the starting state unclear.

## Apply

- [ ] Reconfirm scope and go/no-go conditions at the start of the window.
- [ ] Follow the vendor-supported sequence; do not combine unrelated changes.
- [ ] Record start time, operator, versions and significant output.
- [ ] Watch for installation errors, unexpected restarts and dependency failures.
- [ ] Stop at the agreed trigger rather than improvising on an impaired system.

## Validate

- [ ] Confirm the system booted or the service returned to its intended state.
- [ ] Verify installed versions and update history.
- [ ] Test the service from the user or dependent-system perspective, not only process state.
- [ ] Check logs, monitoring, storage and resource use for new warnings.
- [ ] Confirm redundancy or cluster members are restored to normal state.
- [ ] Observe for the agreed period and compare with the baseline.
- [ ] If backed out, validate the recovered version and service just as carefully.

## Close

- [ ] Record outcome, evidence, downtime and any deviations from plan.
- [ ] Re-enable paused automation or alerting and verify it is active.
- [ ] Notify stakeholders of success, backout or remaining risk.
- [ ] Assign follow-up work for failures, exceptions or documentation changes.
