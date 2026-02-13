from vigilant.common.models import Transaction


def test_account_report_amount() -> None:
    from vigilant.common.models import AccountData, AccountReport

    report = AccountReport(
        accounts=[
            AccountData(identifier="A", amount=100, transactions=[]),
            AccountData(identifier="B", amount=200, transactions=[]),
        ]
    )

    assert report.amount == 300


def test_account_report_transactions() -> None:
    from vigilant.common.models import AccountData, AccountReport

    report = AccountReport(
        accounts=[
            AccountData(
                identifier="A",
                amount=100,
                transactions=[
                    Transaction(
                        date="01/01/2023",
                        description="compra",
                        location="chile",
                        amount=100,
                    )
                ],
            ),
            AccountData(
                identifier="B",
                amount=200,
                transactions=[
                    Transaction(
                        date="02/01/2023",
                        description="compra2",
                        location="chile2",
                        amount=200,
                    )
                ],
            ),
        ]
    )

    assert report.transactions == [
        ["B", "02/01/2023", "compra2", "chile2", 200],
        ["A", "01/01/2023", "compra", "chile", 100],
    ]


def test_transactions_to_list() -> None:
    transaction_list: list[str, int] = ["01/01/0001", "compra", "chile", 100]

    transaction = Transaction(
        **dict(zip(["date", "description", "location", "amount"], transaction_list))
    )

    assert transaction.to_list() == transaction_list
