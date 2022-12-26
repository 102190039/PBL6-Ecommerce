
from datetime import datetime
from rest_framework import serializers
from tech_ecommerce.models import Interactive, CartItem, Categories, ImgProducts, Options, ProductChilds, ProductVariants, Products, Speficication

class ImgProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImgProducts
        fields = '__all__'


class SpeficicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Speficication
        fields = ['brand', 'cpu_speed', 'gpu', 'ram', 'rom',
            'screen_size', 'battery_capacity', 'weight', 'chip_set', 'material']
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
        extra_kwargs = {
            'product': {'required': False},
            'seller': {'required': False},
            'name_url': {'required': False,'write_only':True},
            }
        create_only_fields = ["product","seller","name_url"]

class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Options
        fields = '__all__'
        read_only_fileds=['id']
    def validate(self, data):    
        optionNew = Options.objects.filter(
            product_variant=data['product_variant'],
            product_child=data['product_child'])
        if not self.instance and optionNew.count() > 0:
            raise serializers.ValidationError({
                "option": "Variant option is existed"
            })
        if self.instance and optionNew:
            if self.instance.product_child != optionNew[0].product_child:
                raise serializers.ValidationError({
                    "option": "Multi product childs must not be in a variant option"
                })      
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
        extra_kwargs = {
            'product': {'required': False},
            }
        create_only_fields = ["product"]
    # Kiểm tra product variant chỉ chứa 1 (Màu, Dung lượng)
    # Kiểm tra option chỉ chứa 1 child ứng với 1 variant
    def validate(self, data):
        variant = ProductVariants.objects.filter(name=data['name'],product=data['product'])
        if not self.instance and variant.count()>0:
            raise serializers.ValidationError({
                "variant": "Product variant is existed"
            })
        optionData = data['options']
        for i in range(0,len(optionData)):
            for j in range(i+1,len(optionData)):
                if optionData[i].get('product_child')==optionData[j].get('product_child'):
                    raise serializers.ValidationError({
                        "option": "Multi product childs must not be in a variant option"
                    })
        return data

    def create(self, validated_data):
        optionsData = validated_data.pop('options')  
        variant=ProductVariants.objects.create(**validated_data)
        for option in optionsData:
            Options.objects.create(product_variant=variant,**option)
        return variant

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)     
        instance.save()
        options = list((instance.options).all())
        optionsData = validated_data.pop('options') 
        for option in optionsData:        
            optionUpdate=options.pop(0)
            optionUpdate.value = option.get('value', optionUpdate.value)
            optionUpdate.product_child = option.get('product_child', optionUpdate.product_child)
            optionUpdate.save()
        return instance


class ProductListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields =('id','category', 'name','short_description', 'price','original_price','quantity_sold','rating_average','discount_rate')
    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['img_products'] = ImgProductSerializer(instance.img_products,many=True).data
        return response

class ProductsSerializer(serializers.ModelSerializer):
    speficication = SpeficicationSerializer()

    class Meta:
        model = Products
        fields = '__all__'     
        extra_kwargs = {'seller': {'required': False}}
        create_only_fields = ('category','seller', 'img_products','product_variants')
        read_only_fields = ('slug','price','rating_average','quantity_sold','review_count')
    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['img_products'] = ImgProductSerializer(instance.img_products,many=True).data
        response['product_childs'] = ProductChildSerializer(instance.product_childs,many=True).data
        response['product_variants'] = ProductVariantSerializer(instance.product_variants,many=True).data
        return response

    def create(self, validated_data):
        speficicationData = validated_data.pop('speficication')
        product = Products.objects.create(**validated_data)
        Speficication.objects.create(product=product,**speficicationData)

        
        return product

    def update(self, instance, validated_data):
        speficicationPop = validated_data.pop('speficication')

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
        speficication.brand = speficicationPop.get('brand', speficication.brand)
        speficication.cpu_speed = speficicationPop.get('cpu_speed', speficication.cpu_speed)
        speficication.gpu = speficicationPop.get('gpu', speficication.gpu)
        speficication.ram = speficicationPop.get('ram', speficication.ram)
        speficication.rom = speficicationPop.get('rom', speficication.rom)
        speficication.screen_size = speficicationPop.get('screen_size', speficication.screen_size)
        speficication.battery_capacity = speficicationPop.get('battery_capacity', speficication.battery_capacity)
        speficication.weight = speficicationPop.get('weight', speficication.weight)
        speficication.chip_set = speficicationPop.get('chip_set', speficication.chip_set)
        speficication.material = speficicationPop.get('material', speficication.material)
        speficication.save()
        return instance


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Categories
        fields = '__all__'

class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['product_child'] = {
            "product":instance.product_child.product_id,
            "name" : instance.product_child.name,
            "price" : instance.product_child.price,
            "thumbnail_url":instance.product_child.thumbnail_url,
            "option1":instance.product_child.option1,
            "option2":instance.product_child.option2,
            
        }
        return response
    def CalTotalPrice(self, quantity, product_child):
        totalPrice = product_child.price*quantity
        return totalPrice
    def create(self, validated_data):
        price = self.CalTotalPrice(validated_data.get('quantity'), validated_data.get('product_child'))
        cartItem = CartItem.objects.create(
            user=validated_data.get('user'),
            product_child=validated_data.get('product_child'),
            quantity=validated_data.get('quantity'),
            total_price=price,
        )
        return cartItem

    def update(self, instance, validated_data):
        instance.quantity = validated_data.get('quantity', instance.quantity)
        price = self.CalTotalPrice(instance.quantity, instance.product_child)
        instance.total_price = validated_data.get('price', price)
        instance.save()
        return instance

class InteractiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interactive
        fields = '__all__'
    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['user'] = {
            "id": instance.user.pk,
            "name":instance.user.first_name,
            "avt" : f'/{instance.user.user_profile.avt}',          
        }
        return response



