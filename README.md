# BankSystem

## Overview
The BankSystem is a Python application that implements managing a bank's database. It works with a local database to perform transactions, manage customer data, and handle banking services through a series of classes.

## How It Works
User Interaction: Upon launching the application, users are asked to enter commands that dictate the action to be performed.
Command Execution: Based on the user's input, the application instantiates the corresponding class (CustomerOperator, AccountOperator, or ServiceOperator) to handle the request.
Database Transactions: Each class uses methods from the Operator class to securely interact with the database, whether it’s adding a new customer or updating an account balance.
Logging: All operations, successful or failed, are logged into a file and the console, providing a traceable history of activities and errors for troubleshooting and auditing purposes.

## Overview of the classes
### Operator Class:
Acts as the central class for database operations, establishing connections and executing SQL queries.
Manages database sessions and includes robust error handling and comprehensive logging to ensure all activities are recorded.

### CustomerOperator Class:
Focuses on customer management tasks.
Adds new customers with detailed profiles.
Retrieves specific customer information based on their name.

### AccountOperator Class:
Manages bank accounts for existing customers.
Opens new accounts with specified types and balances.
Processes deposits and withdrawals, updating account balances accordingly.

### ServiceOperator Class:
Handles additional services like loans, credit cards, and insurance.
Enrolls customers in various financial services, setting terms such as interest rates and fees.

### OperatorInput Class:
Serves as the user interface for the bank system.
Interprets user commands to trigger specific operations (e.g., adding accounts or customers).
