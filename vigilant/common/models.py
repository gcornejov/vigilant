from __future__ import annotations

from pydantic import BaseModel


class AccountData(BaseModel):
    identifier: str
    amount: int
    transactions: list[Transaction]


class Transaction(BaseModel):
    date: str
    description: str
    location: str
    amount: int

    def to_list(self) -> list[str, int]:
        """Transforms transaction data into a list

        Returns:
            list[str, int]: Transaction data as a list
        """
        return list(self.model_dump().values())
