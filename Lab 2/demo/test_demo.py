import logging
from demo import BankAccount

LOGGER = logging.getLogger(__name__)


def test_deposit():
    LOGGER.info(f"Running deposit test.")
    account = BankAccount("Dagobert Duck", (12345678, 87654321, 00000000), 10)
    
    account.deposit(5)
    LOGGER.debug(account)
    assert account.balance == 15


def test_withdraw():
    LOGGER.info(f"Running withdraw test.")
    account = BankAccount("Dagobert Duck", (12345678, 87654321, 00000000), 10)
    
    account.withdraw(5)
    LOGGER.debug(account)
    assert account.balance == 5


def test_is_overdrawn_positive():
    LOGGER.info(f"Running withdraw test.")
    account = BankAccount("Dagobert Duck", (12345678, 87654321, 00000000), 10)
    
    account.withdraw(5)
    LOGGER.debug(account)
    assert account.is_overdrawn() == False
    

def test_is_overdrawn_negative():
    LOGGER.info(f"Running withdraw test.")
    account = BankAccount("Dagobert Duck", (12345678, 87654321, 00000000), 10)
    
    account.withdraw(15)
    LOGGER.debug(account)
    assert account.is_overdrawn() == True
