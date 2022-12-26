
import json
from urllib.parse import urlparse
import requests
from django.core.files.base import ContentFile
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from authenticate.models import Seller, UserProfile
from order_payment.models import PayOut
from tech_ecommerce.models import Categories, Interactive, ImgProducts, Options, ProductChilds, ProductVariants, Products, Speficication

def ConvertURLToImage(url):
    name = urlparse(url).path.split('/')[-1]
    response = requests.get(url)
    return name, response

class InsertData():

    admin_group = Group.objects.create(name="ADMIN")      
    staff_group = Group.objects.create(name="STAFF")
    user_group = Group.objects.create(name="USER")
    seller_group = Group.objects.create(name="SELLER")

    # admin_group = Group.objects.get(name="ADMIN")
    # user_group = Group.objects.get(name="USER")
    # seller_group = Group.objects.get(name="SELLER") 
    
    admin1 = User.objects.create_superuser(
            username='admin01',
            password='admin01',
            email= 'pbl6teche@gmail.com',
            first_name='admin',      
        )
    admin1.groups.add(admin_group)
    admin2 = User.objects.create_superuser(
            username='admin02',
            password='admin02',
            email= 'pbl6teche@gmail.com',
            first_name='admin',      
        )
    admin2.groups.add(admin_group)

    list_seller = []
    users_data = json.load(open("./Data/users_data.json", encoding='utf8'))
    for user in users_data:
        user_new = User.objects.create_user(
            username=user['username'],
            password=user['password'],
            email= user['email'],
            first_name=user['first_name'],
            last_name=user['last_name'],          
        )
        user_new.groups.add(user_group)
        user_profile = user['userprofile']
        user_profile_new = UserProfile.objects.create(
            user = user_new,
            is_seller = user_profile['is_seller'],
            gender = user_profile['gender'],
            birthday =user_profile['birthday'],
            phone =user_profile['phone'],
            address=user_profile['address'],
        )
        if user_profile['avt'] is not None:
            name,response = ConvertURLToImage(user_profile['avt'])
            user_profile_new.avt.save(name, ContentFile(response.content), save=True)

        if user_profile['is_seller']:
            seller = user_profile['seller']
            seller_new = Seller.objects.create(
                user=user_profile_new,
                name_store= seller['name_store'],
                )
            name,response = ConvertURLToImage(seller['logo'])
            seller_new.logo.save(name, ContentFile(response.content), save=True)
            list_seller.append(seller_new)
            user_new.groups.add(seller_group)
            PayOut.objects.create(seller=seller_new,account="userpbl601@personal.example.com")



    for i in ["Smart phone","Tablet","Laptop"]:
        category = Categories.objects.create(name=i)


    products_data = json.load(open("./Data/products_data.json", encoding='utf8'))
    interactives = json.load(open("./Data/comments_data.json", encoding='utf8'))
    id_seller = -1
    for idx in range(0,len(products_data)):
        if idx % 7 == 0:
            id_seller += 1
        print("product -> ",idx)
        product = products_data[idx]
        product_new = Products.objects.create(
            seller=list_seller[id_seller],
            category_id=product['category_id']+1,
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
        count=0
        for child in child_products:
            child_new = ProductChilds.objects.create(
                product=product_new,
                seller = list_seller[id_seller],
                name = child['name'],
                price = child['price'],
                inventory_status = child['inventory_status'],
                selected = child['selected'],
                thumbnail_url = child['thumbnail_url'],
                name_url = f"product_{product_new.pk}_child_{count}",
                option1=child['option1'],
                option2=child['option2']              
            )
            count+=1
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
            
            for id in range(0,len(list_childs)):
                option_new = Options.objects.create(
                    product_child_id = list_childs[id].pk,
                    product_variant_id=variant_new.pk,
                    value = list_options[id]['option'+str(option_idx)]
                )
            option_idx+=1
        count = 0
        imgs_data = product['img_products']
        for img in imgs_data:
            ImgProducts.objects.create(product_id=product_new.pk,link=img['link'], name = f"product_{product_new.pk}_image_{count}")
            count+=1

        count = 0
        for interactive in interactives[idx]:
            Interactive.objects.create(
                product_id=interactive['product_id']+1,
                user_id=interactive['user_id'],
                favorite=interactive['favorite'], 
                link=interactive['link'], 
                comment=interactive['comment'], 
                rating=int(interactive['rating']), 
                time_interactive=interactive['time_interactive'],)
            count+=1
        
