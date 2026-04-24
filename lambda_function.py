import boto3
import logging

# Initialize logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

wafv2 = boto3.client('wafv2', region_name='us-east-1') 

# CONFIGURATION
IP_SET_NAME = 'AutomatedBlockList' 
IP_SET_ID = 'your-ip-set-id-here' 
SCOPE = 'REGIONAL'

def lambda_handler(event, context):
    try:
        # 1. Get the current IP Set and its LockToken (for concurrency)
        get_res = wafv2.get_ip_set(Name=IP_SET_NAME, Scope=SCOPE, Id=IP_SET_ID)
        lock_token = get_res['LockToken']
        current_ips = get_res['IPSet'].get('Addresses', [])
        
        # Example: In a real scenario, this IP would be parsed from logs
        ip_to_block = "1.2.3.4/32" 
        
        if ip_to_block not in current_ips:
            current_ips.append(ip_to_block)
            
            # 2. Update the WAF IP Set
            wafv2.update_ip_set(
                Name=IP_SET_NAME,
                Scope=SCOPE,
                Id=IP_SET_ID,
                Addresses=current_ips,
                LockToken=lock_token
            )
            logger.info(f"Successfully blocked IP: {ip_to_block}")
        else:
            logger.info(f"IP {ip_to_block} already exists in the blocklist.")
            
    except Exception as e:
        logger.error(f"Error updating IP Set: {str(e)}")
        raise e
