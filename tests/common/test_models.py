from vigilant.common.models import Transaction


def test_transactions_to_list() -> None:
    transaction_list: list[str, int] = ["01/01/0001", "compra", "chile", 100]

    transaction = Transaction(
        **dict(zip(["date", "description", "location", "amount"], transaction_list))
    )

    assert transaction.to_list() == transaction_list
