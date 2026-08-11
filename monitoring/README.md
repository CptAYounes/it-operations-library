# Monitoring

Monitoring turns system and service behaviour into evidence that can be acted on. This section concentrates on choosing useful signals, understanding normal behaviour and responding without treating an alert as a diagnosis.

- [What to monitor on a host](host-monitoring/what-to-monitor.md)
- [Thresholds and baselines](performance/thresholds-baselines.md)
- [Alert, fault and symptom](alerting/alert-fault-symptom.md)
- [Establishing normal behaviour](performance/normal-behaviour.md)
- [Log monitoring fundamentals](logs/log-monitoring-fundamentals.md)
- [Alert response workflow](alerting/alert-response-workflow.md)

A practical starting sequence is to define the user-visible service, select a small set of availability, error, latency and saturation signals, observe them across normal and busy periods, and then set an alert with an owner, safe first checks and a recovery test. Review noisy or unactionable alerts instead of teaching responders to ignore them. When an alert fires, preserve the time window and compare related signals before changing the monitored system.
