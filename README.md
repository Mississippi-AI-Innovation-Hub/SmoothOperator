# Hub-ITS-Triage-Agent

**Mississippi AI Innovation Hub | AWS Fellowship PoC**
**Agency Partner:** Mississippi Department of Information Technology Services (ITS)
**Developer:** Aditya (Adi) Singh — Mississippi State University, Computer Science
**Fellowship Period:** April 6 – April 27, 2026

---

## Overview

This repository contains the code and documentation for an AI Innovation Hub Proof of Concept focused on automating the Mississippi State Government Operator call triage process. The PoC was developed to explore whether an AI-enabled voice agent could help ITS by automatically classifying inbound citizen caller intent and routing callers to the correct Mississippi state agency — without manual operator intervention.

The project demonstrates feasibility within a limited prototype environment and is not a production-ready solution.

> **Try the live demo:** Call **+1 (866) 777-4471** and speak naturally — say what you need and the AI will route you to the correct Mississippi state agency.

---

## Agency Problem

The Mississippi ITS State Government Operator line receives thousands of routine inbound calls from citizens who need help reaching the right state agency. Today, every call is handled manually by ITS operator staff — creating unpredictable workload spikes, limiting availability to business hours, and introducing inconsistency in routing accuracy.

This PoC demonstrates that an AI-powered voice agent can handle routine triage calls automatically, 24 hours a day, 7 days a week, with full auditability.

---

## PoC Scope and Demonstrated Capabilities

| Capability | Status |
|---|---|
| Natural language intent classification (16 intent categories) | ✅ Demonstrated |
| AI-powered agency routing via Amazon Bedrock | ✅ Demonstrated — 100% accuracy on test calls |
| Voice response delivery (digit-by-digit phone number) | ✅ Demonstrated |
| Live agency call transfer (press 1 to connect) | ✅ Demonstrated |
| Emergency keyword detection → 911 advisory | ✅ Demonstrated |
| After-hours detection with business hours messaging | ✅ Demonstrated |
| Full call audit logging to DynamoDB | ✅ Demonstrated — 165+ calls logged |
| Retry loop on unclear input | ✅ Demonstrated |
| Confidence threshold fallback to human operator | ✅ Demonstrated |
| Human-in-the-Loop feedback architecture | ✅ Demonstrated |
| Few-shot feedback loop (verified calls improve AI prompt) | ✅ Demonstrated |
| QuickSight analytics dashboard | ✅ Demonstrated — 165 calls visualized |
| EventBridge auto-refresh (hourly dashboard updates) | ✅ Demonstrated |
| SMS follow-up via AWS End User Messaging | ⚠️ Implemented — toll-free number registered (+1 888-861-6097), pending AWS carrier activation |

---

## Architecture Overview

```
Caller
  └─▶ Amazon Connect (+1 866-777-4471) [us-west-2]
        └─▶ Amazon Lex v2 — ITSTriageBot [us-east-1]
              └─▶ AWS Lambda — ITS-Triage-Agent (Python 3.12) [us-east-1]
                    ├─▶ Amazon Bedrock — Nova Micro (intent classification + routing)
                    ├─▶ Amazon DynamoDB — its-triage-calls (call logging)
                    └─▶ AWS End User Messaging SMS (follow-up text to caller)
              └─▶ Amazon Polly — Danielle Neural (voice response)
                    └─▶ Caller / Optional Live Transfer to Agency

Dashboard Pipeline:
DynamoDB → its-triage-export Lambda → S3 (its-triage-dashboard-data) → Amazon QuickSight
EventBridge (hourly) → triggers export Lambda automatically
```

All services deployed in AWS us-east-1 (N. Virginia) except Amazon Connect (us-west-2) per fellowship account configuration.

---

## Repository Structure

```
Hub-ITS-Triage-Agent/
├── README.md
├── LICENSE
├── .gitignore
├── .env.example
├── CHANGELOG.md
├── src/
│   ├── lambda_function.py              # Main Lambda: routing logic, Bedrock, DynamoDB, SNS
│   ├── lambda_export.py                # Export Lambda: DynamoDB → S3 CSV for QuickSight
│   └── connect_flow/
│       └── ITS-Triage-Flow.json        # Amazon Connect contact flow export
├── docs/
│   ├── architecture.md                 # Detailed architecture documentation
│   ├── setup.md                        # Setup and deployment instructions
│   ├── testing.md                      # Testing approach and results
│   ├── data-notes.md                   # Data sources and governance notes
│   ├── limitations.md                  # Known issues and limitations
│   └── images/                         # Architecture diagrams and screenshots
├── data/
│   └── sample/
│       └── agency-directory.md         # Sample agency directory structure (no real PII)
├── demos/
│   └── sample-prompts/
│       └── test-utterances.md          # Sample test utterances for each intent
└── tests/
    └── test-events/
        └── sample-lambda-events.json   # Sample Lambda test event payloads
```

---

## Setup

See [docs/setup.md](docs/setup.md) for full setup and deployment instructions.

**Prerequisites:**
- AWS account with access to us-east-1 services
- Amazon Connect instance (us-west-2 recommended per fellowship configuration)
- Amazon Bedrock access (Nova Micro model — `amazon.nova-micro-v1:0`)
- Python 3.12
- AWS CLI configured with appropriate permissions

**Quick start:**
1. Clone this repository
2. Copy `.env.example` to `.env` and fill in your values
3. Deploy the Lambda function from `src/lambda_function.py`
4. Deploy the export Lambda from `src/lambda_export.py`
5. Import the contact flow from `src/connect_flow/ITS-Triage-Flow.json` into Amazon Connect
6. Claim a phone number and attach the flow
7. Create DynamoDB table `its-triage-calls` with partition key `call_id` (String)
8. Create S3 bucket `its-triage-dashboard-data` for QuickSight export

---

## Configuration

Copy `.env.example` to `.env` and supply your own values. See `.env.example` for required fields.

The system uses IAM role-based authentication for all AWS service calls. No Anthropic API key is required — Amazon Bedrock is invoked via IAM permissions.

**Required IAM policies for Lambda execution role:**
- `AmazonBedrockFullAccess`
- `AmazonDynamoDBFullAccess`
- `AmazonSNSFullAccess`
- `AmazonS3FullAccess`
- Inline policy for `sms-voice:SendTextMessage` on origination number ARN

---

## Data Notes

This repository does not include real citizen data. All test calls were made by the development team using personal devices. The agency directory embedded in the Lambda function is sourced from the publicly available 2025–2026 Mississippi State Government Telephone Directory published by ITS.

See [docs/data-notes.md](docs/data-notes.md) for full data governance notes.

---

## Usage

Call **+1 (866) 777-4471** to interact with the live PoC system, or invoke the Lambda function directly with a test event:

```json
{
  "caller_input": "I need help with child support"
}
```

**Supported intent categories (16 total):**

| Intent | Example Phrases |
|---|---|
| ChildSupport | "I need help with child support" |
| Unemployment | "I lost my job" |
| DriversLicense | "I need to renew my drivers license" |
| Medicaid | "I need help with Medicaid" |
| FoodStamps | "I need food assistance" |
| MentalHealth | "I need mental health help" |
| ChildWelfare | "I need to report child abuse" |
| Insurance | "I have an insurance complaint" |
| Education | "I have a school question" |
| Veterans | "I need veterans help" |
| PublicHealth | "I need a birth certificate" |
| Transportation | "I have a road question" |
| GovernmentOffice | "I need to reach the governor" |
| PoisonControl | "poison control" |
| HumanOperator | "I need to speak to someone" |
| Emergency | "this is an emergency" |

See `tests/test-events/sample-lambda-events.json` for full test payloads.

---

## Testing and Evaluation

- 165+ test calls made across all 16 intent categories
- **100% routing accuracy** observed on all test scenarios
- Confidence scores of **0.95–0.99** on successful routes
- Human fallback correctly triggered at confidence < 0.75
- Emergency detection confirmed across multiple distress phrases
- After-hours detection confirmed via off-hours test calls
- Live agency call transfer confirmed to MDHS line
- All calls logged to DynamoDB with full audit fields
- QuickSight dashboard visualizing all 165 call records

See [docs/testing.md](docs/testing.md) for detailed testing notes and full results tables.

---

## Key Design Decisions

| Decision | Rationale |
|---|---|
| Lex fulfillment disabled | Enabling Lex fulfillment AND Connect Lambda invocation caused double-invocation and garbled audio |
| Lambda timeout 8s in Connect | Default 3s caused silent failures; Bedrock calls require 2–4 seconds |
| Flat JSON return from Lambda | Amazon Connect requires flat key-value string map for dynamic Play prompts |
| format_phone() for Polly | Digit-by-digit formatting (e.g. `1. 877. 882. 4916`) is clearer for callers to write down |
| Human-in-the-Loop architecture | Verified correct calls feed back into AI prompt as few-shot examples — supervised improvement only |
| INTENT_MAP in Lambda | Lex passes intent names; Lambda maps to natural language phrases for Bedrock prompt |

---

## Limitations

This PoC was developed within a 3-week timeline and controlled AWS environment. Key limitations include:

- Agency directory is hardcoded in Lambda — requires code deployment to update
- SMS delivery pending — toll-free origination number (+1 888-861-6097) registered through AWS End User Messaging, awaiting carrier activation
- English-only — Spanish-speaking callers not supported
- No load testing performed
- Caller phone numbers logged as plaintext — production requires PII review
- Nova Micro model used due to fellowship SCP restrictions — a more capable model would improve consistency

See [docs/limitations.md](docs/limitations.md) for the full limitations list and production readiness requirements.

---

## Disclaimer

This repository contains code and supporting materials developed as part of a Mississippi Artificial Intelligence Innovation Hub Proof of Concept project. The contents are provided for prototype demonstration purposes. They are not production ready by default and may include simplified workflows, incomplete security guardrails, placeholder integrations, or reduced controls appropriate only for a Proof-of-Concept environment.

This code should not be used with production data or in production environments without additional architecture, security, privacy, testing, and stakeholder review.

---

## License

MIT License — see [LICENSE](LICENSE) for full terms.

---

## Contributors

**Aditya (Adi) Singh** — Mississippi State University, Computer Science
- GitHub: [@operator2036](https://github.com/operator2036)
- Email: as5142@msstate.edu
- Phone: 662-497-0736

**Fellowship Partners:** AWS Mississippi AI Innovation Hub | Mississippi Department of ITS | Mississippi Artificial Intelligence Network (MAIN)

**Fellowship Partners:** AWS Mississippi AI Innovation Hub | Mississippi Department of ITS | Mississippi Artificial Intelligence Network (MAIN)
