from typing import Optional
from payment_strategies import PaymentStrategy

class PaymentProcessor:
    """
    Клас-контекст, який використовує обрану стратегію для обробки платежу.
    """
    def __init__(self, strategy: Optional[PaymentStrategy] = None):
        self._strategy = strategy
        if strategy:
            print(f"PaymentProcessor initialized with strategy: {strategy.__class__.__name__}")
        else:
            print("PaymentProcessor initialized without a default strategy.")


    def set_strategy(self, strategy: PaymentStrategy):
        self._strategy = strategy
        print(f"Payment strategy set to: {strategy.__class__.__name__}")


    def process_payment(self, amount: float) -> bool:
        if not self._strategy:
            print("Error: Payment strategy not set.")
            return False
        if amount <= 0:
            print("Error: Payment amount must be positive.")
            return False

        print(f"PaymentProcessor attempting to process payment of ${amount:.2f}...")
        try:
            return self._strategy.pay(amount)
        except Exception as e:
            print(f"Error during payment processing with {self._strategy.__class__.__name__}: {e}")
            return False