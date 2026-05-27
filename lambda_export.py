import json
import boto3

def lambda_handler(event, context):
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    s3 = boto3.client("s3", region_name="us-east-1")
    
    table = dynamodb.Table("its-triage-calls")
    
    response = table.scan()
    items = response["Items"]
    
    while "LastEvaluatedKey" in response:
        response = table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
        items.extend(response["Items"])
    
    items = [i for i in items if not str(i.get("call_id", "")).startswith("retry_")]
    
    def format_val(h, item):
        val = str(item.get(h, ""))
        if h == "timestamp" and "." in val:
            val = val[:23]
        return val.replace(",", " ")
    
    headers = ["call_id", "timestamp", "caller_input", "routed_agency", "phone", "confidence", "fallback_to_human", "status", "verified", "correct"]
    rows = [",".join(headers)]
    
    for item in items:
        row = [format_val(h, item) for h in headers]
        rows.append(",".join(row))
    
    csv_content = "\n".join(rows)
    
    s3.put_object(
        Bucket="its-triage-dashboard-data",
        Key="call-logs/calls.csv",
        Body=csv_content.encode("utf-8"),
        ContentType="text/csv"
    )
    
    print(f"Exported {len(items)} records to S3")
    return {"statusCode": 200, "records_exported": len(items)}
