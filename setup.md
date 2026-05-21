# Setup and Deployment Guide

## Hub-ITS-Triage-Agent | AWS AI Innovation Hub PoC

---

## Prerequisites

- AWS account with access to **us-east-1** services (required due to SCP configuration)
- Amazon Connect instance in **us-west-2** (or your preferred region)
- Amazon Bedrock access enabled for `amazon.nova-micro-v1:0` in us-east-1
- Python 3.12
- AWS CLI configured with appropriate permissions

> **Note:** This PoC was developed under an AWS fellowship account with specific Service Control Policies (SCPs) restricting services to us-east-1. If your account has different restrictions, adjust region settings in the Lambda code accordingly.

---

## Step 1 — Create DynamoDB Table

1. Go to **DynamoDB** in the AWS console (us-east-1)
2. Click **Create table**
3. Fill in:
   - **Table name:** `its-triage-calls`
   - **Partition key:** `call_id` (String)
4. Leave all other settings as default
5. Click **Create table**

---

## Step 2 — Create Lambda Function

1. Go to **Lambda** in the AWS console (us-east-1)
2. Click **Create function** → **Author from scratch**
3. Fill in:
   - **Function name:** `ITS-Triage-Agent`
   - **Runtime:** Python 3.12
   - **Architecture:** x86_64
4. Click **Create function**
5. Under **Configuration** → **General configuration** → **Edit**:
   - **Timeout:** 60 seconds
   - **Memory:** 256 MB
6. Click **Save**

---

## Step 3 — Deploy Lambda Code

1. In the Lambda function, click the **Code** tab
2. Select all existing code (Ctrl+A) and replace with the contents of `src/lambda_function.py`
3. Click **Deploy**

---

## Step 4 — Attach IAM Permissions to Lambda

1. In the Lambda function, click **Configuration** → **Permissions**
2. Click the **role name** link (opens IAM)
3. Click **Add permissions** → **Attach policies**
4. Search and add each of the following:
   - `AmazonBedrockFullAccess`
   - `AmazonDynamoDBFullAccess`
   - `AmazonSNSFullAccess`

---

## Step 5 — Add Connect Resource Policy to Lambda

1. Still in Lambda → **Configuration** → **Permissions**
2. Scroll down to **Resource-based policy statements**
3. Click **Add permissions** → select **Other**
4. Fill in:
   - **Statement ID:** `connect-invoke`
   - **Principal:** `connect.amazonaws.com`
   - **Source ARN:** `arn:aws:connect:us-west-2:[YOUR-ACCOUNT-ID]:instance/[YOUR-CONNECT-INSTANCE-ID]`
   - **Action:** `lambda:InvokeFunction`
5. Click **Save**

---

## Step 6 — Create Amazon Lex Bot

1. Go to **Amazon Lex** in the AWS console (us-east-1)
2. Click **Create bot** → **Create a blank bot**
3. Fill in:
   - **Bot name:** `ITSTriageBot`
   - **IAM permissions:** Create a role with basic Amazon Lex permissions
   - **COPPA:** No
   - **Idle session timeout:** 2 minutes
4. Click **Next**
5. Language settings:
   - **Language:** English (US)
   - **Voice:** Danielle (Neural)
   - **Speech model:** Neural
   - **Confidence threshold:** 0.75
6. Click **Done**

### Create the 16 Intents

For each intent below, click **Add intent** → **Add empty intent**, name it, and add the sample utterances:

| Intent | Sample Utterances (add at least 10) |
|---|---|
| ChildSupport | I need help with child support, child support payments, I owe child support, child support enforcement, I haven't received my child support payment, how do I apply for child support, my ex isn't paying child support, I need to modify my child support order, child support services, paternity and child support |
| Unemployment | I lost my job, I need unemployment benefits, unemployment insurance, I got laid off, how do I apply for unemployment, I need jobless benefits, unemployment claim, I lost my income, I was fired and need help, I was let go from my job |
| DriversLicense | I need to renew my drivers license, drivers license, renew my license, vehicle registration renewal, I lost my drivers license, how do I get a state ID, I need to transfer my title, license plate renewal, my license is expired, drivers license office |
| Medicaid | I need help with Medicaid, Medicaid, I need health insurance, medical assistance, I can't afford health insurance, I need to apply for Medicaid, my Medicaid was cancelled, I need help paying for healthcare, low income health insurance, Medicaid renewal |
| HumanOperator | I need to speak to someone, transfer me to a human, speak to an operator, representative, I need help, let me talk to a person, I want to speak to a real person, I need a live agent, agent please, real person |
| Emergency | this is an emergency, I need help right now, I am in danger, someone is hurt, call 911, I need police, someone is in danger, there's been an accident, life threatening situation, I need an ambulance |
| FoodStamps | I need food assistance, I need help buying food, food stamps, SNAP benefits, I can't afford groceries, how do I apply for food stamps, EBT card, food assistance program, I need help feeding my family, my food stamps were cut off |
| MentalHealth | I need mental health help, I need to talk to someone, I'm struggling mentally, I need counseling, mental health services, I need help with depression, substance abuse help, I need rehab, drug treatment program, mental health crisis |
| ChildWelfare | I need to report child abuse, I want to report a neglected child, child protective services, I'm concerned about a child, child abuse hotline, foster care information, I want to adopt a child, I need to report an unsafe home, CPS, child endangerment |
| Insurance | I have an insurance question, my insurance claim was denied, I need to file an insurance complaint, insurance coverage question, I need help with my insurance, insurance dispute, consumer insurance complaint, my insurance company won't pay, insurance fraud, I need to verify insurance |
| Education | I have a school question, I need help with my child's school, public school issue, education department, school district complaint, I need information about colleges, higher education question, university admissions help, I need financial aid information, I need to enroll my child in school |
| Veterans | I need veterans help, veterans benefits, VA benefits, I am a veteran, veterans affairs, military veteran assistance, I need help with my veterans claim, veterans home purchase, GI bill, military benefits |
| PublicHealth | I need public health information, I need a birth certificate, I need a death certificate, vital records, I need WIC, women infants and children, health department, I need immunization records, food safety complaint, I need a health inspection |
| Transportation | I have a road question, highway question, road construction, I need to report a road hazard, transportation department, MDOT, bridge issue, I need a highway permit, public transit help, traffic issue |
| GovernmentOffice | I need to reach the governor, governor's office, lieutenant governor, elected official, attorney general, state treasurer, state auditor, secretary of state, I need to contact a state official, I need to reach an elected official |
| PoisonControl | poison control, someone swallowed something dangerous, I think someone was poisoned, toxic substance, I need poison help, overdose, chemical exposure, someone ate something toxic, poisoning emergency, hazardous substance |

7. Click **Build** after adding all intents
8. Wait for build to complete

---

## Step 7 — Link Lambda to Lex Alias

1. In Lex → **Aliases** → **TestBotAlias**
2. Click **English (US)** under Languages
3. Select **ITS-Triage-Agent** Lambda function → **$LATEST**
4. Click **Save**

> **Important:** Do NOT enable Lambda fulfillment on individual intents. Lex fulfillment should remain disabled. Connect handles Lambda invocation directly.

---

## Step 8 — Create Amazon Connect Instance

1. Go to **Amazon Connect** in AWS console (us-west-2 recommended)
2. Click **Create instance**
3. Fill in:
   - **Identity management:** Store users within Amazon Connect
   - **Access URL:** `its-triage-agent` (or your preferred subdomain)
4. Follow setup wizard with defaults
5. Click **Create instance**

---

## Step 9 — Link Lex Bot to Connect

1. In AWS console → **Amazon Connect** → click your instance
2. Click **Flows** on the left sidebar
3. Scroll to **Amazon Lex** → **Add Lex Bot**
4. Set **Region** to `US East (N. Virginia)` (us-east-1)
5. Select **ITSTriageBot** → **TestBotAlias**
6. Click **Add Amazon Lex Bot**

---

## Step 10 — Import Contact Flow

1. In the Amazon Connect admin panel → **Routing** → **Flows**
2. Click the dropdown next to **Create flow** → **Import**
3. Upload `src/connect_flow/ITS-Triage-Flow.json`
4. Review the imported flow
5. Update the Lambda ARN in the Lambda function block to your Lambda ARN
6. Click **Publish**

---

## Step 11 — Claim a Phone Number

1. In Amazon Connect → **Channels** → **Phone numbers** → **Claim a number**
2. Select:
   - **Channel:** Voice
   - **Type:** Toll free
   - **Country:** US
3. Claim an available number
4. Under **Contact flow / IVR** → select **ITS-Triage-Flow**
5. Click **Save**

---

## Step 12 — Test the System

Call your claimed phone number and say:
- "I need help with child support"
- "I lost my job"
- "I need food stamps"
- "this is an emergency"

Check DynamoDB → `its-triage-calls` → **Explore table items** to verify calls are being logged.

---

## Known Setup Issues

| Issue | Solution |
|---|---|
| SCP blocks Bedrock in non-approved regions | Deploy Lambda in us-east-1; confirm approved regions with your AWS admin |
| Lambda invocation timeout in Connect | Set Lambda invocation timeout to 8 seconds in the Connect contact flow Lambda block (default is 3s) |
| Double audio / garbled call | Disable Lambda fulfillment on all Lex intents — Connect handles Lambda invocation directly |
| "No origination entities" SNS error | SNS account is in sandbox mode; request production access or use verified sandbox numbers only |
| Lex bot not appearing in Connect | Ensure Lex bot is in the same region specified when adding to Connect (us-east-1) |
| Transfer goes straight to goodbye | `phone_e164` contact attribute not set; verify Set contact attributes block is wired between Lambda and transfer block |
