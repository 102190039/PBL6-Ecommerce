import json
from tech_ecommerce.models import Categories, ImgProducts, Options, ProductChilds, ProductVariants, Products, Speficication
from django.contrib.auth.models import Group


def AddGroup():
    admin_group = Group.objects.get_or_create(name="ADMIN")      
    staff_group = Group.objects.get_or_create(name="STAFF")
    user_group = Group.objects.get_or_create(name="USER")
    sup_group = Group.objects.get_or_create(name="SELLER")


class InsertData():
    
    for i in ["Điện Thoại","Laptop"]:
        category = Categories.objects.get_or_create(name=i)

    data = json.load(open("./Data/crawled_data.json", encoding='utf8'))
    data_img = json.load(open("./Data/img_data.json", encoding='utf8'))
    for idx in range(0,len(data)):
        product = data[idx]
        product_new = Products.objects.create(
            seller_id=1,
            category_id=1,
            name=product['name'], 
            short_description= product['short_description'],
            description=product['description'],
            price= product['price'],
            original_price= product['original_price'],
            discount_rate = product['discount_rate'],
            rating_average= product['rating_average'],
            quantity_sold= product['quantity_sold'],           
        )
        speficication= product['speficication']
        speficication_new = Speficication.objects.create(
            product_id=product_new.pk,
            brand = speficication['brand'],
            cpu_speed = speficication['cpu_speed'],
            gpu = speficication['gpu'],
            ram = speficication['ram'],
            rom = speficication['rom'],
            screen_size = speficication['screen_size'],
            battery_capacity= speficication['battery_capacity'],
            weight = speficication['weight'],
            chip_set = speficication['chip_set'],
            material = speficication['material'],
        )
        child_products=product['child_product']
        list_childs=[]
        list_options=[]
        for child in child_products:
            child_new = ProductChilds.objects.create(
                product_id=product_new.pk,
                seller_id = 1,
                name = child['name'],
                sku = child['sku'],
                price = child['price'],
                inventory_status = child['inventory_status'],
                selected = child['selected'],
                thumbnail_url = child['thumbnail_url']                
            )
            option= dict()
            option['option1']=child['option1']
            if 'option2' in child and child['option2']:
                option['option2']=child['option2']            
            list_options.append(option)
            list_childs.append(child_new)
           
            

        product_variants = product['product_variants']
        option_idx=1
        for variant in product_variants:
            variant_new = ProductVariants.objects.create(
                product_id=product_new.pk,
                name = variant['name'],              
            )
            
            for idx in range(0,len(list_childs)):
                print(list_options[idx]['option'+str(option_idx)])
                option_new = Options.objects.create(
                    product_child_id = list_childs[idx].pk,
                    product_variant_id=variant_new.pk,
                    value = list_options[idx]['option'+str(option_idx)]
                )
            option_idx+=1
        for img in data_img[idx]:
            ImgProducts.objects.create(product_id=product_new.pk,link=img['link'])
