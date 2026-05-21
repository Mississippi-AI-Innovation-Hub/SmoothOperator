# Testing and Evaluation Notes

## Hub-ITS-Triage-Agent | AWS AI Innovation Hub PoC

---

## Testing Approach

Testing was conducted in two phases:

1. **Lambda unit testing** — Direct Lambda test events via the AWS console to validate AI routing logic independently of the phone system
2. **End-to-end call testing** — Live phone calls to +1 (866) 777-4471 to validate the full pipeline from caller speech to routed response

All test calls were made by the development team using personal devices. No real citizen data was used.

---

## Success Metrics (from original PoC scope)

| Metric | Target | Result |
|---|---|---|
| Routing accuracy on test scenarios | ≥ 85% | **100%** (50+ test calls) |
| Call logging completeness | 100% of calls logged | **100%** |
| Confidence score on successful routes | ≥ 0.75 | **0.95–0.99 average** |
| Human fallback on ambiguous input | Required | **Confirmed** |
| System stability during variable testing | Stable | **Stable** |

---

## Lambda Unit Test Results

### Test Method
Direct Lambda invocation via AWS Console test events using the following payload format:

```json
{
  "caller_input": "I need help with child support payments"
}
```

### Results

| Input | Expected Agency | Actual Agency | Confidence | Correct |
|---|---|---|---|---|
| I need help with child support payments | MDHS | MDHS (Child Support) | 0.99 | ✅ |
| I lost my job and need unemployment help | MDES | MDES (Unemployment) | 0.95 | ✅ |
| I need to renew my drivers license | DPS | DPS (Driver's License) | 0.99 | ✅ |
| I have a question about my taxes | Dept of Revenue | Dept of Revenue | 0.99 | ✅ |
| I need help with Medicaid | Division of Medicaid | Division of Medicaid | 0.99 | ✅ |
| I have no idea what I need help with | Human fallback | General Info (fallback) | 0.65 | ✅ |
| I need food stamps | MDHS | MDHS (SNAP Benefits) | 0.99 | ✅ |
| I need mental health help | DMH | DMH (Mental Health) | 0.97 | ✅ |
| I need to report child abuse | MDCPS | MDCPS (Child Protection) | 0.98 | ✅ |
| I have an insurance complaint | MID | MID (Dept of Insurance) | 0.99 | ✅ |

---

## End-to-End Call Test Results

### Intent Coverage Test

All 16 Lex intents were tested via live phone calls. Each test called +1 (866) 777-4471 and spoke the test phrase naturally.

| Intent | Test Phrase | Result |
|---|---|---|
| ChildSupport | "I need help with child support" | ✅ Routed to MDHS |
| Unemployment | "I lost my job" | ✅ Routed to MDES |
| DriversLicense | "I need to renew my drivers license" | ✅ Routed to DPS |
| Medicaid | "I need help with Medicaid" | ✅ Routed to Division of Medicaid |
| HumanOperator | "I need to speak to someone" | ✅ Human transfer message |
| Emergency | "this is an emergency" | ✅ 911 advisory played |
| FoodStamps | "I need food assistance" | ✅ Routed to MDHS SNAP |
| MentalHealth | "I need mental health help" | ✅ Routed to DMH |
| ChildWelfare | "I need to report child abuse" | ✅ Routed to MDCPS |
| Insurance | "I have an insurance question" | ✅ Routed to MID |
| Education | "I have a school question" | ✅ Routed to MDE |
| Veterans | "I need veterans help" | ✅ Routed to Veterans Affairs |
| PublicHealth | "I need a birth certificate" | ✅ Routed to MSDH |
| Transportation | "I have a road question" | ✅ Routed to MDOT |
| GovernmentOffice | "I need to reach the governor" | ✅ Routed to Governor's Office |
| PoisonControl | "poison control" | ✅ Routed to Poison Control |

### Confidence Threshold Test

| Test | Input | Confidence | Fallback Triggered |
|---|---|---|---|
| Ambiguous input | "I have no idea what I need" | 0.65 | ✅ Yes — human fallback |
| Very unclear | "umm I don't know" | 0.60 | ✅ Yes — human fallback |
| Clear intent | "child support" | 0.99 | ❌ No — routed correctly |

### Emergency Detection Test

| Test Phrase | Expected | Result |
|---|---|---|
| "this is an emergency" | 911 advisory | ✅ Correct |
| "I am in danger" | 911 advisory | ✅ Correct |
| "someone is hurt" | 911 advisory | ✅ Correct |
| "call 911" | 911 advisory | ✅ Correct |

### After-Hours Detection Test

Tested by temporarily adjusting the business hours check in Lambda to simulate off-hours:

| Scenario | Expected Message | Result |
|---|---|---|
| After 5PM CST | "Our offices are currently closed..." | ✅ Correct |
| Before 8AM CST | "Our offices are currently closed..." | ✅ Correct |
| Weekend | "Our offices are currently closed..." | ✅ Correct |
| Business hours | Normal routing message | ✅ Correct |

### Live Transfer Test

| Test | Input | Result |
|---|---|---|
| Press 1 to transfer | "I need child support" → press 1 | ✅ Live transfer to MDHS line initiated |
| Hang up instead | "I need child support" → hang up | ✅ Call ended cleanly |
| Timeout (no press) | "I need child support" → wait 5s | ✅ Goodbye message + disconnect |

---

## DynamoDB Audit Log Verification

After each test session, DynamoDB records were inspected to confirm logging completeness.

Sample DynamoDB record:

```json
{
  "call_id": "7a9afc35-6caa-4024-a500-69069efc3b37",
  "timestamp": "2026-04-17T04:28:51.211380",
  "caller_input": "I need help with child support payments",
  "routed_agency": "MDHS (Child Support)",
  "phone": "877-882-4916",
  "confidence": "0.99",
  "fallback_to_human": "False",
  "status": "success",
  "verified": "null",
  "correct": "null"
}
```

All 50+ test calls were successfully logged with complete field coverage.

---

## Running Lambda Tests Locally

To run a Lambda test event directly in the AWS console:

1. Go to Lambda → **ITS-Triage-Agent** → **Test** tab
2. Create a new test event with one of the following payloads:

```json
// Child Support
{ "caller_input": "I need help with child support payments" }

// Unemployment
{ "caller_input": "I lost my job and need unemployment help" }

// Emergency (will return 911 advisory)
{ "caller_input": "EMERGENCY" }

// Human Operator
{ "caller_input": "HumanOperator" }

// Ambiguous (will trigger fallback)
{ "caller_input": "I have no idea what I need help with" }
```

See `tests/test-events/sample-lambda-events.json` for the full set of test payloads.

---

## Known Test Limitations

- All testing was performed by the development team — no external user validation was conducted
- Load testing was not performed; concurrent call performance is untested
- Lex intent recognition was validated on clean speech from a quiet environment; real-world background noise was not tested
- SMS delivery was not testable due to SNS sandbox restrictions on the fellowship account
- Test calls used the developer's personal phone number — no anonymous caller testing was conducted
