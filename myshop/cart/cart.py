from decimal import Decimal
from django.conf import settings
from shop.models import Product


class Cart(object):
    def __init__(self, request):
        """Inicializa o carrinho de compras"""
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # salva um carrinho vazio
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1, override_quantity=False):
        """"Adiciona um produto no carrinho de compras ou atualiza a quantidade"""
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0, 'price': str(product.price)}
        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()

    def save(self):
        # marca a sessao como 'modificada' para garantir que ela seja salva
        self.session.modified = True

    def remove(self, product):
        """Remove um item do carrinho"""
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        """
        Itera pelos itens do carrinho de compras e obtem os produtos do banco de dados
        """
        product_ids = self.cart.keys()
        # obtém os objetos referentes aos produtos e os adiciona no carrinha
        products = Product.objects.filter(id__in=product_ids)

        cart = self.cart.copy()
        for product in products:
            cart[str(product.id)]['product'] = product
        
        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        """Contabiliza todos os itens que estão no carrinho de compras"""
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        """Soma o total dos pedido"""
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        del self.session[settings.CART_SESSION_ID]
        self.save()
