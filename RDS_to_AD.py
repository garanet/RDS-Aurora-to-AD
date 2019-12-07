import sys, boto3, logging, pymysql, base64, json, os
from ldap3  import *
from botocore.exceptions import ClientError 

### READ THE DB AUTH KEYS FROM SECRET MANAGERS 
def get_secret(secret_name,region_name):
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
def try_db_conn():
  keys= get_secret("CHANGEME","CHANGEME")
  # Retrive the credentials
  db_username = keys['username']
  db_password =  keys['password']
  db_name = keys['database']
  db_endpoint = keys['host']
  port = keys['port']
  print(keys)
  try:
      conn = pymysql.connect(db_endpoint, user=db_username,passwd=db_password, db=db_name, connect_timeout=5)
  except:
      logger.error("ERROR: Unexpected error: Could not connect to MySql instance.")
      sys.exit()
  logger.info("SUCCESS: Connection to RDS mysql instance succeeded")
  return(conn)

# READ USERS FROM RDS AURORA
def read_rds():
  conn = try_db_conn()
  logger.info("Reading from RDS")
  item_count = 0
  # READ FROM RDS THE USERS (CHECK THE SCHEMA)
  with conn.cursor() as cur:
    cur.execute("select * from Employee")
    for row in cur:
        print(row)
        item_count += 1
        logger.info(row)
        EmpID = row[0]
        objectClass = row[1]
        sAMAccountName = row[2]
        sAMAccountType = row[3]
        displayName = row[4]
        password = row[5]
        userAccountControl = row[6]
        userPrincipalName = row[7]
        sn = row[8]
        givenName = row[9]
        initials = row[10]
        mail = row[11]
        logger.info("SUCCESS: Record read from RDS")
        logger.info(item_count)
        
        # CALL THE AD FUNCTION
        write_ad(EmpID,objectClass,sAMAccountName,sAMAccountType,displayName,password,userAccountControl,userPrincipalName,sn,givenName,initials,mail)
        logger.info(write_ad)
  
# WRITE TO AD
def write_ad(EmpID,objectClass,sAMAccountName,sAMAccountType,displayName,password,userAccountControl,userPrincipalName,sn,givenName,initials,mail):
  # GET CONNECTION TO SECRET MANAGER FOR AD
  keys= get_secret("CHANGEME","CHANGEME")
  # Retrive the credentials
  domain = keys['domain']
  loginun = 'CHANGEME\\' + keys['loginun']
  loginpw = keys['loginpw']
  adurl = keys['url']
  port = keys['port']

  s = Server(adurl+':'+port, use_ssl=True, get_info=ALL)
  c=Connection(s,user=loginun, password=loginpw, check_names=True, lazy=False,raise_exceptions=False)
  
  # TRY IF THE AD CONNECTION WORKS
  if not c.bind():
      exit(c.result)
  
  # CREATE USER TO AD (CHECK THE SCHEMA)
  userdn = 'CN={},CN=CHANGEME,DC=CHANGEME,DC=CHANGEME,DC=CHANGEME'.format(sAMAccountName)

  c.add(userdn, attributes={
    'objectClass': ['organizationalPerson', 'person', 'top', 'user'],
    'givenName': givenName,
    'sn': sn,
    'initials': initials,
    'userPrincipalName': userPrincipalName,
    'sAMAccountName': sAMAccountName,
    'displayName': displayName,
    'mail': mail
  })

  # set password - must be done before enabling user
  # you must connect with SSL to set the password 
  c.extend.microsoft.modify_password(userdn, password)
  
  # Assign the user to Member Of
  #c.extend.microsoft.add_members_to_groups('cn=Administrator,cn=CHANGEME,dc=CHANGEME,dc=CHANGEME,dc=CHANGEME', 'cn=Enterprise Admins,cn=Users,dc=CHANGEME,dc=CHANGEME,dc=CHANGEME')
  
  # # enable user (after password set)
  c.modify(userdn, {'userAccountControl': [('MODIFY_REPLACE', 512)]})
  
  # # disable user
  # c.modify(userdn, {'userAccountControl': [('MODIFY_REPLACE', 2)]})
  
  logger.info(c.result)
  # # close the connection
  c.unbind()
  print(logger.info)
  return(logger.info)

def check_ping():
    hostname = "172.31.5.105"
    response = os.system("ping -c 1 " + hostname)
    # and then check the response...
    if response == 0:
        pingstatus = "Network Active"
    else:
        pingstatus = "Network Error"
        
# START THE 2 PROCESSES SCRIPTS
logger = logging.getLogger()
logger.setLevel(logging.INFO)
read_rds()
# check_ping()
