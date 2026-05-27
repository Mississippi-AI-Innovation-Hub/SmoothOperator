import json
import boto3
import uuid
from datetime import datetime

INTENT_MAP = {
    "ChildSupport": "I need help with child support payments",
    "Unemployment": "I need help with unemployment benefits",
    "DriversLicense": "I need to renew my drivers license",
    "Medicaid": "I need help with Medicaid",
    "HumanOperator": "I need to speak with a human operator",
    "Emergency": "EMERGENCY",
    "FoodStamps": "I need help with food stamps and SNAP benefits",
    "MentalHealth": "I need mental health or substance abuse services",
    "ChildWelfare": "I need to report child abuse or get foster care information",
    "Insurance": "I have an insurance question or complaint",
    "Education": "I have a question about public schools or higher education",
    "Veterans": "I need help with veterans benefits and military assistance",
    "PublicHealth": "I need help with public health, vital records, or health department services",
    "Transportation": "I have a question about roads, highways, or transportation",
    "GovernmentOffice": "I need to reach an elected official or government office",
    "PoisonControl": "I need poison control assistance"
}

DTMF_MAP = {
    "1": "I need help with child support payments",
    "2": "I need help with unemployment benefits",
    "3": "I need to renew my drivers license",
    "4": "I need help with Medicaid",
    "0": "I need to speak with a human operator"
}

AGENCY_DIRECTORY = """
Mississippi State Agencies - Official 2025-2026 Directory:

EMERGENCY SERVICES:
- Emergency (Fire/Police/Ambulance): 911
- Capitol Police: 601-359-3125
- Mississippi Highway Patrol: 601-987-1212
- Homeland Security: 601-987-1278
- MS Emergency Management Agency (MEMA): 601-933-6362
- MEMA 24-Hour Emergency Line: 601-933-6875
- Poison Control Services Center: 601-984-1675

HUMAN SERVICES & BENEFITS:
- Child Support Enforcement: MDHS (Mississippi Dept of Human Services) — 877-882-4916
- Food Stamps / SNAP Benefits / TANF: MDHS (Mississippi Dept of Human Services) — 601-359-4500
- Child Abuse Hotline: MDHS Child Protection Services — 601-576-1501
- Adult Protection Hotline: MDHS — 601-359-4577
- Child Welfare / Foster Care / Adoption: MDCPS (Dept of Child Protection Services) — 601-359-4500
- Early Childhood Care & Development: MDHS — 601-359-4544
- Youth Services: MDHS — 601-359-4972

HEALTH & MEDICAID:
- Medicaid / Health Insurance Assistance: Division of Medicaid — 601-359-6050
- Medicaid Eligibility (Kids Now Hotline): 601-576-0871
- Medicaid Fraud Hotline: 601-576-4162
- State Department of Health: MSDH — 601-576-7400
- Health Info Line: 866-458-4948
- Birth & Death Certificates / Vital Records: MSDH — 601-206-8200
- WIC (Women, Infants & Children): MSDH — 601-991-6000

MENTAL HEALTH & DISABILITY:
- Mental Health / Substance Abuse: DMH (Dept of Mental Health) — 601-359-1288
- Disability Services / Vocational Rehabilitation: MDRS (Dept of Rehabilitation Services) — 601-853-5100
- Mississippi State Hospital: 601-351-8000
- Boswell Regional Center (IDD Services): 601-867-5000

EMPLOYMENT & UNEMPLOYMENT:
- Unemployment Benefits / Job Loss: MDES (Mississippi Dept of Employment Security) — 601-321-6000
- MDES Contact Center: 601-493-9427
- Workers Compensation / Workplace Injury: MWCC (Workers Comp Commission) — 601-987-4200

DRIVERS LICENSE & VEHICLES:
- Driver's License / Vehicle Tags / Registration: DPS (Dept of Public Safety) — 601-987-1212
- Driver Services Bureau: 601-487-7091
- Motor Vehicle Commission: 601-987-3995
- Inclement Weather Road Line: 601-987-1211

TAXES & REVENUE:
- State Tax Questions / Tax Returns: Dept of Revenue — 601-923-7700
- Individual Tax Help Line: 601-923-7700
- Individual Tax Refund Line: 601-923-7801
- Sales and Use Tax: 601-923-7015
- Alcoholic Beverage Control: 601-856-1301

BUSINESS & LICENSING:
- Business Licensing / Business Registration: Secretary of State — 601-359-1633
- Contractors Board: 601-354-6161
- Banking & Consumer Finance: 601-321-6901
- Securities Regulation Hotline: 601-359-1334

VOTING & ELECTIONS:
- Voting / Voter Registration / Elections: Secretary of State — 601-576-2550
- Secretary of State Main: 601-359-1350

CORRECTIONS & LAW ENFORCEMENT:
- Corrections / Inmate Information: MDOC (Dept of Corrections) — 601-359-5600
- Parole Board: 601-576-3520
- Bureau of Narcotics: 601-371-3600
- Crime Stopper Hotline: 888-827-4637

EDUCATION:
- Public School Issues / K-12: MDE (State Dept of Education) — 601-359-3513
- Higher Education / College / University: IHL (Institutions of Higher Learning) — 601-432-6623
- Student Financial Aid (IHL): 601-432-6997
- Community & Junior Colleges Board: 601-432-6518

ENVIRONMENT & AGRICULTURE:
- Environmental Concerns / Pollution: MDEQ (Dept of Environmental Quality) — 601-961-5171
- Agriculture / Farming / Livestock: MDA (Dept of Agriculture) — 601-359-1100
- State Parks / Wildlife / Hunting & Fishing Licenses: MDWFP (Wildlife, Fisheries & Parks) — 601-432-2400
- Forestry Commission: 601-359-1386

INSURANCE & LEGAL:
- Insurance Questions / Consumer Complaints: MID (Dept of Insurance) — 601-359-3569
- Insurance Consumer Assistance: 601-359-2453
- Attorney General: 601-359-3680
- Consumer Protection (AG Office): 601-359-3680
- Domestic Violence (AG Office): 601-359-3680

VETERANS & MILITARY:
- Veterans Affairs Board: 601-576-4850
- Veterans Home Purchase Board: 601-576-4800
- Military Department of Mississippi: 601-313-6764
- G.V. Montgomery VA Medical Center: 601-362-4471

TRANSPORTATION & ROADS:
- Transportation / Roads / Highways: MDOT (Dept of Transportation) — 601-359-7001
- MDOT Public Affairs: 601-359-7074

ELECTED OFFICIALS:
- Governor's Office: 601-359-3150
- Lieutenant Governor's Office: 601-359-3200
- Secretary of State: 601-359-1350
- Attorney General: 601-359-3680
- State Treasurer: 601-359-3600
- State Auditor: 601-576-2800

STATE GOVERNMENT OPERATOR:
- ITS State Operator (Main): 601-359-1000
- ITS Main: 601-432-8000
- ITS Help Desk / Technical Support: 601-432-8080

FINANCIAL AID & FEDERAL SERVICES:
- Federal Financial Aid / FAFSA: US Dept of Education — 1-800-433-3243
- Social Security / SSI / SSDI: Social Security Administration — 1-800-772-1213
- Federal Veterans Benefits: VA (Veterans Affairs) — 1-800-827-1000
- Medicare Questions: Centers for Medicare & Medicaid — 1-800-633-4227
"""

def format_phone(phone):
    digits = ''.join(filter(str.isdigit, phone))
    if len(digits) == 11:
        # Format as 1. 8 7 7. 8 8 2. 4 9 1 6
        return f"{digits[0]}. {' '.join(digits[1:4])}. {' '.join(digits[4:7])}. {' '.join(digits[7:])}"
    elif len(digits) == 10:
        return f"{' '.join(digits[0:3])}. {' '.join(digits[3:6])}. {' '.join(digits[6:])}"
    return phone

def e164_phone(phone):
    digits = ''.join(filter(str.isdigit, phone))
    if len(digits) == 11:
        return f"+{digits}"
    elif len(digits) == 10:
        return f"+1{digits}"
    return phone

def log_call(table, caller_input, routing, status="success"):
    table.put_item(Item={
        "call_id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat(),
        "caller_input": caller_input,
        "routed_agency": routing.get("agency", "unknown"),
        "phone": routing.get("phone", "unknown"),
        "confidence": str(routing.get("confidence", 0)),
        "fallback_to_human": str(routing.get("fallback_to_human", False)),
        "status": status,
        "verified": "null",
        "correct": "null"
    })

def send_sms(caller_phone, agency, phone):
    try:
        client = boto3.client("pinpoint-sms-voice-v2", region_name="us-east-1")
        message = f"Thank you for calling MS State Government. You were connected to: {agency}. Their direct number: {phone}. Have a great day!"
        response = client.send_text_message(
            DestinationPhoneNumber=caller_phone,
            OriginationIdentity="arn:aws:sms-voice:us-east-1:568318158080:phone-number/phone-889ba07387aa46b7873de605b5605494",
            MessageBody=message,
            MessageType="TRANSACTIONAL"
        )
        print(f"SMS sent successfully: {response}")
    except Exception as e:
        print(f"SMS failed: {str(e)}")

def invoke_bedrock(client, prompt, attempts=3):
    for i in range(attempts):
        try:
            response = client.invoke_model(
                modelId="amazon.nova-micro-v1:0",
                body=json.dumps({
                    "messages": [{"role": "user", "content": [{"text": prompt}]}],
                    "inferenceConfig": {"max_new_tokens": 400}
                }),
                contentType="application/json",
                accept="application/json"
            )
            result = json.loads(response["body"].read())
            raw_text = result["output"]["message"]["content"][0]["text"]
            start = raw_text.find("{")
            end = raw_text.rfind("}") + 1
            clean = raw_text[start:end]
            routing = json.loads(clean)
            assert "agency" in routing and "phone" in routing and "description" in routing
            return routing
        except Exception as e:
            print(f"Attempt {i+1} failed: {str(e)}")
            if i == attempts - 1:
                raise

def build_prompt(caller_input):
    return f"""You are a professional AI call triage agent for the Mississippi State Government Operator line.
A citizen has called and said: "{caller_input}"

Using the official 2025-2026 Mississippi State Government Telephone Directory below, identify what they need and route them to the correct agency.
{AGENCY_DIRECTORY}

Respond ONLY with valid JSON in this exact format, no extra text whatsoever:
{{
  "agency": "Full official agency name",
  "phone": "phone number",
  "description": "You are being connected to [full agency name]. They handle [specific services]. Their direct number is [phone number]. Please hold while I connect you.",
  "confidence": 0.95,
  "fallback_to_human": false
}}

Rules:
- Use ONLY phone numbers from the official directory above
- Be specific and professional about what the agency handles
- Always include the phone number in the description
- If confidence is below 0.75, set fallback_to_human to true and set description to a polite clarifying question
- Never make eligibility or legal determinations
- If caller mentions emergency, danger, or injury set agency to Emergency Services, phone to 911"""

def lambda_handler(event, context):
    print("FULL EVENT:", json.dumps(event))
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")

    # Lex event
    if "sessionState" in event:
        intent_name = event.get("sessionState", {}).get("intent", {}).get("name", "")
        caller_input = INTENT_MAP.get(intent_name, "I need help")
        table = dynamodb.Table("its-triage-calls")

        if intent_name == "Emergency":
            routing = {"agency": "Emergency Services", "phone": "911", "description": "This sounds like an emergency. Please hang up immediately and dial 9 1 1.", "confidence": 1.0, "fallback_to_human": True}
            log_call(table, caller_input, routing, status="emergency")
            return {"sessionState": {"dialogAction": {"type": "Close"}, "intent": {"name": intent_name, "state": "Fulfilled"}}, "messages": [{"contentType": "PlainText", "content": "This sounds like an emergency. Please hang up immediately and dial 9 1 1."}]}

        if intent_name == "HumanOperator":
            routing = {"agency": "Human Operator", "phone": "0", "description": "Transferring you to a live operator now. Please hold, your call is important to us.", "confidence": 1.0, "fallback_to_human": True}
            log_call(table, caller_input, routing, status="human_transfer")
            return {"sessionState": {"dialogAction": {"type": "Close"}, "intent": {"name": intent_name, "state": "Fulfilled"}}, "messages": [{"contentType": "PlainText", "content": "Transferring you to a live operator now. Please hold, your call is important to us."}]}

        try:
            client = boto3.client("bedrock-runtime", region_name="us-east-1")
            routing = invoke_bedrock(client, build_prompt(caller_input))
            phone_spoken = format_phone(routing.get("phone", ""))
            description = f"You are being connected to {routing.get('agency')}. Their direct number is {phone_spoken}. Please hold while I connect you."
            log_call(table, caller_input, routing, status="success")
            return {"sessionState": {"dialogAction": {"type": "Close"}, "intent": {"name": intent_name, "state": "Fulfilled"}}, "messages": [{"contentType": "PlainText", "content": description}]}
        except Exception as e:
            print("ERROR:", str(e))
            log_call(table, caller_input, {}, status=f"error: {str(e)}")
            return {"sessionState": {"dialogAction": {"type": "Close"}, "intent": {"name": intent_name, "state": "Failed"}}, "messages": [{"contentType": "PlainText", "content": "I apologize, something went wrong. Please hold while I transfer you to an operator."}]}

    # Connect event
    raw_input = event.get("Details", {}).get("Parameters", {}).get("caller_input", "") or event.get("caller_input", "")
    print("RAW INPUT:", raw_input)
    raw_stripped = str(raw_input).strip()
    caller_input = DTMF_MAP.get(raw_stripped) or INTENT_MAP.get(raw_stripped) or "I need help"
    print("CALLER INPUT:", caller_input)
    caller_phone = event.get("Details", {}).get("ContactData", {}).get("CustomerEndpoint", {}).get("Address", "")
    print("CALLER PHONE:", caller_phone)

    table = dynamodb.Table("its-triage-calls")

    if raw_stripped in ("0", "HumanOperator"):
        routing = {"agency": "Human Operator", "phone": "0", "description": "Transferring you to a live operator now. Please hold, your call is important to us.", "confidence": 1.0, "fallback_to_human": True}
        log_call(table, caller_input, routing, status="human_transfer")
        return {"description": "Transferring you to a live operator now. Please hold, your call is important to us.", "fallback": "True"}

    if raw_stripped == "Emergency":
        routing = {"agency": "Emergency Services", "phone": "911", "description": "This sounds like an emergency. Please hang up immediately and dial 9 1 1.", "confidence": 1.0, "fallback_to_human": True}
        log_call(table, caller_input, routing, status="emergency")
        return {"description": "This sounds like an emergency. Please hang up immediately and dial 9 1 1.", "fallback": "True"}

    # Check business hours (CST = UTC-6)
    now_utc = datetime.utcnow()
    cst_hour = (now_utc.hour - 6) % 24
    cst_weekday = now_utc.weekday()
    is_business_hours = (cst_weekday < 5) and (8 <= cst_hour < 17)

    try:
        client = boto3.client("bedrock-runtime", region_name="us-east-1")
        routing = invoke_bedrock(client, build_prompt(caller_input))
        phone_spoken = format_phone(routing.get("phone", ""))
        phone_transfer = e164_phone(routing.get("phone", ""))

        if not is_business_hours:
            description = f"Our offices are currently closed. You are trying to reach {routing.get('agency')}. Their direct number is {phone_spoken}. Please call back Monday through Friday between 8 AM and 5 PM Central Time."
        else:
            description = f"You are being connected to {routing.get('agency')}. Their direct number is {phone_spoken}. Please hold while I connect you."

        routing["description"] = description
        log_call(table, caller_input, routing, status="success")

        if caller_phone:
            send_sms(caller_phone, routing.get("agency", ""), routing.get("phone", ""))

        return {
            "description": description,
            "agency": routing.get("agency", "unknown"),
            "phone": routing.get("phone", "unknown"),
            "phone_e164": phone_transfer,
            "confidence": str(routing.get("confidence", 0)),
            "fallback": str(routing.get("fallback_to_human", False))
        }

    except Exception as e:
        print("ERROR:", str(e))
        log_call(table, caller_input, {}, status=f"error: {str(e)}")
        return {"description": "I apologize, something went wrong. Please try again."}
