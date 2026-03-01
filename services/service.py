from datetime import datetime, timezone


class ShippingService:
    SHIPPING_CREATED = 'created'
    SHIPPING_IN_PROGRESS = 'in progress'
    SHIPPING_COMPLETED = 'completed'
    SHIPPING_FAILED = 'failed'

    def __init__(self, repository, publisher):
        self.repository = repository
        self.publisher = publisher

    @staticmethod
    def list_available_shipping_type():
        return ['Нова Пошта', 'Укр Пошта', 'Meest Express', 'Самовивіз']

    def create_shipping(self, shipping_type, product_ids, order_id, due_date):
        if shipping_type not in self.list_available_shipping_type():
            raise ValueError("Shipping type is not available")

        if due_date <= datetime.now(timezone.utc):
            raise ValueError("Shipping due datetime must be greater than datetime now")

        shipping_id = self.repository.create_shipping(
            shipping_type,
            product_ids,
            order_id,
            self.SHIPPING_CREATED,
            due_date
        )

        self.publisher.send_new_shipping(shipping_id)
        self.repository.update_shipping_status(
            shipping_id,
            self.SHIPPING_IN_PROGRESS
        )

        return shipping_id

    def process_shipping_batch(self):
        result = []
        shipping_ids = self.publisher.poll_shipping()

        for shipping_id in shipping_ids:
            self.process_shipping(shipping_id)
            result.append({"shipping_id": shipping_id})

        return result

    def process_shipping(self, shipping_id):
        shipping = self.repository.get_shipping(shipping_id)

        if datetime.fromisoformat(shipping['due_date']) < datetime.now(timezone.utc):
            return self.fail_shipping(shipping_id)

        return self.complete_shipping(shipping_id)

    def check_status(self, shipping_id):
        shipping = self.repository.get_shipping(shipping_id)
        return shipping['status']

    def fail_shipping(self, shipping_id):
        self.repository.update_shipping_status(
            shipping_id,
            self.SHIPPING_FAILED
        )
        return {"shipping_id": shipping_id}

    def complete_shipping(self, shipping_id):
        self.repository.update_shipping_status(
            shipping_id,
            self.SHIPPING_COMPLETED
        )
        return {"shipping_id": shipping_id}
