"""
One test class per design pattern. Run from the Lab2 folder:

    python3 -m unittest -v
"""

import csv
import os
import tempfile
import threading
import unittest
from decimal import Decimal

from wealth import PortfolioBuilder, PortfolioDirector, WealthDashboard
from wealth.assets import AssetFactory, AssetGroup, BuilderError, Crypto, RealEstate, Stock
from wealth.pricing import (ApiPriceProvider, CachingPriceProvider, DemoMarketData,
                            LiveMarketData, MockPriceProvider)
from wealth.storage import AssetRepository, Database
from wealth.valuation import FixedFee, PercentageFee

PRICES = MockPriceProvider({"AAPL": Decimal("214.50"), "MSFT": Decimal("432.10"),
                            "BTC": Decimal("61250.00"), "ETH": Decimal("2980.75")})


class PatternTestCase(unittest.TestCase):
    def setUp(self):
        Database._reset()  # every test starts from a fresh shared connection


class SingletonTest(PatternTestCase):

    def test_every_call_returns_the_same_instance(self):
        self.assertIs(Database(), Database())
        self.assertIs(Database.instance(), Database())

    def test_repositories_share_one_connection(self):
        first, second = AssetRepository(), AssetRepository()
        first.save(PortfolioDirector().demo_portfolio())
        self.assertEqual(len(list(second.load().holdings())), 6)

    def test_reopening_at_a_different_path_is_refused(self):
        Database(":memory:")
        with self.assertRaises(RuntimeError):
            Database("/tmp/other.db")

    def test_concurrent_first_use_creates_one_instance(self):
        seen = []
        threads = [threading.Thread(target=lambda: seen.append(Database()))
                   for _ in range(16)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        self.assertEqual(len({id(db) for db in seen}), 1)


class FactoryMethodTest(PatternTestCase):

    def test_demo_source_creates_a_cached_mock_provider(self):
        provider = DemoMarketData().provider()
        self.assertIsInstance(provider, CachingPriceProvider)
        self.assertIsInstance(provider.inner, MockPriceProvider)

    def test_live_source_creates_an_api_provider(self):
        provider = LiveMarketData("https://quotes.example", "key").provider()
        self.assertIsInstance(provider.inner, ApiPriceProvider)

    def test_provider_is_created_once_per_source(self):
        source = DemoMarketData()
        self.assertIs(source.provider(), source.provider())

    def test_asset_factory_creates_the_registered_class(self):
        asset = AssetFactory.create("real_estate", "FLAT", "1",
                                    {"appraised_value": "85000", "mortgage_balance": "41000"})
        self.assertIsInstance(asset, RealEstate)
        self.assertEqual(asset.appraised_value, Decimal("85000"))  # Decimal, not str

    def test_asset_factory_rejects_unknown_kinds(self):
        with self.assertRaises(ValueError):
            AssetFactory.create("bond", "X", "1")


class BuilderTest(PatternTestCase):

    def test_director_builds_the_expected_tree(self):
        root = PortfolioDirector().demo_portfolio()
        self.assertEqual([g.name for g in root.children],
                         ["Investments", "Savings", "Property"])
        self.assertEqual([a.symbol for a in root.holdings()],
                         ["AAPL", "MSFT", "BTC", "ETH", "EUR-SAVINGS", "FLAT-CHISINAU"])

    def test_same_builder_serves_several_recipes(self):
        director = PortfolioDirector()
        self.assertEqual(len(list(director.demo_portfolio().holdings())), 6)
        self.assertEqual(len(list(director.starter_portfolio().holdings())), 2)

    def test_float_input_does_not_leak_binary_error(self):
        root = PortfolioBuilder().crypto("BTC", 0.35).build()
        self.assertEqual(next(root.holdings()).quantity, Decimal("0.35"))

    def test_invalid_portfolios_are_rejected(self):
        cases = {
            "duplicate": lambda b: b.stock("AAPL", 1).stock("AAPL", 2),
            "negative": lambda b: b.stock("AAPL", -1),
            "unclosed": lambda b: b.group("Open").stock("AAPL", 1),
            "stray end": lambda b: b.end(),
            "empty": lambda b: b,
            "underwater": lambda b: b.real_estate("FLAT", "10", "20"),
        }
        for name, steps in cases.items():
            with self.subTest(name), self.assertRaises(BuilderError):
                steps(PortfolioBuilder()).build()


class CompositeTest(PatternTestCase):

    def setUp(self):
        super().setUp()
        self.root = PortfolioDirector().demo_portfolio()

    def test_group_value_is_sum_of_children(self):
        self.assertEqual(self.root.market_value(PRICES), Decimal("90191.150"))
        investments = self.root.children[0]
        self.assertEqual(investments.market_value(PRICES), Decimal("38691.150"))

    def test_leaf_and_group_are_used_identically(self):
        leaf = Stock("AAPL", Decimal("12"))
        for component in (leaf, AssetGroup("Only AAPL", [leaf])):
            self.assertEqual(component.market_value(PRICES), Decimal("2574.00"))

    def test_walk_reports_group_paths(self):
        paths = {asset.symbol: "/".join(path[1:]) for path, asset in self.root.walk()}
        self.assertEqual(paths["BTC"], "Investments/Crypto")
        self.assertEqual(paths["EUR-SAVINGS"], "Savings")

    def test_tree_survives_a_database_round_trip(self):
        repo = AssetRepository()
        repo.save(self.root)
        loaded = repo.load()
        self.assertEqual(loaded.market_value(PRICES), self.root.market_value(PRICES))
        self.assertEqual([(d, g.name) for d, g in loaded.outline()],
                         [(d, g.name) for d, g in self.root.outline()])


class DecoratorTest(PatternTestCase):

    def test_percentage_fee(self):
        self.assertEqual(PercentageFee(Stock("AAPL", Decimal("12")), "0.005")
                         .market_value(PRICES), Decimal("2561.13000"))

    def test_decorators_stack_and_order_matters(self):
        btc = Crypto("BTC", Decimal("0.35"))
        pct_then_fixed = FixedFee(PercentageFee(btc, "0.01"), "15")
        fixed_then_pct = PercentageFee(FixedFee(btc, "15"), "0.01")
        self.assertEqual(pct_then_fixed.market_value(PRICES), Decimal("21208.125"))
        self.assertEqual(fixed_then_pct.market_value(PRICES), Decimal("21208.275"))
        self.assertEqual(pct_then_fixed.costs(), ["fee 1%", "fee 15"])

    def test_a_whole_group_can_be_decorated(self):
        stocks = PortfolioDirector().demo_portfolio().children[0].children[0]
        self.assertEqual(PercentageFee(stocks, "0.10").market_value(PRICES),
                         Decimal("4261.050"))

    def test_proceeds_never_go_negative(self):
        tiny = Crypto("ETH", Decimal("0.001"))
        self.assertEqual(FixedFee(tiny, "15").market_value(PRICES), Decimal("0"))

    def test_invalid_rate_is_rejected(self):
        with self.assertRaises(ValueError):
            PercentageFee(Stock("AAPL", Decimal("1")), "1.5")


class FacadeTest(PatternTestCase):

    def setUp(self):
        super().setUp()
        self.dashboard = WealthDashboard(DemoMarketData())
        self.dashboard.save_portfolio(PortfolioDirector().demo_portfolio())

    def test_summary_figures(self):
        summary = self.dashboard.summary()
        self.assertEqual(summary.net_worth, Decimal("90191.15"))
        self.assertEqual(summary.liquidation_value, Decimal("85747.92"))
        self.assertEqual(summary.selling_cost, Decimal("4443.23"))

    def test_export_picks_format_from_extension(self):
        with tempfile.TemporaryDirectory() as folder:
            path = self.dashboard.export(os.path.join(folder, "p.csv"))
            with open(path, newline="") as handle:
                header = next(csv.reader(handle))
            self.assertEqual(header[-1], "net_value")
            with self.assertRaises(ValueError):
                self.dashboard.export(os.path.join(folder, "p.xlsx"))

    def test_prices_are_fetched_once_per_symbol(self):
        source = DemoMarketData()
        dashboard = WealthDashboard(source)
        dashboard.save_portfolio(PortfolioDirector().demo_portfolio())
        dashboard.summary()  # values every holding, every group, gross and net
        self.assertEqual(source.provider().inner.calls, 4)  # AAPL MSFT BTC ETH


if __name__ == "__main__":
    unittest.main()
