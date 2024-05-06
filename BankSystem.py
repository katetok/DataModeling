from sqlalchemy import create_engine, text, exc
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import logging
import os

#Main class for managing database BankSystem. It mainly accesses the database and execute queries
#Classes that work with specific table inherit that class and send specific queries through
#main execute_query method defined here. The classes handles connection with the database
#so children classes are only about working with specific tables
class Operator:
    _logger = logging.getLogger('Operator')
    def __init__(self, db_url):
        log_dir = 'logs'
        log_file_path = os.path.join(log_dir, 'BankSystem.log')
        # To ensure the `logs` folder exists
        if not os.path.exists(log_dir):
            os.mkdir(log_dir)
        self.__class__._logger.setLevel(logging.DEBUG)
        fileHandler = logging.FileHandler(log_file_path)
        fileHandler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fileHandler.setFormatter(file_formatter)
        consoleHandler = logging.StreamHandler()
        consoleHandler.setLevel(logging.DEBUG)
        self.__class__._logger.addHandler(fileHandler)
        self.__class__._logger.addHandler(consoleHandler)
        try:
            self.engine = create_engine(db_url)
            Session = sessionmaker(bind=self.engine)
            self.session = Session()
        except exc.SQLAlchemyError as sqle:
            self.__class__._logger.error("An unexpected error occured:", sqle)

    def execute_query(self, sql_query, params = None):
        try:
            result = self.session.execute(text(sql_query), params)
            self.session.commit()
            return result
        except exc.SQLAlchemyError as sqle:
            self.__class__._logger.error("An unexpected error occured:", sqle)
            return None
        
    def get_customer_id(self):
        print('Enter first and last name of the client')
        first_name = input("First Name: ")
        last_name = input("Last Name: ")
        sql_select = "SELECT id FROM customer WHERE first_name = '" + first_name + "' AND last_name = '" + last_name + "';"
        select_result = self.execute_query(sql_select)
        if select_result.rowcount == 1:
            return int(select_result.first()[0])
        elif select_result.rowcount == 0:
            return -1
        elif select_result.rowcount > 1:
            return -2

#Class that works with customer table and provides functionality such as adding new customers
#and retreiving information about customers
class CustomerOperator(Operator):
    def add_customer(self):
        print("Enter customer details:")
        first_name = input("First Name: ")
        last_name = input("Last Name: ")
        address = input("Address: ")
        phone_number = input("Phone Number: ")
        email = input("Email: ")
        gender = input("Gender: ")
        dob = input("Date of Birth (YYYY-MM-DD): ")
        try:
            dob = datetime.strptime(dob, "%Y-%m-%d")
        except ValueError:
            print("Invalid date format. Please start over and enter the date in YYYY-MM-DD format.")
            return

        customer_since = datetime.now()

        sql_insert = """
            INSERT INTO Customer (first_name, last_name, address, phone_number, email, gender, dob, customer_since)
            VALUES (:first_name, :last_name, :address, :phone_number, :email, :gender, :dob, :customer_since)
        """
        
        # Create a dictionary with customer characteristics values
        params = {
            'first_name': first_name,
            'last_name': last_name,
            'address': address,
            'phone_number': phone_number,
            'email': email,
            'gender': gender,
            'dob': dob,
            'customer_since': customer_since
        }
        insert_result = self.execute_query(sql_insert, params)
        if (insert_result.rowcount > 0):
            self.__class__._logger.info("Customer successfully added")
        else: self.__class__._logger.error("Error occured while adding the customer")


#Class that adds an account for an existing customer
class AccountOperator(Operator):
    def add_account(self):
        customer_id = super().get_customer_id()
        if customer_id >= 0:
            account_type = input("Input account type (Checking, Savings, IRA or ESA):") #Checking, Savings, IRA, ESA
            balance = input("Input balance:")
            opening_date = str(datetime.now())
            account_status = 'Active' #'Active', 'Frozen', 'Closed'
            sql_insert = (
                f"INSERT INTO Account (customer_id, account_type, balance, opening_date, account_status) "
                f"VALUES ({customer_id}, '{account_type}', {balance}, '{opening_date}', '{account_status}')")
            insert_result = self.execute_query(sql_insert)
            if insert_result:
                self.__class__._logger.info('Account successfully created')
            else:
                self.__class__._logger.info('Coudn\'t create an account for this customer')
        else:
            self.__class__._logger.warning('No customer exists with this name')

    def update_balance(self, transaction_type):
        customer_id = self.get_customer_id()
        if customer_id >= 0:
            amount = input(f"Enter an amount to {transaction_type}: ")
            if not amount.isdigit() or int(amount) <= 0:
                self.__class__._logger.warning('Incorrect amount. Please start again')
                return
            if transaction_type == 'deposit':
                sql_update = f"UPDATE Account SET balance = balance + {amount} WHERE customer_id = {customer_id};"
            elif transaction_type == 'withdrawal':
                sql_update = f"UPDATE Account SET balance = balance - {amount} WHERE customer_id = {customer_id} AND balance >= {amount};"
            update_result = self.execute_query(sql_update)
            if update_result.rowcount > 0:
                self.__class__._logger.info(f'{transaction_type.capitalize()} successfully made')
            else:
                self.__class__._logger.error(f'Error occurred while {transaction_type}')
        else:
            self.__class__._logger.warning('No customer exists with this name')


#Class that adds a service for an existing customer
class ServiceOperator(Operator):
    def add_service(self):
        customer_id = super().get_customer_id()
        if customer_id >= 0:
            service_type = input('Input service type (Loan, Credit Card or Insurance):')
            interest_rate = input('Interest rate:')
            credit_limit = input('Credit limit:')
            annual_fee = input('Annual fee:')
            opening_date = datetime.now()
            term = input('Input term of the service:')
            sql_insert = (
            f"INSERT INTO Service (customer_id, service_type, interest_rate, credit_limit, annual_fee, opening_date, term)" 
            f" VALUES ({customer_id}, '{service_type}', {interest_rate}, {credit_limit}, {annual_fee}, '{opening_date}', {term});")
            insert_result = self.execute_query(sql_insert)
            if insert_result.rowcount > 0:
                self.__class__._logger.info('Service successfully added')
            else: self.__class__._logger.error('Error occured while adding a survice')
        else:
            self.__class__._logger.warning('No customer exists with this name')



db_url = 'mysql+pymysql://root:4570219@127.0.0.1/banksystem'

#Main class for interacting with an operator of a database
#Asks for operators input on which operation is performing, a connection with a database
#Calls corresponging methods for operations implemented in CustomerOperator class
class OperatorInput():
    def __init__(self, db_url):
        #Options: add_customer, get_customer, add_account
        input_command = input("Print command you performing:")
        if input_command == 'add_customer':
            CustomerOperator(db_url).add_customer()
        elif input_command == 'get_customer':
            CustomerOperator(db_url).get_customer()
        elif input_command == 'add_account':
            AccountOperator(db_url).add_account()
        elif input_command == 'deposit':
            AccountOperator(db_url).update_balance('deposit')
        elif input_command == 'withdrawal':
            AccountOperator(db_url).update_balance('withdrawal')
        elif input_command == 'add_service':
            ServiceOperator(db_url).add_service()
        else: print('No such command found')

OpInput  = OperatorInput(db_url)









