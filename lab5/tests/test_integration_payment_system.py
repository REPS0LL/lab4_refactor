import pytest
from payment_strategies import (
    CreditCardPaymentStrategy,
    PayPalPaymentStrategy,
    CryptoPaymentStrategy
)
from payment_processor import PaymentProcessor

VALID_CRYPTO_ADDRESS_INTEG = "bc1qj8nferns9wf35s208vwedywudvxm76n2z8j9l3"

# Integration Tests

def test_integ_cc_payment_insufficient_funds():
    cc_strategy = CreditCardPaymentStrategy("2222333344445555", "10/26", "456", initial_balance=50.0)
    processor = PaymentProcessor(cc_strategy)
    assert processor.process_payment(100.0) is False
    assert cc_strategy.balance == 50.0 # Баланс не змінився

def test_integ_cc_payment_successful():
    cc_strategy = CreditCardPaymentStrategy("1111222233334444", "12/25", "123", initial_balance=200.0)
    processor = PaymentProcessor(cc_strategy)
    assert processor.process_payment(150.75) is True
    assert cc_strategy.balance == pytest.approx(200.0 - 150.75)


def test_integ_paypal_payment_successful():
    # ВАЖЛИВО: Вказуємо initial_balance
    paypal_strategy = PayPalPaymentStrategy("integ_user@test.co", initial_balance=100.0)
    processor = PaymentProcessor(paypal_strategy)
    assert processor.process_payment(75.25) is True
    assert paypal_strategy.balance == pytest.approx(100.0 - 75.25)

def test_integ_paypal_payment_insufficient_funds():
    paypal_strategy = PayPalPaymentStrategy("another_user@test.co", initial_balance=25.0)
    processor = PaymentProcessor(paypal_strategy)
    assert processor.process_payment(50.0) is False
    assert paypal_strategy.balance == 25.0

def test_integ_crypto_payment_successful():
    crypto_strategy = CryptoPaymentStrategy(VALID_CRYPTO_ADDRESS_INTEG, initial_balance=60.0)
    processor = PaymentProcessor(crypto_strategy)
    amount_to_send = 50.0
    fee = crypto_strategy._calculate_fee(amount_to_send)
    assert processor.process_payment(amount_to_send) is True # Правильно: передаємо amount_to_send як позиційний аргумент
    assert crypto_strategy.balance == pytest.approx(60.0 - (amount_to_send + fee))


def test_integ_crypto_payment_insufficient_funds():
    # amount_to_send = $10. fee = $0.1 (згідно з логікою CryptoPaymentStrategy._calculate_fee). total_debit = $10.1.
    crypto_strategy = CryptoPaymentStrategy(VALID_CRYPTO_ADDRESS_INTEG, initial_balance=10.0) # Балансу $10.0 не вистачить для $10.1
    processor = PaymentProcessor(crypto_strategy)
    assert processor.process_payment(10.0) is False # Виправлено тут: передаємо просто 10.0
    assert crypto_strategy.balance == 10.0 # Баланс не має змінитися

def test_integ_switching_strategies_and_payments():
    processor = PaymentProcessor()

    # ... (частина для Кредитної картки та PayPal залишається як була) ...

    # Кредитна картка
    cc_strategy = CreditCardPaymentStrategy("3333444455556666", "01/27", "789", initial_balance=100.0)
    processor.set_strategy(cc_strategy)
    assert processor.process_payment(50.0) is True, "Credit Card payment failed"
    assert cc_strategy.balance == 50.0

    # PayPal
    pp_strategy = PayPalPaymentStrategy("switch_user@example.org", initial_balance=100.0)
    processor.set_strategy(pp_strategy)
    assert processor.process_payment(75.0) is True, "PayPal payment after switching failed"
    assert pp_strategy.balance == 25.0

    # Криптовалюта
    # Ось тут виправлення: r_strategy -> cr_strategy
    cr_strategy = CryptoPaymentStrategy(VALID_CRYPTO_ADDRESS_INTEG, initial_balance=30.0)
    processor.set_strategy(cr_strategy)
    amount_to_send_crypto = 20.0
    # Розрахунок комісії має відбуватися для правильного екземпляра cr_strategy
    fee_crypto = cr_strategy._calculate_fee(amount_to_send_crypto)
    assert processor.process_payment(
        amount_to_send_crypto) is True, "Crypto payment after switching failed"
    assert cr_strategy.balance == pytest.approx(30.0 - (amount_to_send_crypto + fee_crypto))

    # Кредитна картка
    cc_strategy = CreditCardPaymentStrategy("3333444455556666", "01/27", "789", initial_balance=100.0)
    processor.set_strategy(cc_strategy)
    assert processor.process_payment(50.0) is True, "Credit Card payment failed"
    assert cc_strategy.balance == 50.0

    # PayPal
    pp_strategy = PayPalPaymentStrategy("switch_user@example.org", initial_balance=100.0)
    processor.set_strategy(pp_strategy)
    assert processor.process_payment(75.0) is True, "PayPal payment after switching failed"
    assert pp_strategy.balance == 25.0

    # Криптовалюта
    # amount_to_send = $20. fee (приклад) = $0.1
    # total_debit = $20.1
    cr_strategy = CryptoPaymentStrategy(VALID_CRYPTO_ADDRESS_INTEG, initial_balance=30.0)
    processor.set_strategy(cr_strategy)
    amount_to_send_crypto = 20.0
    fee_crypto = cr_strategy._calculate_fee(amount_to_send_crypto)
    assert processor.process_payment(amount_to_send_crypto) is True, "Crypto payment after switching failed"
    assert cr_strategy.balance == pytest.approx(30.0 - (amount_to_send_crypto + fee_crypto))

def test_integ_payment_with_no_strategy_set_in_processor():
    processor = PaymentProcessor()
    assert processor.process_payment(100.0) is False

def test_integ_payment_with_zero_amount():
    cc_strategy = CreditCardPaymentStrategy("4444555566667777", "02/28", "111", initial_balance=100.0)
    processor = PaymentProcessor(cc_strategy)
    assert processor.process_payment(0.0) is False
    assert cc_strategy.balance == 100.0



####
def test_integ_cc_payment_insufficient_funds():
    cc_strategy = CreditCardPaymentStrategy("2222333344445555", "10/26", "456", initial_balance=50.0)
    processor = PaymentProcessor(cc_strategy)
    assert processor.process_payment(100.0) is False # Очікуємо False
    assert cc_strategy.balance == 50.0 # Баланс не має змінитися

