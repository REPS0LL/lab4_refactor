### Застосування шаблону проектування "Стратегія"
# та розробка через тестування (TDD) з модульними та інтеграційними тестами
# для системи обробки платежів

from payment_strategies import (
    CreditCardPaymentStrategy,
    PayPalPaymentStrategy,
    CryptoPaymentStrategy,
    PaymentStrategy
)
from payment_processor import PaymentProcessor
from typing import List, Optional

saved_payment_methods: List[PaymentStrategy] = []
processor = PaymentProcessor()


def display_main_menu():
    print("\nГоловне меню:")
    print("1. Додати новий платіжний метод")
    print("2. Переглянути збережені платіжні методи")
    print("3. Здійснити платіж")
    print("4. Поповнити баланс рахунку")  # Змінено текст
    print("5. Вихід")


def display_add_method_menu():
    print("\nОберіть тип платіжного методу для додавання:")
    print("1. Кредитна картка")
    print("2. PayPal")
    print("3. Криптовалютний гаманець")
    print("0. Повернутися до головного меню")


def get_initial_balance_from_user() -> float:
    """Запитує у користувача початковий баланс та валідує його."""
    while True:
        initial_balance_str = input("Введіть початковий баланс (наприклад, 100.00, Enter для 0): ")
        if not initial_balance_str:
            return 0.0
        try:
            initial_balance = float(initial_balance_str)
            if initial_balance < 0:
                print("Початковий баланс не може бути негативним. Спробуйте ще раз.")
                continue
            return initial_balance
        except ValueError:
            print("Некоректний формат балансу. Введіть число (наприклад, 50.25).")


def handle_add_credit_card():
    print("\n--- Додавання кредитної картки ---")
    try:
        card_number = input("Введіть номер картки: ")
        expiry_date = input("Введіть термін дії (ММ/РР): ")
        cvv = input("Введіть CVV/CVC: ")
        if not card_number or not expiry_date or not cvv:
            print("Помилка: Всі поля картки є обов'язковими.")
            return
        initial_balance = get_initial_balance_from_user()
        strategy = CreditCardPaymentStrategy(card_number, expiry_date, cvv, initial_balance)
        saved_payment_methods.append(strategy)
        print(f"Кредитна картка ...{card_number[-4:]} додана. Баланс: ${strategy.balance:.2f}")
    except ValueError as e:
        print(f"Помилка: {e}")
    except Exception as e:
        print(f"Невідома помилка: {e}")


def handle_add_paypal():
    print("\n--- Додавання PayPal акаунту ---")
    try:
        email = input("Введіть email для PayPal: ")
        if not email:
            print("Помилка: Email є обов'язковим.")
            return
        initial_balance = get_initial_balance_from_user()  # Запитуємо баланс
        strategy = PayPalPaymentStrategy(email, initial_balance)  # Передаємо баланс
        saved_payment_methods.append(strategy)
        print(f"PayPal акаунт {email} доданий. Баланс: ${strategy.balance:.2f}")
    except ValueError as e:
        print(f"Помилка: {e}")
    except Exception as e:
        print(f"Невідома помилка: {e}")


def handle_add_crypto_wallet():
    print("\n--- Додавання криптовалютного гаманця ---")
    try:
        wallet_address = input("Введіть адресу криптовалютного гаманця: ")
        if not wallet_address:
            print("Помилка: Адреса гаманця є обов'язковою.")
            return
        initial_balance = get_initial_balance_from_user()  # Запитуємо баланс
        strategy = CryptoPaymentStrategy(wallet_address, initial_balance)  # Передаємо баланс
        saved_payment_methods.append(strategy)
        print(f"Крипто-гаманець {wallet_address[:6]}... доданий. Баланс: ${strategy.balance:.2f}")
    except ValueError as e:
        print(f"Помилка: {e}")
    except Exception as e:
        print(f"Невідома помилка: {e}")


def list_saved_methods(filter_for_add_funds: bool = False) -> List[PaymentStrategy]:
    """
    Відображає список збережених платіжних методів.
    Якщо filter_for_add_funds=True, показує тільки ті, що підтримують add_funds.
    Повертає список відображених методів.
    """
    print("\n--- Збережені платіжні методи ---")

    displayable_methods = []
    if filter_for_add_funds:
        for method in saved_payment_methods:
            # Перевіряємо, чи метод не є базовим PaymentStrategy і чи він перевизначив add_funds
            # або чи це CreditCardPaymentStrategy, яка точно має add_funds
            # Простіший спосіб: перевірити, чи метод повертає щось інше, ніж False від базового класу
            # Але для наочності зробимо явну перевірку на типи, які ми точно зробили поповнюваними
            if isinstance(method, (CreditCardPaymentStrategy, PayPalPaymentStrategy, CryptoPaymentStrategy)):
                displayable_methods.append(method)
    else:
        displayable_methods = list(saved_payment_methods)

    if not displayable_methods:
        if filter_for_add_funds:
            print("У вас немає рахунків, які можна поповнити.")
        else:
            print("У вас ще немає збережених платіжних методів.")
        return []

    for i, method in enumerate(displayable_methods):
        method_type_name = method.__class__.__name__.replace("PaymentStrategy", "")
        balance_info = method.get_balance_info()
        details = ""

        if isinstance(method, CreditCardPaymentStrategy):
            details = f"Картка ...{method.card_number[-4:]}"
        elif isinstance(method, PayPalPaymentStrategy):
            details = f"PayPal: {method.email}"
        elif isinstance(method, CryptoPaymentStrategy):
            details = f"Гаманець: {method.wallet_address[:6]}..."

        if balance_info:
            details += f", {balance_info}"

        print(f"{i + 1}. {method_type_name} ({details})")
    return displayable_methods


def handle_add_funds():  # Перейменовано з handle_add_funds_to_card
    """Обробляє поповнення балансу обраного рахунку."""
    print("\n--- Поповнення балансу рахунку ---")

    # Показуємо тільки ті методи, які підтримують поповнення
    accounts_to_fund = list_saved_methods(filter_for_add_funds=True)
    if not accounts_to_fund:
        print("--> Немає рахунків для поповнення. Повернення до головного меню.")
        return

    try:
        choice_str = input(f"Оберіть номер рахунку для поповнення (1-{len(accounts_to_fund)}): ")
        if not choice_str.isdigit():
            print("Некоректний вибір. Будь ласка, введіть число.")
            return

        account_index = int(choice_str) - 1
        if not (0 <= account_index < len(accounts_to_fund)):
            print("Некоректний номер рахунку.")
            return

        selected_account = accounts_to_fund[account_index]

        amount_str = input("Введіть суму для поповнення: ")
        if not amount_str.replace('.', '', 1).isdigit() or float(amount_str) <= 0:
            print("Некоректна сума. Сума має бути позитивним числом.")
            return

        amount_to_add = float(amount_str)

        # Викликаємо метод add_funds, який тепер є у всіх потрібних стратегіях
        if selected_account.add_funds(amount_to_add):
            print("Поповнення успішне!")
        else:
            # Повідомлення про помилку буде виведено з самого методу add_funds
            pass

    except ValueError:
        print("Помилка: Будь ласка, введіть числове значення для вибору або суми.")
    except Exception as e:
        print(f"Невідома помилка під час поповнення: {e}")


def handle_make_payment():
    print("\n--- Здійснення платежу ---")

    available_methods = list_saved_methods()
    if not available_methods:
        print("--> У вас немає збережених платіжних методів. Додайте спочатку метод.")
        return

    try:
        choice_str = input(f"Оберіть номер платіжного методу (1-{len(available_methods)}): ")
        if not choice_str.isdigit():
            print("Некоректний вибір.")
            return

        method_index = int(choice_str) - 1
        if not (0 <= method_index < len(available_methods)):
            print("Некоректний номер методу.")
            return

        selected_strategy = available_methods[method_index]
        processor.set_strategy(selected_strategy)

        # Для крипто, amount_to_send це сума яку отримає отримувач
        # Для інших - загальна сума списання
        prompt_message = "Введіть суму платежу: "
        if isinstance(selected_strategy, CryptoPaymentStrategy):
            prompt_message = "Введіть суму, яку має отримати отримувач (комісія буде додана): "

        amount_str = input(prompt_message)
        if not amount_str.replace('.', '', 1).isdigit() or float(amount_str) <= 0:
            print("Некоректна сума.")
            return

        amount = float(amount_str)

        print(f"\nОбробка платежу...")
        if processor.process_payment(amount):
            print(">>>> Платіж успішно оброблено! <<<<")
        else:
            print(">>>> Не вдалося обробити платіж. <<<<")

    except ValueError:
        print("Помилка: Будь ласка, введіть числове значення.")
    except Exception as e:
        print(f"Невідома помилка: {e}")


def main_loop():
    while True:
        display_main_menu()
        choice = input("Ваш вибір: ")

        if choice == '1':
            # ... (код додавання методів залишається тим же)
            while True:
                display_add_method_menu()
                method_choice = input("Оберіть тип методу: ")
                if method_choice == '1':
                    handle_add_credit_card()
                elif method_choice == '2':
                    handle_add_paypal()
                elif method_choice == '3':
                    handle_add_crypto_wallet()
                elif method_choice == '0':
                    break
                else:
                    print("Некоректний вибір, спробуйте ще раз.")
        elif choice == '2':
            list_saved_methods()
        elif choice == '3':
            handle_make_payment()
        elif choice == '4':
            handle_add_funds()  # Викликаємо узагальнену функцію
        elif choice == '5':
            print("Дякуємо за використання програми! До побачення.")
            break
        else:
            print("Некоректний вибір, спробуйте ще раз.")


if __name__ == "__main__":
    print("Вітаємо у консольній програмі керування платежами!")
    main_loop()