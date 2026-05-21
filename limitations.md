# Limitations and Disclaimer

## Hub-ITS-Triage-Agent | AWS AI Innovation Hub PoC

---

## Disclaimer

This repository contains code and supporting materials developed as part of a Mississippi Artificial Intelligence Innovation Hub Proof of Concept project. The contents are provided for prototype demonstration purposes. They are not production ready by default and may include simplified workflows, incomplete security guardrails, placeholder integrations, or reduced controls appropriate only for a Proof-of-Concept environment.

This code should not be used with production data or in production environments without additional architecture, security, privacy, testing, and stakeholder review.

---

## Known Limitations

### 1. Hardcoded Agency Directory
The Mississippi State Agency Directory is embedded as a string constant in the Lambda function (`AGENCY_DIRECTORY`). Any change to agency phone numbers, new agency additions, or organizational changes requires a Lambda code deployment. A production system should replace this with a managed, ITS-controlled knowledge base such as Amazon Kendra.

### 2. SNS SMS Delivery Not Functional in PoC Environment
The SMS follow-up feature is fully implemented in Lambda and verified via CloudWatch logs. However, the AWS fellowship account SNS configuration has sandbox restrictions that prevented live SMS delivery to end users during the PoC. Production deployment requires SNS production access approval from AWS.

### 3. AI Model Limitations (Nova Micro)
Amazon Nova Micro was the only Bedrock model available within the fellowship account's Service Control Policy restrictions. Nova Micro is a smaller, faster model optimized for speed rather than nuanced reasoning. A more capable model such as Claude Haiku or Claude Sonnet would produce more consistent structured JSON output and handle ambiguous or multi-topic caller inputs more reliably. Nova Micro occasionally returns malformed JSON — mitigated in this PoC by a 3-attempt retry loop with robust JSON extraction.

### 4. Max Retry Counter Not Fully Implemented
A 3-strike human transfer (after 3 failed recognition attempts, route to human operator) was designed and partially implemented. Amazon Connect does not natively persist counters across Lambda invocations within the same call session without additional infrastructure (e.g., ElastiCache session store or DynamoDB session table). The retry loop exists in the Connect flow but the strike counter was not reliably persisted across invocations.

### 5. English-Only Support
The system only supports English-language callers. Spanish-speaking or non-English-speaking callers will not be correctly routed. Adding multi-language support would require Amazon Translate integration before the Lex intent classification step.

### 6. No Load Testing
The system has not been tested under concurrent call volume. Performance, Lambda concurrency limits, Bedrock throttling behavior, and DynamoDB write capacity under high load are untested. Load testing is required before any pilot or expanded access.

### 7. PII in Call Logs
Caller phone numbers are captured from the Amazon Connect contact data object and used for SMS follow-up. These are logged in Lambda print statements (CloudWatch) but are not persisted to DynamoDB call logs in the current implementation. A production deployment would require a formal privacy review, PII minimization assessment, and data retention policy aligned with state data governance frameworks.

### 8. Cross-Region Architecture
Amazon Connect was deployed in us-west-2 (Oregon) while all other services are in us-east-1 (N. Virginia), due to fellowship account configuration. This cross-region setup introduced debugging complexity and may introduce latency in production. A fully co-located deployment in a single region is recommended for production.

### 9. No Authentication or Authorization
The system accepts all inbound calls without caller authentication or identity verification. Any caller can invoke the system. There is no mechanism to detect or block robocalls, spam calls, or malicious inputs. A production deployment should evaluate appropriate safeguards.

### 10. Live Transfer Limitations
The live call transfer feature routes callers to real agency phone numbers. There is no confirmation that the agency line is operational, staffed, or has capacity. If an agency line is busy, out of service, or has changed, callers will encounter the agency's own voicemail or busy signal. The system does not handle transfer failure gracefully beyond the Connect flow's built-in error paths.

### 11. No Web Interface or Admin Panel
There is no administrative dashboard, agency directory update interface, or call log review tool included in this PoC. ITS staff would need direct AWS console access to review DynamoDB logs or update the Lambda function. A production deployment should include an admin interface for directory management and Human-in-the-Loop review.

### 12. Synthetic Lex Training Data
All Lex intent utterances were created synthetically by the development team. No real ITS call transcripts were used for training. Real caller speech patterns, regional dialect, and edge-case phrasings may not be fully represented in the current utterance set. Accuracy on real production calls may differ from PoC test results.

---

## Production Readiness Requirements

Before this system could be considered for production deployment, the following reviews and improvements would be required at minimum:

| Area | Requirement |
|---|---|
| Security | Full cybersecurity review including IAM policy audit, network security, and penetration testing |
| Privacy | PII handling review, data retention policy, and alignment with state data governance framework |
| Accessibility | Review against accessibility standards for voice systems |
| Performance | Load testing, concurrency planning, and Bedrock throttling limits assessment |
| Reliability | Replace Nova Micro with a more capable model; add circuit breakers and dead-letter queues |
| Maintainability | Replace hardcoded directory with Amazon Kendra; build admin update interface |
| Support Ownership | Define ITS operational ownership, escalation procedures, and incident response |
| Governance | Agency stakeholder sign-off, legal review of automated routing of citizen calls |
| Integration | Define integration path with existing ITS telephony infrastructure and operator workflows |
| Testing | External user testing, accessibility testing, and UAT with ITS operator staff |
