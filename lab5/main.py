# main.py
from payment_strategies import (
    CreditCardPaymentStrategy,
    PayPalPaymentStrategy,
    CryptoPaymentStrategy
)
from payment_processor import PaymentProcessor

def demonstrate_payments():
    print("--- Демонстрація роботи системи платежів ---")

    # Створення стратегій
    try:
        cc_strategy = CreditCardPaymentStrategy("1111222233334444", "12/28", "123")
        pp_strategy = PayPalPaymentStrategy("demo_user@example.com")
        crypto_strategy = CryptoPaymentStrategy("bc1qdemouseraddressfordemonstrationpurposes") # Вигадана адреса
    except ValueError as e:
        print(f"Помилка ініціалізації стратегії: {e}")
        return

    # Створення процесора платежів
    processor = PaymentProcessor()

    # --- Платіж кредитною карткою ---
    print("\n1. Спроба платежу кредитною карткою:")
    processor.set_strategy(cc_strategy)
    amount_cc = 150.75
    if processor.process_payment(amount_cc):
        print(f">>>> Головна програма: Платіж ${amount_cc:.2f} кредитною карткою успішний.")
    else:
        print(f">>>> Головна програма: Платіж ${amount_cc:.2f} кредитною карткою НЕ успішний.")

    # --- Платіж PayPal ---
    print("\n2. Спроба платежу PayPal:")
    processor.set_strategy(pp_strategy)
    amount_pp = 75.50
    if processor.process_payment(amount_pp):
        print(f">>>> Головна програма: Платіж ${amount_pp:.2f} через PayPal успішний.")
    else:
        print(f">>>> Головна програма: Платіж ${amount_pp:.2f} через PayPal НЕ успішний.")

    # --- Платіж криптовалютою (успішний) ---
    print("\n3. Спроба платежу криптовалютою (достатня сума):")
    processor.set_strategy(crypto_strategy)
    amount_crypto_ok = 200.00
    if processor.process_payment(amount_crypto_ok):
        print(f">>>> Головна програма: Платіж ${amount_crypto_ok:.2f} криптовалютою успішний.")
    else:
        print(f">>>> Головна програма: Платіж ${amount_crypto_ok:.2f} криптовалютою НЕ успішний.")

    # --- Платіж криптовалютою (недостатня сума для комісії) ---
    print("\n4. Спроба платежу криптовалютою (недостатня сума):")
    processor.set_strategy(crypto_strategy) # Стратегія вже встановлена, але для наочності
    amount_crypto_fail = 0.30 # Менше мінімальної комісії
    if processor.process_payment(amount_crypto_fail):
        print(f">>>> Головна програма: Платіж ${amount_crypto_fail:.2f} криптовалютою успішний.")
    else:
        print(f">>>> Головна програма: Платіж ${amount_crypto_fail:.2f} криптовалютою НЕ успішний.")

    # --- Спроба платежу без встановленої стратегії ---
    print("\n5. Спроба платежу без встановленої стратегії (після скидання):")
    # Створимо новий процесор або "скинемо" стратегію (у поточній реалізації немає методу скидання)
    new_processor = PaymentProcessor()
    amount_no_strategy = 10.0
    if new_processor.process_payment(amount_no_strategy):
        print(f">>>> Головна програма: Платіж ${amount_no_strategy:.2f} без стратегії успішний (неочікувано).")
    else:
        print(f">>>> Головна програма: Платіж ${amount_no_strategy:.2f} без стратегії НЕ успішний (очікувано).")

    print("\n--- Демонстрація завершена ---")

if __name__ == "__main__":
    demonstrate_payments()