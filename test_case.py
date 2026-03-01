import unittest
from eshop import Product, ShoppingCart, Order
from unittest.mock import MagicMock

class TestEshopExtended(unittest.TestCase):
    def setUp(self):
        self.product = Product(name='Test', price=100.0, stock=10)
        self.cart = ShoppingCart()
        self.mock_shipping_service = MagicMock()

    def test_mock_add_product(self):
        self.product.is_available = MagicMock(return_value=True)
        self.cart.add_product(self.product, 5)
        self.product.is_available.assert_called_with(5)

    def test_add_available_amount(self):
        self.cart.add_product(self.product, 5)
        self.assertIn(self.product, self.cart.products)

    def test_add_non_available_amount(self):
        with self.assertRaises(ValueError):
            self.cart.add_product(self.product, 15)

    def test_product_initialization(self):
        self.assertEqual(self.product.name, 'Test')
        self.assertEqual(self.product.price, 100.0)

    def test_calculate_total_single_item(self):
        self.cart.add_product(self.product, 3)
        self.assertEqual(self.cart.calculate_total(), 300.0)

    def test_calculate_total_multiple_items(self):
        p2 = Product('Apple', 10.0, 50)
        self.cart.add_product(self.product, 1)
        self.cart.add_product(p2, 5)
        self.assertEqual(self.cart.calculate_total(), 150.0)

    def test_remove_product_logic(self):
        self.cart.add_product(self.product, 1)
        self.cart.remove_product(self.product)
        self.assertNotIn(self.product, self.cart.products)

    def test_add_zero_amount(self):
        self.cart.add_product(self.product, 0)
        self.assertEqual(self.cart.products[self.product], 0)

    def test_add_negative_amount(self):
        with self.assertRaises(ValueError):
            self.cart.add_product(self.product, -1)

    def test_order_reduces_stock(self):
        self.cart.add_product(self.product, 2)
        # Передаємо mock_shipping_service як другий аргумент
        order = Order(self.cart, self.mock_shipping_service)
        order.place_order()
        self.assertEqual(self.product.stock, 8)

    def test_cart_clears_after_order(self):
        self.cart.add_product(self.product, 1)
        # Передаємо mock_shipping_service як другий аргумент
        Order(self.cart, self.mock_shipping_service).place_order()
        self.assertEqual(len(self.cart.products), 0)

    def test_is_available_exact_amount(self):
        self.assertTrue(self.product.is_available(10))

    def test_is_available_exceed_amount(self):
        self.assertFalse(self.product.is_available(11))

if __name__ == '__main__':
    unittest.main()