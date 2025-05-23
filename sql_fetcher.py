import os,pyodbc
import pandas as pd
import json
from semantic_kernel.skill_definition import sk_function

class Fetchsqlresultsfromdb:
	@sk_function(
	description="takes a sql query as input and runs it in the db and gives back the result",
	name="Fetchsqlresults",
	input_description="The the input sql statement which needs to executed in database",)
	def get_result_from_database(self,input_sql: str) -> str:
		server_name = os.getenv("server_name")
		database_name = os.getenv("database_name")

		# Determine authentication method based on environment
		if os.getenv('MSI_ENDPOINT') or os.getenv('IDENTITY_ENDPOINT'):
			auth_method = 'ActiveDirectoryMsi'
			# Prerequisites for using Managed Identity (Authentication=ActiveDirectoryMsi):
			# 1. The Python script must be running on an Azure service that supports Managed Identities.
			#    Examples include Azure App Service, Azure Functions, Azure Virtual Machines, Azure Kubernetes Service.
			# 2. The Azure resource (e.g., App Service, VM) running this code must have a
			#    System-Assigned or User-Assigned Managed Identity enabled.
			# 3. This Managed Identity must be granted appropriate permissions on the target Azure SQL Database.
			#    For example, the identity needs to be added as a user in the database and granted
			#    roles like 'db_datareader' or specific SELECT permissions on the queried tables.
			# 4. The environment variables 'server_name' and 'database_name' must be correctly set to point
			#    to your Azure SQL server and database.
		else:
			auth_method = 'ActiveDirectoryInteractive'
			# 'ActiveDirectoryInteractive' will be used if Managed Identity environment variables are not found.
			# This typically requires user interaction (e.g., a pop-up) for authentication.
			# Ensure Azure CLI or other Azure SDK tools are configured for authentication if running locally.

		try:
			conn_str = 'DRIVER=ODBC Driver 18 for SQL Server;SERVER={0};DATABASE={1};Authentication={2};Encrypt=yes'.format(
				server_name, database_name, auth_method
			)
			# Optional: print(f"Using connection string: {conn_str}") # For debugging
			conn = pyodbc.connect(conn_str)
			df = pd.read_sql(input_sql, conn)
			return df.to_json(orient='records', lines=True)
		except Exception as e:
			print(f"Error during database operation: {e}")
			print(f"Connection string used (check for sensitive info before logging broadly): DRIVER=ODBC Driver 18 for SQL Server;SERVER={server_name};DATABASE={database_name};Authentication={auth_method};Encrypt=yes")
			return "No Result Found"
