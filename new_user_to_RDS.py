# SEARCH AND CHANGE THE 'CHANGEME' value.
import sys, logging, pymysql, boto3,json, base64
from botocore.exceptions import ClientError 

### READ THE DB AUTH KEYS FROM SECRET MANAGERS 
def get_secret(secret_name,region_name):
    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )
    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            raise e
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            raise e
    else:
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
            return json.loads(secret)
        else:
            decoded_binary_secret = base64.b64decode(get_secret_value_response['SecretBinary'])
            return json.loads(decoded_binary_secret)
# TRYING IF THE DB CONNECTION WORKS
def try_conn():
  # RETRIVE CREDENTIALS
  keys= get_secret("CHANGEME","CHANGEME")
  db_username = keys['username']
  db_password =  keys['password']
  db_name = keys['database']
  db_endpoint = keys['host']
  port = keys['port']
  
  try:
      conn = pymysql.connect(db_endpoint, user=db_username,passwd=db_password, db=db_name, connect_timeout=5)
  except:
      logger.error("ERROR: Unexpected error: Could not connect to MySql instance.")
      sys.exit()
  logger.info("SUCCESS: Connection to RDS mysql instance succeeded")
  return(conn)
 

def lambda_handler():
    item_count = 0
    conn = try_conn()
    with conn.cursor() as cur:
        cur.execute('insert into Employee (EmpID, objectClass, sAMAccountName, sAMAccountType, displayName, password, userAccountControl, userPrincipalName, sn,  givenName, initials, mail) values("6", "[\'organizationalPerson\', \'person\', \'top\', \'user\']", "powershell.first", "805306368", "powershell.first", "powershell1", "544", "powershell.first@CHANGEME.internal", "Firt", "powershell", "F", "powershell.first@CHANGEME.domain")')
        conn.commit()
        cur.execute("select * from Employee")
        for row in cur:
            item_count += 1
            logger.info(row)
            print(logger.info(row))
    return print("Added %d items to RDS MySQL table" %(item_count))

logger = logging.getLogger()
logger.setLevel(logging.INFO)
lambda_handler()
