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
import os

# Replace with your actual values
server = 'x6eps4xrq2xudenlfv6naeo3i4-5k6kabwq66je5j6st3x2vdnzuq.msit-datawarehouse.fabric.microsoft.com'
database = 'mdeedap'
driver = '{ODBC Driver 17 for SQL Server}'

# Determine authentication method based on environment
if os.getenv('MSI_ENDPOINT') or os.getenv('IDENTITY_ENDPOINT'):
    print("Using Managed Identity (ActiveDirectoryMsi) authentication.")
    authentication = 'ActiveDirectoryMsi'
    # For Managed Identity, UID and PWD are not needed in the connection string.
    # The identity of the Azure resource itself is used.
    # Prerequisites:
    # 1. Script running on an Azure service supporting Managed Identities (e.g., App Service, VM, Azure Functions).
    # 2. Managed Identity (System-Assigned or User-Assigned) enabled on the Azure resource.
    # 3. Managed Identity granted appropriate permissions on the Azure SQL Database.
else:
    print("Using Interactive (ActiveDirectoryInteractive) authentication.")
    authentication = 'ActiveDirectoryInteractive'
    # 'ActiveDirectoryInteractive': Prompts for Azure AD login. Suitable for local development.
    # Ensure Azure CLI or other Azure SDK tools are configured for authentication if running locally.

# Connection string for Azure SQL + AAD auth
# Encrypt=yes is a security best practice.
conn_str = f'''
DRIVER={driver};
SERVER={server};
DATABASE={database};
Authentication={authentication};
Encrypt=yes;
'''
print(f"Connection String: {conn_str}") # Optional: for debugging

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
