import pytest
from payment_strategies import (
    CreditCardPaymentStrategy,
    PayPalPaymentStrategy,
    CryptoPaymentStrategy,
    PaymentStrategy
)
from payment_processor import PaymentProcessor
from unittest.mock import MagicMock

# CreditCardPaymentStrategy

def test_cc_creation_ok():
    strategy = CreditCardPaymentStrategy("1234567812345678", "12/25", "123", initial_balance=100.0)
    assert isinstance(strategy, PaymentStrategy)
    assert strategy.card_number == "1234567812345678"
    assert strategy.balance == 100.0
    assert "Баланс: $100.00" in strategy.get_balance_info()

def test_cc_creation_default_balance():
    strategy = CreditCardPaymentStrategy("1111222233334444", "01/26", "000") # initial_balance = 0.0 за замовчуванням
    assert strategy.balance == 0.0

def test_cc_creation_invalid_details():
    with pytest.raises(ValueError, match="Номер картки, термін дії та CVV мають бути надані."):
        CreditCardPaymentStrategy("", "12/25", "123", 100.0)

def test_cc_creation_negative_initial_balance():
    with pytest.raises(ValueError, match="Початковий баланс не може бути негативним."):
        CreditCardPaymentStrategy("1234567812345678", "12/25", "123", initial_balance=-50.0)

def test_cc_add_funds():
    strategy = CreditCardPaymentStrategy("1111", "01/26", "000", initial_balance=50.0)
    assert strategy.add_funds(50.0) is True
    assert strategy.balance == 100.0
    assert strategy.add_funds(0.0) is False # Не можна поповнити на 0
    assert strategy.balance == 100.0
    assert strategy.add_funds(-10.0) is False # Не можна поповнити на негативну суму
    assert strategy.balance == 100.0

def test_cc_pay_successful():
    strategy = CreditCardPaymentStrategy("1111", "01/26", "000", initial_balance=150.0)
    assert strategy.pay(100.0) is True
    assert strategy.balance == 50.0

def test_cc_pay_insufficient_funds():
    strategy = CreditCardPaymentStrategy("1111", "01/26", "000", initial_balance=50.0)
    assert strategy.pay(100.0) is False
    assert strategy.balance == 50.0 # Баланс не змінився

def test_cc_pay_zero_amount():
    strategy = CreditCardPaymentStrategy("1111", "01/26", "000", initial_balance=100.0)
    assert strategy.pay(0.0) is False
    assert strategy.balance == 100.0

def test_cc_pay_negative_amount():
    strategy = CreditCardPaymentStrategy("1111", "01/26", "000", initial_balance=100.0)
    assert strategy.pay(-50.0) is False
    assert strategy.balance == 100.0

#  PayPalPaymentStrategy ---

def test_paypal_creation_ok():
    strategy = PayPalPaymentStrategy("test@example.com", initial_balance=50.0)
    assert isinstance(strategy, PaymentStrategy)
    assert strategy.email == "test@example.com"
    assert strategy.balance == 50.0
    assert "Баланс: $50.00" in strategy.get_balance_info()

def test_paypal_creation_default_balance():
    strategy = PayPalPaymentStrategy("another@example.com") # initial_balance = 0.0
    assert strategy.balance == 0.0

def test_paypal_creation_invalid_email():
    with pytest.raises(ValueError, match=r"Некоректний формат PayPal email: testexample\.com"):
        PayPalPaymentStrategy("testexample.com", 100.0)

def test_paypal_creation_negative_initial_balance():
    with pytest.raises(ValueError, match="Початковий баланс не може бути негативним."):
        PayPalPaymentStrategy("test@example.com", initial_balance=-20.0)

def test_paypal_add_funds():
    strategy = PayPalPaymentStrategy("test@example.com", initial_balance=20.0)
    assert strategy.add_funds(30.0) is True
    assert strategy.balance == 50.0
    assert strategy.add_funds(0) is False
    assert strategy.balance == 50.0

def test_paypal_pay_successful():
    strategy = PayPalPaymentStrategy("user@domain.com", initial_balance=100.0)
    assert strategy.pay(50.0) is True
    assert strategy.balance == 50.0

def test_paypal_pay_insufficient_funds():
    strategy = PayPalPaymentStrategy("user@domain.com", initial_balance=30.0)
    assert strategy.pay(50.0) is False
    assert strategy.balance == 30.0

def test_paypal_pay_zero_amount():
    strategy = PayPalPaymentStrategy("user@domain.com", initial_balance=50.0)
    assert strategy.pay(0) is False
    assert strategy.balance == 50.0

# CryptoPaymentStrategy

VALID_CRYPTO_ADDRESS = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa" # Length 34

def test_crypto_creation_ok():
    strategy = CryptoPaymentStrategy(VALID_CRYPTO_ADDRESS, initial_balance=1.0) # $1.0
    assert isinstance(strategy, PaymentStrategy)
    assert strategy.wallet_address == VALID_CRYPTO_ADDRESS
    assert strategy.balance == 1.0
    assert "Баланс: $1.00" in strategy.get_balance_info()

def test_crypto_creation_default_balance():
    strategy = CryptoPaymentStrategy(VALID_CRYPTO_ADDRESS) # initial_balance = 0.0
    assert strategy.balance == 0.0

def test_crypto_creation_invalid_address_short():
    with pytest.raises(ValueError, match="Надано некоректну або занадто коротку адресу крипто-гаманця."):
        CryptoPaymentStrategy("short", 10.0)

def test_crypto_creation_negative_initial_balance():
     with pytest.raises(ValueError, match="Початковий баланс не може бути негативним."):
        CryptoPaymentStrategy(VALID_CRYPTO_ADDRESS, initial_balance=-1.0)

def test_crypto_add_funds():
    strategy = CryptoPaymentStrategy(VALID_CRYPTO_ADDRESS, initial_balance=0.5)
    assert strategy.add_funds(1.5) is True
    assert strategy.balance == 2.0
    assert strategy.add_funds(0) is False
    assert strategy.balance == 2.0

def test_crypto_pay_successful_with_fee():
    # amount_to_send = $10.
    # fee_from_percentage = 10 * 0.005 = $0.05.
    # calculated_fee = max(0.1 (MIN_ABSOLUTE_FEE), 0.05) = $0.1.
    # final_fee = min(0.1, 5.0 (MAX_ABSOLUTE_FEE)) = $0.1.
    # total_to_debit = 10 + 0.1 = $10.1.
    strategy = CryptoPaymentStrategy(VALID_CRYPTO_ADDRESS, initial_balance=15.0)
    assert strategy.pay(amount_to_send=10.0) is True
    assert strategy.balance == pytest.approx(15.0 - 10.1) # 4.9

def test_crypto_pay_insufficient_funds_for_amount_and_fee():
    # amount_to_send = $1.0. fee = $0.1. total_to_debit = $1.1.
    strategy = CryptoPaymentStrategy(VALID_CRYPTO_ADDRESS, initial_balance=1.0) # Баланс менший за суму + комісія
    assert strategy.pay(amount_to_send=1.0) is False
    assert strategy.balance == 1.0 # Баланс не змінився

def test_crypto_pay_amount_to_send_results_in_high_fee_relative_to_amount():
    # amount_to_send = $0.01.
    # fee_from_percentage = 0.01 * 0.005 = $0.00005.
    # calculated_fee = max(0.1 (MIN_ABSOLUTE_FEE), 0.00005) = $0.1.
    # final_fee = $0.1.
    # total_to_debit = 0.01 + 0.1 = $0.11.
    strategy = CryptoPaymentStrategy(VALID_CRYPTO_ADDRESS, initial_balance=1.0)
    assert strategy.pay(amount_to_send=0.01) is True
    assert strategy.balance == pytest.approx(1.0 - 0.11) # 0.89

def test_crypto_pay_zero_amount_to_send():
    strategy = CryptoPaymentStrategy(VALID_CRYPTO_ADDRESS, initial_balance=1.0)
    assert strategy.pay(amount_to_send=0.0) is False
    assert strategy.balance == 1.0

def test_crypto_get_balance_info():
    strategy = CryptoPaymentStrategy(VALID_CRYPTO_ADDRESS, 123.45)
    assert strategy.get_balance_info() == "Баланс: $123.45"

#  PaymentProcessor

def test_payment_processor_creation_no_strategy():
    processor = PaymentProcessor()
    assert processor._strategy is None # Доступ до _strategy для тестування, хоча це "приватне" поле

def test_payment_processor_creation_with_strategy():
    mock_strategy = MagicMock(spec=PaymentStrategy)
    processor = PaymentProcessor(mock_strategy)
    assert processor._strategy == mock_strategy

def test_payment_processor_set_strategy():
    processor = PaymentProcessor()
    mock_strategy = MagicMock(spec=PaymentStrategy)
    processor.set_strategy(mock_strategy)
    assert processor._strategy == mock_strategy

def test_payment_processor_process_payment_no_strategy():
    processor = PaymentProcessor()
    assert processor.process_payment(100.0) is False

def test_payment_processor_process_payment_with_mock_strategy_success():
    mock_strategy = MagicMock(spec=PaymentStrategy)
    mock_strategy.pay.return_value = True
    processor = PaymentProcessor(mock_strategy)
    assert processor.process_payment(100.0) is True
    mock_strategy.pay.assert_called_once_with(100.0)

def test_payment_processor_process_payment_with_mock_strategy_failure():
    mock_strategy = MagicMock(spec=PaymentStrategy)
    mock_strategy.pay.return_value = False
    processor = PaymentProcessor(mock_strategy)
    assert processor.process_payment(50.0) is False
    mock_strategy.pay.assert_called_once_with(50.0)

def test_payment_processor_process_payment_zero_amount_bypasses_strategy():
    # Процесор сам перевіряє суму перед викликом стратегії
    mock_strategy = MagicMock(spec=PaymentStrategy)
    processor = PaymentProcessor(mock_strategy)
    assert processor.process_payment(0.0) is False
    mock_strategy.pay.assert_not_called()

def test_payment_processor_process_payment_negative_amount_bypasses_strategy():
    mock_strategy = MagicMock(spec=PaymentStrategy)
    processor = PaymentProcessor(mock_strategy)
    assert processor.process_payment(-10.0) is False
    mock_strategy.pay.assert_not_called()

