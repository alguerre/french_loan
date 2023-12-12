import pandas as pd

from definitions import PartialAmortization


class LoanService:
    def __init__(
        self,
        borrowed_capital: int,
        eir: float,
        duration: int,
        partial_interest: float = 0.02,
    ):
        self.borrowed_capital = borrowed_capital
        self.eir = eir  # effective interest rate
        self.duration = duration  # years
        self.partial_interest = partial_interest  # interest for partial amortization

    @property
    def annuity(self) -> float:
        # yearly payment
        return round(
            self.borrowed_capital
            * self.eir
            * (1 + self.eir) ** self.duration
            / ((1 + self.eir) ** self.duration - 1),
            2,
        )

    def _compute_row(self, year: int, previous_row: dict) -> dict:
        interest = round(previous_row["outstanding_capital"] * self.eir, 2)
        amortized_capital = min(
            previous_row["outstanding_capital"],
            self.annuity - interest
        )
        outstanding_capital = previous_row["outstanding_capital"] - amortized_capital

        return {
            "year": int(year),
            "annuity": self.annuity,
            "interest": interest,
            "amortized_capital": amortized_capital,
            "outstanding_capital": outstanding_capital,
        }

    def _first_row(self) -> dict:
        return {
            "year": 0,
            "annuity": None,
            "interest": None,
            "amortized_capital": None,
            "outstanding_capital": self.borrowed_capital,
        }

    def get_amortization_table(self) -> pd.DataFrame:
        amortization = [self._first_row()]

        for year in range(1, self.duration + 1):
            amortization.append(
                self._compute_row(
                    year,
                    amortization[year - 1],
                )
            )

        return pd.DataFrame(amortization)

    def _compute_partial_row(self, year: int, partial: PartialAmortization, previous_row: dict):
        return {
            "year": int(year),
            "annuity": None,
            "interest": partial.capital * self.partial_interest,
            "amortized_capital": partial.capital,
            "outstanding_capital": previous_row["outstanding_capital"]
            - partial.capital,
        }

    def get_amortization_table_with_partials(
        self, partials: list[PartialAmortization]
    ) -> pd.DataFrame:
        amortization = [self._first_row()]

        for year in range(1, self.duration + 1):
            if partials and partials[0].year == year:
                partial = partials.pop(0)
                amortization.append(
                    self._compute_partial_row(
                        year,
                        partial,
                        amortization[-1],
                    )
                )

            amortization.append(
                self._compute_row(
                    year,
                    amortization[-1],
                )
            )

        return pd.DataFrame(amortization)
