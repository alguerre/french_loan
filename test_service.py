from unittest import TestCase

from service import LoanService
from definitions import PartialAmortization


class LoanServiceTest(TestCase):
    def test_annuity(self):
        loan = LoanService(borrowed_capital=10_000, duration=6, eir=0.03)
        self.assertEqual(1_845.98, loan.annuity)

    def test_get_amortization_table(self):
        loan = LoanService(borrowed_capital=6_000, duration=3, eir=0.05)
        table = loan.get_amortization_table()

        self.assertDictEqual(
            {
                "year": 2,
                "annuity": 2_203.25,
                "interest": 204.84,
                "amortized_capital": 1_998.41,
                "outstanding_capital": 2_098.34,
            },
            table.iloc[2].to_dict(),
        )

    def test_get_amortization_table_with_partials(self):
        loan = LoanService(borrowed_capital=6_000, duration=3, eir=0.05)
        table = loan.get_amortization_table_with_partials(
            [PartialAmortization(year=2, capital=500)]
        )

        row = table.iloc[2].to_dict()

        self.assertEqual(2, row["year"])
        self.assertEqual(500.0, row["amortized_capital"])
        self.assertEqual(3_596.75, row["outstanding_capital"])
