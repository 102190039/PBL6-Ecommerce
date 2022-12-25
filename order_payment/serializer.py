
from rest_framework import serializers
from authenticate.models import Seller
from order_payment.models import Order, OrderDetail, PayIn, PurchasedProduct
from tech_ecommerce.models import CartItem, ProductChilds

class OrderDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderDetail
        fields = ['id','quantity','total_price','discount']

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['product_child'] = {
            "product":instance.product_child.product_id,
            "name" : instance.product_child.name,
            "thumbnail_url":instance.product_child.thumbnail_url,
        }
        response['seller'] = {
            "id":instance.seller.pk,
            "name_store" : instance.seller.name_store,
            "logo" : f'/{instance.seller.logo}'
        }
        return response
    def create(self, validated_data):
        return OrderDetail.objects.create(**validated_data)

class OrderSerializer(serializers.ModelSerializer):
    # order_details = OrderDetailSerializer(many=True)
    cart_item_id = serializers.PrimaryKeyRelatedField(queryset=CartItem.objects.all(), write_only=True,many=True)
    class Meta:
        model = Order
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['order_details'] = OrderDetailSerializer(instance.order_details,many=True).data
        return response

    def create(self, validated_data):
        cartItems = validated_data.pop('cart_item_id')
        numberOrder = int(len(cartItems))
        order = Order(
            user = validated_data.get('user'),
            total_price = 0,
            order_count = numberOrder,
        )
        subPrice = 0
        for i in range(0, numberOrder):
            item = cartItems[i]
            # get child from cart_item
            child = ProductChilds.objects.get(pk=item.product_child_id)
            # get seller from child
            sellerId = child.seller_id
            seller = Seller.objects.get(pk=sellerId)
            OrderDetail.objects.create(
                product_child = child, 
                order = order,
                seller = seller,
                quantity =  item.quantity,
                total_price =  item.total_price,
            )
            subPrice += item.total_price
            item.delete()
        order.total_price = subPrice
        order.save()
        return order

# ------------------------ Payment ------------------------

class PayInSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayIn
        fields = '__all__'
    def create(self, validated_data):
        # convert VND to USD
        numberMoney = validated_data.get('number_money')/25000
        payIn = PayIn.objects.create(
            order= validated_data.get('order'),
            number_money= numberMoney,
            type_payment = validated_data.get('type_payment'))
        return payIn

class PurchasedProductSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['order'] = OrderSerializer(instance.order).data
        return response

    class Meta:
        model= PurchasedProduct
        fields = ['status_purchase']

        