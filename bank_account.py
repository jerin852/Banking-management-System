
from abc import ABC, abstractmethod


class BankAccount(ABC):

    def __init__(self, name, balance):
        if balance < 0:
            raise ValueError("Initial balance cannot be negative")

        self.name = name
        self.__balance = round(float(balance), 2)

    def deposit(self, amount):
        amount = float(amount)

        if amount <= 0:
            raise ValueError("Deposit amount must be positive")

        self.__balance = round(self.__balance + amount, 2)

        return self.__balance

    def withdraw(self, amount):
        amount = float(amount)

        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")

        if amount > self.__balance:
            raise ValueError("Insufficient balance")

        self.__balance = round(self.__balance - amount, 2)

        return self.__balance

    def get_balance(self):
        return self.__balance

    @abstractmethod
    def calculate_interest(self):
        pass


class SavingsAccount(BankAccount):

    def calculate_interest(self):
        return round(self.get_balance() * 0.05, 2)
