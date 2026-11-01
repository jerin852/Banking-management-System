
from bank_account import SavingsAccount

accounts = {}


def create_account():
    name = input("Enter account holder name: ")

    try:
        balance = float(input("Enter initial balance: "))

        if balance < 0:
            print("Initial balance cannot be negative!")
            return

        account_number = str(1001 + len(accounts))

        account = SavingsAccount(name, balance)
        accounts[account_number] = account

        print("\nAccount created successfully!")
        print("Account Number:", account_number)

    except ValueError as error:
        print("Error:", error)


def check_account():
    account_number = input("Enter account number: ")

    if account_number in accounts:
        accounts[account_number].check_balance()
    else:
        print("Account not found!")


def deposit_money():
    account_number = input("Enter account number: ")

    if account_number in accounts:
        try:
            amount = float(input("Enter deposit amount: "))
            accounts[account_number].deposit(amount)
        except ValueError as error:
            print("Transaction Error:", error)
    else:
        print("Account not found!")


def withdraw_money():
    account_number = input("Enter account number: ")

    if account_number in accounts:
        try:
            amount = float(input("Enter withdrawal amount: "))
            accounts[account_number].withdraw(amount)
        except ValueError as error:
            print("Transaction Error:", error)
    else:
        print("Account not found!")


while True:

    print("\n===== BANKING MANAGEMENT SYSTEM =====")
    print("1. Create Account")
    print("2. Check Account Details")
    print("3. Deposit Money")
    print("4. Withdraw Money")
    print("5. Exit")

    choice = input("Enter your choice: ")

    if choice == "1":
        create_account()

    elif choice == "2":
        check_account()

    elif choice == "3":
        deposit_money()

    elif choice == "4":
        withdraw_money()

    elif choice == "5":
        print("Thank you for using our Banking System!")
        break

    else:
        print("Invalid choice!")
