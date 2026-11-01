
from abc import ABC, abstractmethod


class BankAccount(ABC):

    def __init__(self, name, balance):
        if balance < 0:
            raise ValueError("Initial balance cannot be negative")

        self.name = name
        self.__balance = balance

    def deposit(self, amount):

        if amount <= 0:
            raise ValueError("Deposit amount must be positive")

        self.__balance += amount
        print("Deposited:", amount)

    def withdraw(self, amount):

        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")

        if amount > self.__balance:
            raise ValueError("Insufficient balance")

        self.__balance -= amount
        print("Withdrawn:", amount)

    def check_balance(self):
        print("Account Holder:", self.name)
        print("Current Balance:", self.__balance)

    def get_balance(self):
        return self.__balance

    @abstractmethod
    def calculate_interest(self):
        pass


class SavingsAccount(BankAccount):

    def calculate_interest(self):
        return self.get_balance() * 0.05


class CurrentAccount(BankAccount):

    def calculate_interest(self):
        return self.get_balance() * 0.02


class SalaryAccount(BankAccount):

    def calculate_interest(self):
        return self.get_balance() * 0.08
