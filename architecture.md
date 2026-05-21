# Architecture Documentation

## Hub-ITS-Triage-Agent | AWS AI Innovation Hub PoC

---

## System Overview

The ITS Call Triage Agent is a fully serverless, voice-enabled AI pipeline built on AWS. It accepts inbound phone calls, classifies caller intent using natural language understanding, queries an authoritative agency knowledge base via AI, and routes callers to the correct Mississippi state agency — with an optional live call transfer.

All services are deployed in **AWS us-east-1 (N. Virginia)** except Amazon Connect which is hosted in **us-west-2 (Oregon)** per fellowship account configuration.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        CITIZEN CALLER                           │
└────────────────────────────┬────────────────────────────────────┘
                             │ Inbound call
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              AMAZON CONNECT  [us-west-2]                        │
│         Toll-Free Number: +1 (866) 777-4471                     │
│         Contact Flow: ITS-Triage-Flow                           │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ 1. Set Voice (Danielle Neural)                           │   │
│  │ 2. Play Welcome Prompt                                   │   │
│  │ 3. Get Customer Input → Amazon Lex                       │   │
│  │ 4. Play Hold Message ("One moment please")               │   │
│  │ 5. Wait (3 seconds)                                      │   │
│  │ 6. Invoke Lambda Function                                │   │
│  │ 7. Play Routing Result (from Lambda response)            │   │
│  │ 8. Get Customer Input → Press 1 to Transfer              │   │
│  │ 9. Transfer to Phone Number OR Goodbye + Disconnect      │   │
│  └──────────────────────────────────────────────────────────┘   │
└────────┬───────────────────────────────────────────────┬────────┘
         │ Speech input                                  │ Transfer
         ▼                                               ▼
┌─────────────────────┐                    ┌─────────────────────┐
│   AMAZON LEX v2     │                    │   REAL AGENCY LINE  │
│   [us-east-1]       │                    │   (e.g. MDHS)       │
│   ITSTriageBot      │                    └─────────────────────┘
│   16 Intent         │
│   Categories        │
│   TestBotAlias      │
└──────────┬──────────┘
           │ Intent name passed to Connect
           │ Connect passes to Lambda via parameter
           ▼
┌─────────────────────────────────────────────────────────────────┐
│                  AWS LAMBDA  [us-east-1]                        │
│                  ITS-Triage-Agent (Python 3.12)                 │
│                  Memory: 256MB | Timeout: 60s                   │
│                                                                 │
│  Input: { "caller_input": "ChildSupport" }                      │
│                                                                 │
│  1. Map intent name → natural language phrase (INTENT_MAP)      │
│  2. Check business hours (CST = UTC-6)                          │
│  3. Build prompt with full agency directory                     │
│  4. Call Amazon Bedrock (Nova Micro) — up to 3 attempts         │
│  5. Parse structured JSON routing response                      │
│  6. Format phone number digit-by-digit                          │
│  7. Build description (business hours / after-hours variant)    │
│  8. Log call to DynamoDB                                        │
│  9. Send SMS via SNS                                            │
│  10. Return flat JSON to Connect                                │
│                                                                 │
│  Output: { description, agency, phone, phone_e164,              │
│            confidence, fallback }                               │
└────┬─────────────────────┬───────────────────────┬─────────────┘
     │                     │                       │
     ▼                     ▼                       ▼
┌──────────────┐  ┌────────────────────┐  ┌───────────────────┐
│ AMAZON       │  │ AMAZON DYNAMODB    │  │ AMAZON SNS        │
│ BEDROCK      │  │ [us-east-1]        │  │ [us-east-1]       │
│ [us-east-1]  │  │ its-triage-calls   │  │ SMS follow-up     │
│ Nova Micro   │  │                    │  │ to caller         │
│              │  │ Fields:            │  │                   │
│ Returns JSON:│  │ - call_id (UUID)   │  │ Message:          │
│ {            │  │ - timestamp        │  │ "Thank you for    │
│   agency,    │  │ - caller_input     │  │  calling MS Gov.  │
│   phone,     │  │ - routed_agency    │  │  You were         │
│   description│  │ - phone            │  │  connected to     │
│   confidence │  │ - confidence       │  │  [agency]..."     │
│   fallback   │  │ - fallback_to_human│  │                   │
│ }            │  │ - status           │  │ (Sandbox          │
│              │  │ - verified (null)  │  │  restricted in    │
└──────────────┘  │ - correct  (null)  │  │  PoC account)     │
                  └────────────────────┘  └───────────────────┘
```

---

## Component Details

### Amazon Connect (us-west-2)
- **Instance:** its-triage-agent
- **Phone number:** +1 (866) 777-4471 (toll-free)
- **Contact flow:** ITS-Triage-Flow (exported to `src/connect_flow/ITS-Triage-Flow.json`)
- **Voice:** Danielle (Neural) via Amazon Polly
- **Lambda invocation timeout:** 8 seconds (increased from default 3s)

### Amazon Lex v2 (us-east-1)
- **Bot:** ITSTriageBot
- **Alias:** TestBotAlias
- **Language:** English (US), Neural speech model
- **Confidence threshold:** 0.75
- **Intents:** 16 categories (see Lambda section)
- **Fulfillment:** Disabled — Connect handles Lambda invocation directly
- **Note:** Lex is linked to the us-east-1 Lex bot from the us-west-2 Connect instance via cross-region bot association

### AWS Lambda (us-east-1)
- **Function name:** ITS-Triage-Agent
- **Runtime:** Python 3.12
- **Memory:** 256 MB
- **Timeout:** 60 seconds
- **IAM role policies:** AmazonBedrockFullAccess, AmazonDynamoDBFullAccess, AmazonSNSFullAccess
- **Resource policy:** Allows `connect.amazonaws.com` with specific Connect instance ARN

### Amazon Bedrock — Nova Micro (us-east-1)
- **Model ID:** `amazon.nova-micro-v1:0`
- **Max tokens:** 400
- **Retry logic:** Up to 3 attempts on JSON parse failure
- **Knowledge base:** Full 2025–2026 Mississippi State Government Telephone Directory embedded in system prompt
- **Output:** Structured JSON `{ agency, phone, description, confidence, fallback_to_human }`

### Amazon DynamoDB (us-east-1)
- **Table:** its-triage-calls
- **Partition key:** call_id (String / UUID)
- **Billing:** On-demand
- **Encryption:** AWS-managed keys (default)

### Amazon SNS (us-east-1)
- **Topic:** its-triage-sms
- **SMS type:** Transactional
- **Status:** Implemented in Lambda; delivery blocked by fellowship account SNS sandbox restrictions

---

## Intent Categories (16 total)

| Intent Name | Maps To |
|---|---|
| ChildSupport | Child support payments and enforcement |
| Unemployment | Unemployment benefits and job loss |
| DriversLicense | Driver's license, vehicle tags, registration |
| Medicaid | Medicaid and health insurance assistance |
| HumanOperator | Live human operator transfer |
| Emergency | Emergency services — 911 advisory |
| FoodStamps | SNAP benefits and food assistance |
| MentalHealth | Mental health and substance abuse services |
| ChildWelfare | Child abuse reporting, foster care, adoption |
| Insurance | Insurance questions and consumer complaints |
| Education | Public schools and higher education |
| Veterans | Veterans benefits and military assistance |
| PublicHealth | Public health, vital records, health department |
| Transportation | Roads, highways, MDOT |
| GovernmentOffice | Elected officials and government offices |
| PoisonControl | Poison control emergency assistance |

---

## Data Flow Summary

1. Citizen calls +1 (866) 777-4471
2. Connect plays welcome prompt via Polly
3. Lex listens and classifies intent
4. Connect passes intent name to Lambda as `caller_input` parameter
5. Lambda maps intent name to natural language phrase
6. Lambda builds prompt with full agency directory and calls Bedrock
7. Bedrock returns structured JSON routing decision
8. Lambda logs call to DynamoDB, attempts SMS via SNS
9. Lambda returns flat JSON response to Connect
10. Connect reads `description` field via dynamic Play prompt (Polly)
11. Connect asks caller to press 1 for live transfer
12. On press 1: Connect reads `phone_e164` from contact attribute and initiates transfer

---

## IAM Architecture

```
Lambda Execution Role
  ├── AWSLambdaBasicExecutionRole (CloudWatch Logs)
  ├── AmazonBedrockFullAccess (Bedrock InvokeModel)
  ├── AmazonDynamoDBFullAccess (DynamoDB PutItem, UpdateItem)
  └── AmazonSNSFullAccess (SNS Publish)

Lambda Resource Policy
  └── connect.amazonaws.com (InvokeFunction)
      └── SourceArn: arn:aws:connect:us-west-2:568318158080:instance/[instance-id]

Lex Alias Resource Policy
  └── lambda.amazonaws.com (InvokeFunction)
      └── SourceArn: arn:aws:lambda:us-east-1:[account]:function:ITS-Triage-Agent
```

---

## Key Design Decisions

| Decision | Rationale |
|---|---|
| Lex fulfillment disabled | Enabling Lex fulfillment AND Connect Lambda invocation caused double-invocation, garbled audio, and unexpected flow behavior |
| Lambda timeout set to 8s in Connect | Default 3s timeout caused silent failures; Bedrock calls require 2–4 seconds |
| Nova Micro selected | Only Bedrock model available within fellowship account SCP restrictions |
| INTENT_MAP in Lambda | Lex passes intent names (e.g. "ChildSupport"); Lambda maps to natural language for Bedrock prompt |
| Flat JSON return from Lambda | Amazon Connect requires flat key-value string map; nested JSON is not readable by dynamic Play prompts |
| format_phone() for Polly | Bedrock returns phone numbers like "1-877-882-4916"; Polly reads digit groups better with ". " separators |
| e164_phone() for transfer | Amazon Connect requires E.164 format (+18778824916) for live call transfer |
