from datetime import datetime, timedelta
from typing import Any
from pathlib import Path

import pandas as pd

from vigilant.common.values import Documents


class Transactions:
    data_path: Path
    column_idx: tuple[int, ...]
    column_names: tuple[str, ...]
    header_idx: int
    sheet_name: int

    filter_map: dict[str, Any] | None = None

    data = pd.DataFrame

    def __init__(
        self,
        bank: str,
        origin: str,
        data_path: Path,
        column_idx: tuple[int, ...],
        column_names: tuple[str, ...],
        header_idx: int,
        sheet_name: int = 0,
        filter_map: dict[str, Any] | None = None,
    ) -> None:
        """Loads, transforms and tags transactions data from an excel file

        Args:
            bank (str): Bank where the transactions came
            origin (str): Account where the transactions came (Checking account, Credit, etc.)
            data_path (Path): Path of the transactions file
            column_idx (tuple[int, ...]): Index to locate each data column
            column_names (tuple[str, ...]): Name for each data column
            header_idx (int): Row index of data header
            sheet_name (int, optional): Index of the sheet where the data is located. Defaults to 0.
            filter_map (dict[str, Any] | None, optional): Map of column and values to filter matching rows. Defaults to None.
        """
        self.bank = bank
        self.origin = origin

        self.data_path = data_path
        self.column_idx = column_idx
        self.column_names = column_names
        self.header_idx = header_idx
        self.sheet_name = sheet_name

        self.filter_map = filter_map or {}

    def load(self) -> pd.DataFrame:
        """Loads, transforms and tags transactions data

        Returns:
            pd.DataFrame: Transactions data
        """
        self._read()
        self._mutate()

        data_size: int = len(self.data)
        self.data.insert(0, "bank", [self.bank] * data_size)
        self.data.insert(1, "origin", [self.origin] * data_size)
        self.data.insert(2, "label", ["-"] * data_size)

        return self.data

    def _read(self) -> None:
        """Private method which calls read implementation"""
        self.read()

    def _mutate(self) -> None:
        """Private method which calls mutate implementation"""
        self.mutate()

    def read(self) -> None:
        """Reads transactions data from an excel file"""
        self.data = pd.read_excel(
            self.data_path,
            sheet_name=self.sheet_name,
            header=self.header_idx,
            names=self.column_names,
            usecols=self.column_idx,
        )

    def mutate(self) -> None:
        """Filters rows based on matched values defined in the filter map.
        It can be overwritten by a Child class to extend functionality.
        """
        for column, values in self.filter_map.items():
            self.data = self.data[~self.data[column].isin(values)]

    def to_list(self) -> list[list[str]]:
        """Exports transactions data to list."""
        return self.data.fillna("").values.tolist()


class Checking(Transactions):
    def __init__(self) -> None:
        super().__init__(
            bank="CL",
            origin="CA",
            data_path=Documents.CHECKING_CARD,
            column_idx=tuple(range(1, 6)),
            column_names=("date", "description", "location", "charge", "payment"),
            header_idx=26,
            filter_map={
                "description": ("Cargo Por Pago Tc", "Pago Tarjeta De Credito")
            },
        )

    def mutate(self) -> None:
        super().mutate()

        self.data = self.data[
            ~(self.data["charge"].isna() & self.data["payment"].isna())
        ]

        last_week_start = datetime.now() - timedelta(weeks=1)
        self.data["date"] = pd.to_datetime(self.data["date"], dayfirst=True)

        self.data = self.data.loc[self.data["date"] >= last_week_start]
        self.data["date"] = self.data["date"].dt.strftime("%d/%m/%Y")

        self.data["amount"] = self.data["charge"].combine_first(self.data["payment"])
        self.data.drop(["charge", "payment"], axis=1, inplace=True)


class NationalCredit(Transactions):
    def __init__(self) -> None:
        super().__init__(
            bank="CL",
            origin="CN",
            data_path=Documents.NATIONAL_CREDIT,
            column_idx=(1, 4, 6, 10),
            column_names=("date", "description", "location", "amount"),
            header_idx=17,
            filter_map={
                "description": (
                    "TEF PAGO NORMAL",
                    "Pago Pesos TAR",
                    "Pago Pesos TEF PAGO NORMAL",
                )
            },
        )


class InternationalCredit(Transactions):
    def __init__(self) -> None:
        super().__init__(
            bank="CL",
            origin="CI",
            data_path=Documents.INTERNATIONAL_CREDIT,
            column_idx=(1, 4, 6, 8),
            column_names=("date", "description", "location", "amount"),
            header_idx=17,
            filter_map={"description": ("Pago Dolar TEF",)},
        )
