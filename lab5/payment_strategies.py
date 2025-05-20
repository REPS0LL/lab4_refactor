from abc import ABC, abstractmethod
import re
from typing import Optional


class PaymentStrategy(ABC):
    @abstractmethod
    def pay(self, amount: float) -> bool:
        pass

    def get_balance_info(self) -> Optional[str]:
        return None

    def add_funds(self, amount: float) -> bool:
        print(f"Метод {self.__class__.__name__} не підтримує пряме поповнення балансу.")
        return False


class CreditCardPaymentStrategy(PaymentStrategy):
    def __init__(self, card_number: str, expiry_date: str, cvv: str, initial_balance: float = 0.0):
        if not (card_number and expiry_date and cvv):
            raise ValueError("Номер картки, термін дії та CVV мають бути надані.")
        self.card_number = card_number
        self.expiry_date = expiry_date
        self.cvv = cvv
        if initial_balance < 0:
            raise ValueError("Початковий баланс не може бути негативним.")
        self.balance = initial_balance
        print(
            f"CreditCardPaymentStrategy ініціалізовано для картки {self.card_number[-4:]}. Баланс: ${self.balance:.2f}")

    def add_funds(self, amount: float) -> bool:
        if amount <= 0:
            print("Сума поповнення має бути позитивною.")
            return False
        self.balance += amount
        print(f"Баланс картки {self.card_number[-4:]} поповнено на ${amount:.2f}. Новий баланс: ${self.balance:.2f}")
        return True

    def pay(self, amount: float) -> bool:
        if amount <= 0:
            print("Сума платежу має бути позитивною.")
            return False
        print(f"Спроба списання ${amount:.2f} з картки {self.card_number[-4:]} (Баланс: ${self.balance:.2f})...")
        if amount > self.balance:
            print(
                f"Недостатньо коштів на картці {self.card_number[-4:]}. Потрібно: ${amount:.2f}, доступно: ${self.balance:.2f}")
            return False
        self.balance -= amount
        print(f"Списання ${amount:.2f} з картки {self.card_number[-4:]} успішне. Новий баланс: ${self.balance:.2f}")
        return True

    def get_balance_info(self) -> Optional[str]:
        return f"Баланс: ${self.balance:.2f}"


class PayPalPaymentStrategy(PaymentStrategy):
    def __init__(self, email: str, initial_balance: float = 0.0):  # Додано initial_balance
        if not self._is_valid_email(email):
            raise ValueError(f"Некоректний формат PayPal email: {email}")
        self.email = email
        if initial_balance < 0:
            raise ValueError("Початковий баланс не може бути негативним.")
        self.balance = initial_balance  # Додано атрибут balance
        print(f"PayPalPaymentStrategy ініціалізовано для email: {self.email}. Баланс: ${self.balance:.2f}")

    def _is_valid_email(self, email: str) -> bool:
        return bool(re.fullmatch(r"[^@]+@[^@]+\.[^@]+", email))

    def add_funds(self, amount: float) -> bool:
        if amount <= 0:
            print("Сума поповнення має бути позитивною.")
            return False
        self.balance += amount
        print(f"Баланс PayPal акаунту {self.email} поповнено на ${amount:.2f}. Новий баланс: ${self.balance:.2f}")
        return True

    def pay(self, amount: float) -> bool:
        if amount <= 0:
            print("Сума платежу має бути позитивною для PayPal.")
            return False
        print(f"Спроба PayPal платежу ${amount:.2f} для {self.email} (Баланс: ${self.balance:.2f})...")
        if amount > self.balance:
            print(
                f"Недостатньо коштів на PayPal акаунті {self.email}. Потрібно: ${amount:.2f}, доступно: ${self.balance:.2f}")
            return False
        self.balance -= amount
        print(f"PayPal платіж ${amount:.2f} для {self.email} успішний. Новий баланс: ${self.balance:.2f}")
        return True

    def get_balance_info(self) -> Optional[str]:
        return f"Баланс: ${self.balance:.2f}"


class CryptoPaymentStrategy(PaymentStrategy):
    MIN_FEE_PERCENTAGE_OF_AMOUNT = 0.005  # 0.5% від суми як мін. комісія
    MIN_ABSOLUTE_FEE = 0.1  # Мінімальна абсолютна комісія в $
    MAX_ABSOLUTE_FEE = 5.0  # Максимальна абсолютна комісія в $

    def __init__(self, wallet_address: str, initial_balance: float = 0.0):  # Додано initial_balance
        if not wallet_address or len(wallet_address) < 26:
            raise ValueError("Надано некоректну або занадто коротку адресу крипто-гаманця.")
        self.wallet_address = wallet_address
        if initial_balance < 0:
            raise ValueError("Початковий баланс не може бути негативним.")
        self.balance = initial_balance  # Додано атрибут balance
        print(
            f"CryptoPaymentStrategy ініціалізовано для гаманця {self.wallet_address[:10]}... Баланс: ${self.balance:.2f}")

    def _calculate_fee(self, amount_to_send: float) -> float:
        # Комісія розраховується від суми, яку користувач хоче саме ВІДПРАВИТИ отримувачу
        # Це відрізняється від попередньої логіки, де комісія була від загальної суми
        fee_from_percentage = amount_to_send * self.MIN_FEE_PERCENTAGE_OF_AMOUNT
        calculated_fee = max(self.MIN_ABSOLUTE_FEE, fee_from_percentage)
        final_fee = min(calculated_fee, self.MAX_ABSOLUTE_FEE)
        return final_fee

    def add_funds(self, amount: float) -> bool:  # Додано метод add_funds
        if amount <= 0:
            print("Сума поповнення має бути позитивною.")
            return False
        self.balance += amount
        print(
            f"Баланс крипто-гаманця {self.wallet_address[:10]}... поповнено на ${amount:.2f}. Новий баланс: ${self.balance:.2f}")
        return True

    def pay(self, amount_to_send: float) -> bool:  # Оновлено метод pay
        if amount_to_send <= 0:
            print("Сума відправлення має бути позитивною для Крипто платежу.")
            return False

        fee = self._calculate_fee(amount_to_send)
        total_to_debit = amount_to_send + fee

        print(f"Спроба крипто-платежу: відправити ${amount_to_send:.2f} на {self.wallet_address[:10]}...")
        print(
            f"Розрахована комісія: ${fee:.2f}. Загалом до списання: ${total_to_debit:.2f}. (Баланс: ${self.balance:.2f})")

        if total_to_debit > self.balance:
            print(
                f"Недостатньо коштів на крипто-гаманці. Потрібно: ${total_to_debit:.2f}, доступно: ${self.balance:.2f}")
            return False

        self.balance -= total_to_debit
        print(f"Крипто-платіж: ${amount_to_send:.2f} відправлено на {self.wallet_address[:10]} (комісія ${fee:.2f}).")
        print(f"Новий баланс гаманця: ${self.balance:.2f}")
        return True

    def get_balance_info(self) -> Optional[str]:  # Додано метод get_balance_info
        return f"Баланс: ${self.balance:.2f}"