# Sample Agency Directory Structure

## Hub-ITS-Triage-Agent | Data Sample

This file documents the structure and format of the Mississippi State Agency Directory embedded in the Lambda function as the AI knowledge base.

**Note:** The actual agency directory used in this PoC is sourced from the publicly available **2025–2026 Mississippi State Government Telephone Directory** published by the Mississippi Department of Information Technology Services (ITS). It is embedded as a structured string constant in `src/lambda_function.py`.

---

## Directory Format

The agency directory is embedded in Lambda as a formatted string under the `AGENCY_DIRECTORY` constant. Each entry follows this format:

```
- [Service Description]: [Agency Full Name] ([Agency Abbreviation]) — [Phone Number]
```

---

## Category Structure

The directory is organized into the following categories:

### EMERGENCY SERVICES
```
- Emergency (Fire/Police/Ambulance): 911
- Capitol Police: [number]
- Mississippi Highway Patrol: [number]
- Homeland Security: [number]
- MS Emergency Management Agency (MEMA): [number]
- Poison Control Services Center: [number]
```

### HUMAN SERVICES & BENEFITS
```
- Child Support Enforcement: MDHS (Mississippi Dept of Human Services) — [number]
- Food Stamps / SNAP Benefits / TANF: MDHS — [number]
- Child Abuse Hotline: MDHS Child Protection Services — [number]
- Child Welfare / Foster Care / Adoption: MDCPS — [number]
```

### HEALTH & MEDICAID
```
- Medicaid / Health Insurance Assistance: Division of Medicaid — [number]
- State Department of Health: MSDH — [number]
- Birth & Death Certificates / Vital Records: MSDH — [number]
- WIC (Women, Infants & Children): MSDH — [number]
```

### MENTAL HEALTH & DISABILITY
```
- Mental Health / Substance Abuse: DMH (Dept of Mental Health) — [number]
- Disability Services / Vocational Rehabilitation: MDRS — [number]
```

### EMPLOYMENT & UNEMPLOYMENT
```
- Unemployment Benefits / Job Loss: MDES (Mississippi Dept of Employment Security) — [number]
- Workers Compensation / Workplace Injury: MWCC — [number]
```

### DRIVERS LICENSE & VEHICLES
```
- Driver's License / Vehicle Tags / Registration: DPS (Dept of Public Safety) — [number]
- Motor Vehicle Commission: [number]
```

### TAXES & REVENUE
```
- State Tax Questions / Tax Returns: Dept of Revenue — [number]
- Individual Tax Help Line: [number]
```

### BUSINESS & LICENSING
```
- Business Licensing / Business Registration: Secretary of State — [number]
- Contractors Board: [number]
- Banking & Consumer Finance: [number]
```

### VOTING & ELECTIONS
```
- Voting / Voter Registration / Elections: Secretary of State — [number]
```

### CORRECTIONS & LAW ENFORCEMENT
```
- Corrections / Inmate Information: MDOC (Dept of Corrections) — [number]
- Parole Board: [number]
- Bureau of Narcotics: [number]
- Crime Stopper Hotline: [number]
```

### EDUCATION
```
- Public School Issues / K-12: MDE (State Dept of Education) — [number]
- Higher Education / College / University: IHL — [number]
- Community & Junior Colleges Board: [number]
```

### ENVIRONMENT & AGRICULTURE
```
- Environmental Concerns / Pollution: MDEQ — [number]
- Agriculture / Farming / Livestock: MDA — [number]
- State Parks / Wildlife / Hunting & Fishing Licenses: MDWFP — [number]
```

### INSURANCE & LEGAL
```
- Insurance Questions / Consumer Complaints: MID (Dept of Insurance) — [number]
- Attorney General: [number]
- Consumer Protection (AG Office): [number]
```

### VETERANS & MILITARY
```
- Veterans Affairs Board: [number]
- Military Department of Mississippi: [number]
- G.V. Montgomery VA Medical Center: [number]
```

### TRANSPORTATION & ROADS
```
- Transportation / Roads / Highways: MDOT — [number]
```

### ELECTED OFFICIALS
```
- Governor's Office: [number]
- Lieutenant Governor's Office: [number]
- Secretary of State: [number]
- Attorney General: [number]
- State Treasurer: [number]
- State Auditor: [number]
```

### FEDERAL SERVICES
```
- Federal Financial Aid / FAFSA: US Dept of Education — [number]
- Social Security / SSI / SSDI: Social Security Administration — [number]
- Federal Veterans Benefits: VA (Veterans Affairs) — [number]
- Medicare Questions: Centers for Medicare & Medicaid — [number]
```

---

## Notes

- Phone numbers are formatted in Lambda using `format_phone()` for Polly text-to-speech (digit-by-digit)
- Phone numbers are formatted using `e164_phone()` for live call transfer (E.164 format)
- The full directory with actual phone numbers is embedded in `src/lambda_function.py`
- All phone numbers are sourced from the publicly available 2025–2026 Mississippi State Government Telephone Directory
- A production deployment should replace the hardcoded directory with Amazon Kendra for ITS-managed updates
