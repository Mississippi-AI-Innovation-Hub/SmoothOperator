# Changelog

All notable changes to the Hub-ITS-Triage-Agent PoC are documented here.

---

## [1.0.0] — April 27, 2026 — Final PoC Release

### Added
- Full end-to-end serverless voice AI call triage pipeline on AWS
- Amazon Connect contact flow (ITS-Triage-Flow) with toll-free number +1 (866) 777-4471
- Amazon Lex v2 bot (ITSTriageBot) with 16 intent categories and 10+ utterances per intent
- AWS Lambda function (ITS-Triage-Agent) in Python 3.12
- Amazon Bedrock (Nova Micro) integration for real-time intent classification and agency routing
- Full 2025–2026 Mississippi State Government Telephone Directory as Lambda knowledge base
- Amazon DynamoDB table (its-triage-calls) with full audit logging schema including verified/correct feedback fields
- Amazon Polly (Danielle Neural) voice response with digit-by-digit phone number pronunciation
- Live agency call transfer — caller presses 1 to be transferred to the real agency number
- Emergency keyword detection with immediate 911 advisory
- After-hours detection with CST business hours awareness and direct agency number messaging
- Amazon SNS SMS follow-up (implemented; blocked by sandbox restrictions)
- Human-in-the-Loop feedback architecture for supervised AI improvement
- Retry loop — re-prompts caller on unclear input before falling back to human operator
- Confidence threshold system — calls below 0.75 confidence routed to human fallback
- 3-attempt retry logic with robust JSON extraction for Nova Micro response reliability
- format_phone() — digit-by-digit phone number formatting for Polly TTS
- e164_phone() — E.164 format conversion for live call transfer

### Intent Categories (16 total)
ChildSupport, Unemployment, DriversLicense, Medicaid, HumanOperator, Emergency,
FoodStamps, MentalHealth, ChildWelfare, Insurance, Education, Veterans,
PublicHealth, Transportation, GovernmentOffice, PoisonControl

---

## [0.3.0] — April 20, 2026

### Added
- Amazon Lex free speech recognition replacing DTMF button menu
- 11 initial Lex intents with sample utterances
- Lex fulfillment disabled (Connect handles Lambda invocation directly)
- Hold prompt ("One moment please") before Lambda processing
- Wait block (3 seconds) to prevent audio cutoff

### Fixed
- Double-invocation bug — Lex fulfillment + Connect both calling Lambda causing garbled audio
- Lambda invocation timeout in Connect increased from 3s to 8s to accommodate Bedrock response time
- Cross-region Connect (us-west-2) → Lambda (us-east-1) resource policy updated with specific Connect instance ARN

---

## [0.2.0] — April 17, 2026

### Added
- Amazon Connect contact flow wired to Lambda
- DTMF menu (press 1-4, 0) as initial call routing method
- DynamoDB table (its-triage-calls) with call logging
- Set contact attributes blocks for DTMF digit passing
- Retry/error loop for unclear input
- Goodbye prompt and disconnect flow

### Fixed
- SCP region restriction resolved — all services moved to us-east-1
- Lambda resource policy updated to allow Amazon Connect invocation
- DTMF digit not passed to Lambda — fixed via Set contact attributes blocks
- Nova Micro JSON parse failures — added start/end JSON extraction and retry loop

---

## [0.1.0] — April 10, 2026

### Added
- Initial AWS Lambda function (ITS-Triage-Agent) in Python 3.12
- Amazon Bedrock (Nova Micro) integration for intent classification
- Basic Mississippi agency directory (10 agencies)
- DynamoDB table creation (its-triage-calls)
- Initial test event validation — 100% accuracy on 5 test scenarios
- AmazonBedrockFullAccess and AmazonDynamoDBFullAccess IAM policies attached to Lambda role
- Amazon Connect instance created with toll-free number

### Notes
- Initial deployment in us-east-2 blocked by AWS Service Control Policy
- Migrated to us-east-1 after Hub confirmation of approved region
