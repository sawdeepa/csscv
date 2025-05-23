# This script requires 'ODBC Driver 17 for SQL Server' (or a compatible version like 18) to be installed.
#
# For Linux:
# - The driver is often named 'msodbcsql17' (or 'msodbcsql18').
# - Installation via package manager (example commands, adapt to your distribution):
#   - Debian/Ubuntu: sudo apt-get install msodbcsql17  (or msodbcsql18)
#   - RHEL/CentOS: sudo yum install msodbcsql17  (or msodbcsql18)
# - For detailed instructions, refer to the official Microsoft ODBC driver documentation for SQL Server
#   for your specific Linux distribution.
#
# For Windows:
# - Download the driver from the Microsoft website.
# - Search for "Download ODBC Driver for SQL Server".
#
# Note: Exact package names or installation steps might vary depending on your OS distribution and version.

import pyodbc

# Replace with your actual values
server = 'x6eps4xrq2xudenlfv6naeo3i4-5k6kabwq66je5j6st3x2vdnzuq.msit-datawarehouse.fabric.microsoft.com'
database = 'mdeedap'
authentication = 'ActiveDirectoryInteractive'  # Options: ActiveDirectoryInteractive, ActiveDirectoryPassword, etc.
# - 'ActiveDirectoryInteractive': Use this for interactive scenarios where a user can sign in via a pop-up window.
#                                This is suitable when running the script manually.
# - For automated scripts or backend services, consider alternatives:
#   - 'ActiveDirectoryServicePrincipal': Uses an Azure AD App Registration (Service Principal) with a client ID and secret or certificate.
#                                        This is generally recommended for automated flows.
#                                        Requires additional connection string parameters like 'UID=<app_id>' and 'PWD=<app_secret_or_cert>'.
#   - 'ActiveDirectoryPassword': Uses Azure AD username and password. Less recommended for automated flows due to security concerns
#                                with storing passwords. If used, credentials should be handled securely (e.g., environment variables, Azure Key Vault).
#                                Requires 'UID=<username>' and 'PWD=<password>' in the connection string.
# This script will use 'ActiveDirectoryInteractive' as currently set. Modify as needed for your environment.
driver = '{ODBC Driver 17 for SQL Server}'

# Connection string for Azure SQL + AAD auth
conn_str = f'''
DRIVER={driver};
SERVER={server};
DATABASE={database};
Authentication={authentication};
'''

# Connect and query
try:
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    cursor.execute("SELECT TOP 10 * FROM vulnerability_messages")

    # Fetch results
    rows = cursor.fetchall()
    for row in rows:
        print(row)

    cursor.close()
    conn.close()

except pyodbc.Error as odbc_err:
    error_message = str(odbc_err.args[0])
    if "Can't open lib" in error_message or "file not found" in error_message:
        print("Error: The specified ODBC driver was not found. Please ensure 'ODBC Driver 17 for SQL Server' is installed and configured correctly in your system's ODBC driver manager.")
        print(f"Original error: {odbc_err}")
    else:
        print(f"pyodbc Error: {odbc_err}")

except Exception as e:
    print(f"Error: {e}")
