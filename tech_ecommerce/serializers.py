
from datetime import datetime
from django.http.request import QueryDict, MultiValueDict
from rest_framework import serializers
from authenticate.models import Seller
from authenticate.serializers import SellerSerializer
from tech_ecommerce.models import Interactive, CartItem, Categories, ImgProducts, Options, ProductChilds, ProductVariants, Products, Speficication

class ImgProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImgProducts
        fields = '__all__'
    def create(self, validated_data):
        return ImgProducts.objects.create(**validated_data)
    def update(self, instance, validated_data):
        instance.link = validated_data.get('link', instance.link)
        instance.save()
        return instance


class SpeficicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Speficication
        fields = '__all__'
    def create(self, validated_data):
        return Speficication.objects.create(**validated_data)
    def update(self, instance, validated_data):
        instance.brand = validated_data.get('brand', instance.brand)
        instance.cpu_speed = validated_data.get('cpu_speed', instance.cpu_speed)
        instance.gpu = validated_data.get('gpu', instance.gpu)
        instance.ram = validated_data.get('ram', instance.ram)
        instance.screen_size = validated_data.get('screen_size', instance.screen_size)
        instance.battery_capacity = validated_data.get('battery_capacity', instance.battery_capacity)
        instance.weight = validated_data.get('weight', instance.weight)
        instance.chip_set = validated_data.get('chip_set', instance.chip_set)
        instance.material = validated_data.get('material', instance.material)
        instance.save()
        return instance


class ProductChildSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductChilds
        fields = '__all__'
    def create(self, validated_data):
        return ProductChilds.objects.create(**validated_data)
    def update(self, instance, validated_data):
        instance.sku = validated_data.get('sku', instance.sku)
        instance.name = validated_data.get('name', instance.name)
        instance.price = validated_data.get('price', instance.price)
        instance.iventory_status = validated_data.get('iventory_status', instance.iventory_status)
        instance.selected = validated_data.get('selected', instance.selected)
        instance.thumbnail_url = validated_data.get('thumbnail_url', instance.thumbnail_url)
        instance.save()
        return instance

class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Options
        fields = '__all__'
        read_only_fileds=['id']
    def validate(self, data):    
        option_new = Options.objects.get(product_variant=data['product_variant'],product_child=data['product_child'])
        if not self.instance and option_new is not None:
            raise serializers.ValidationError({"option": "Variant option is existed"})
        if self.instance and option_new:
            if self.instance.product_child != option_new.product_child:
                raise serializers.ValidationError({"option": "Multi product childs must not be in a variant option"})      
        return data
     
class ProductVariantSerializer(serializers.ModelSerializer):
    class OptionSerializer(serializers.ModelSerializer):
        class Meta:
            model = Options
            fields = ['id','value','product_child']
            read_only_fileds=['id']

    options = OptionSerializer(many=True)
    class Meta:
        model = ProductVariants
        fields = '__all__'
        read_only_fileds=['id']
    # Kiểm tra product variant chỉ chứa 1 (Màu, Dung lượng)
    # Kiểm tra option chỉ chứa 1 child ứng với 1 variant
    def validate(self, data):
        variant = ProductVariants.objects.get(name=data['name'],product=data['product']) 
        if not self.instance and variant is not None:
            raise serializers.ValidationError({"variant": "Product variant is existed"})
        option_data = data['options']
        for i in range(0,len(option_data)):
            for j in range(i+1,len(option_data)):
                if option_data[i].get('product_child')==option_data[j].get('product_child'):
                    raise serializers.ValidationError({"option": "Multi product childs must not be in a variant option"})
        return data
    def create(self, validated_data):
        options_data = validated_data.pop('options')  
        variant=ProductVariants.objects.create(product_variant=variant,**validated_data)
        for option in options_data:
            Options.objects.create(product_variant=variant,**option)
        return variant

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)     
        instance.save()
        options = list((instance.options).all())
        options_data = validated_data.pop('options') 
        for option in options_data:        
            option_update=options.pop(0)
            option_update.value = option.get('value', option_update.value)
            option_update.product_child = option.get('product_child', option_update.product_child)
            option_update.save()
        return instance


        

class ProductsSerializer(serializers.ModelSerializer):
    img_products = ImgProductSerializer(many=True, required=False)
    product_childs = ProductChildSerializer(many=True, required=False) 
    product_variants = ProductVariantSerializer(many=True, required=False) 
    speficication = SpeficicationSerializer()

    class Meta:
        model = Products
        fields = '__all__'      
        read_only_fileds = ('category','seller', 'img_products','product_variants')
    def create(self, validated_data):
        speficication_data = validated_data.pop('speficication')
        product = Products.objects.create(**validated_data)
        Speficication.objects.create(product=product,**speficication_data)

        product.category.total += 1
        product.category.save()
        product.seller.product_count += 1
        product.seller.save()
        return product

    def update(self, instance, validated_data):
        speficication_pop = validated_data.pop('speficication')

        instance.category = validated_data.get('category', instance.category)
        instance.name = validated_data.get('name', instance.name)
        instance.slug = validated_data.get('slug', instance.slug)
        instance.price = validated_data.get('price', instance.price)
        instance.original_price = validated_data.get('original_price', instance.original_price)
        instance.short_description = validated_data.get('short_description', instance.short_description)
        instance.description = validated_data.get('description', instance.description)
        instance.discount_rate = validated_data.get('discount_rate', instance.discount_rate)
        instance.rating_average = validated_data.get('rating_average', instance.rating_average)
        instance.modified_at = datetime.now()
        instance.color = validated_data.get('color', instance.color)
        instance.quantity_sold = validated_data.get('quantity_sold', instance.quantity_sold)
        instance.review_count = validated_data.get('review_count', instance.review_count)
        instance.save()

        speficication = instance.speficication
        speficication.brand = speficication_pop.get('brand', speficication.brand)
        speficication.cpu_speed = speficication_pop.get('cpu_speed', speficication.cpu_speed)
        speficication.gpu = speficication_pop.get('gpu', speficication.gpu)
        speficication.ram = speficication_pop.get('ram', speficication.ram)
        speficication.rom = speficication_pop.get('rom', speficication.rom)
        speficication.screen_size = speficication_pop.get('screen_size', speficication.screen_size)
        speficication.battery_capacity = speficication_pop.get('battery_capacity', speficication.battery_capacity)
        speficication.weight = speficication_pop.get('weight', speficication.weight)
        speficication.chip_set = speficication_pop.get('chip_set', speficication.chip_set)
        speficication.material = speficication_pop.get('material', speficication.material)
        speficication.save()
        return instance


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Categories
        fields = '__all__'
    def create(self, validated_data):
        return Categories.objects.create(**validated_data)
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.icon = validated_data.get('icon', instance.icon)
        instance.description = validated_data.get('description', instance.description)
        instance.total= validated_data.get('total', instance.total)
        instance.save()
        return instance


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['product_child'] = ProductChildSerializer(instance.product_child).data
        return response
    def cal_total_price(self, quantity, product_child):
        total_price = product_child.price*quantity
        return total_price
    def create(self, validated_data):
        price = self.cal_total_price(validated_data.get('quantity'), validated_data.get('product_child'))
        cart_item = CartItem.objects.create(
            user_profile=validated_data.get('user_profile'),
            product_child=validated_data.get('product_child'),
            quantity=validated_data.get('quantity'),
            total_price=price,
        )
        return cart_item

    def update(self, instance, validated_data):
        instance.quantity = validated_data.get('quantity', instance.quantity)
        price = self.cal_total_price(instance.quantity, instance.product_child)
        instance.total_price = validated_data.get('price', price)
        instance.save()
        return instance

class InteractiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interactive
        fields = '__all__'
    def create(self, validated_data):
        return Interactive.objects.create(**validated_data)
    def update(self, instance, validated_data):
        instance.favorite = validated_data.get('favorite', instance.favorite)
        instance.comment = validated_data.get('comment', instance.comment)
        instance.link = validated_data.get('link', instance.link)
        instance.rating = validated_data.get('rating', instance.rating)
        instance.time_interactive = datetime.now()
        instance.save()
        return instance
    



