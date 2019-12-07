Add-Type -Path "C:\Program Files (x86)\MySQL\MySQL Connector Net 8.0.17\Assemblies\v4.5.2\MySQL.Data.dll"
# This is essential to solve the missing Renci.SshNet.dll error
Add-Type -Path 'C:\Program Files (x86)\MySQL\MySQL Connector Net 8.0.17\Assemblies\v4.5.2\Renci.SshNet.dll'

# Mysql Connection string
$MySQLAdminUserName = ''
$MySQLAdminPassword = ''
$MySQLDatabase = ''
$MySQLHost = ''
$ConnectionString = "server=" + $MySQLHost + ";port=3306;uid=" + $MySQLAdminUserName + ";pwd=" + $MySQLAdminPassword + ";database="+$MySQLDatabase
$Query = 'SELECT * FROM Employee;'

# Open Connection to mysql
Try {
  [void][System.Reflection.Assembly]::LoadWithPartialName("MySql.Data")
  $Connection = New-Object MySql.Data.MySqlClient.MySqlConnection
  $Connection.ConnectionString = $ConnectionString
  $Connection.Open()
  $Command = New-Object MySql.Data.MySqlClient.MySqlCommand($Query, $Connection)
  $DataAdapter = New-Object MySql.Data.MySqlClient.MySqlDataAdapter($Command)
  $DataSet = New-Object System.Data.DataSet
  $RecordCount = $dataAdapter.Fill($dataSet, "data")
  $DataSet.Tables[0]
  }
Catch {
  Write-Host "ERROR : Unable to run query : $query `n$Error[0]"
 }
 # Define the Schema for the AD Users from the DB
 Try {
  foreach ($valRow in $DataSet.Tables[0].rows) {      
        $EmpID = $valRow.EmpID
        $objectClass = $valRow.objectClass
        $sAMAccountName = $valRow.sAMAccountName
        $sAMAccountType = $valRow.sAMAccountType
        $displayName = $valRow.displayName
        $password = $valRow.password
        $userAccountControl = $valRow.userAccountControl
        $userPrincipalName = $valRow.userPrincipalName
        $sn = $valRow.sn
        $givenName = $valRow.givenName
        $initials = $valRow.initials
        $mail = $valRow.mail
Try {
  dsadd user "cn=$givenName $sn,cn=Users,dc=CHANGEME,dc=CHANGEME,dc=CHANGEME" -samid $sAMAccountName -upn ($sAMAccountName+"@CHANGEME.CHANGEME.CHANGEME") -memberof "cn=ReportserverBrowsers,cn=Users,dc=CHANGEME,dc=CHANGEME,dc=CHANGEME" -display ($givenName+" "+$sn) -fn $givenName -ln $sn -email $mail -pwd $password -disabled no -canchpwd no -pwdneverexpires yes
  }
Catch {
  Write-Host "ERROR : Unable to copy Users to AD `n$Error[0]"
}
    }
}
Catch {
  Write-Host "ERROR : Unable to run the loop `n$Error[0]"
 }

Finally {
  $Connection.Close()
  Write-Host "RDS users copied to AD"
  }

