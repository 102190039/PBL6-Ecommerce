import traceback
import time
from django.http.request import QueryDict, MultiValueDict
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from authenticate import group_permission
from order_payment.models import PurchasedProduct
from tech_ecommerce.filters import ProductFilter
from tech_ecommerce.models import ( Interactive, 
                                    CartItem, 
                                    Categories, 
                                    ImgProducts, 
                                    Options, 
                                    ProductChilds, 
                                    ProductVariants, 
                                    Products, 
                                    Speficication)
                                    
from tech_ecommerce.serializers import (CartItemSerializer, 
                                        CategorySerializer, 
                                        ImgProductSerializer,
                                        InteractiveSerializer, 
                                        OptionSerializer, 
                                        ProductChildSerializer,
                                        ProductListSerializer, 
                                        ProductVariantSerializer, 
                                        ProductsSerializer, 
                                        SpeficicationSerializer)

from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter
from rest_framework.decorators import action
from django.core.files.storage import default_storage
from config_firebase.config import storage


class ProductViewSet(viewsets.ViewSet):
    serializer_class = ProductsSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny(), ]
        if self.action in ['create', 'update', 'destroy']:
            return [group_permission.IsSeller(), ]
        return super().get_permissions()

    def retrieve(self, request, pk=None):
        try:
            product = Products.objects.get(pk=pk)
            serializer = ProductsSerializer(product)
            return Response({
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            traceback.print_exc()
            return Response({
                "ERROR": f'Exception: {e}'
            }, status=status.HTTP_404_NOT_FOUND)

    def create(self, request):
        data = request.data
        sellerId = self.request.user.id
        if sellerId != int(data["seller"]):
            return Response({
                "ERROR": f"user is not allowed to create product of another seller!",
            }, status=status.HTTP_403_FORBIDDEN)

        serialierProduct = ProductsSerializer(data=data)
        if not serialierProduct.is_valid():
            return Response({
                "ERROR": serialierProduct.errors
            }, status=status.HTTP_404_NOT_FOUND)

        serialierProduct.save()
        return Response({
            "message": "Create product is success!",
            "data": serialierProduct.data
        }, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        sellerId = self.request.user.id
        # find product base on id seller
        try:
            product = Products.objects.get(pk=pk, seller_id=sellerId)
            serializer = ProductsSerializer(
                instance=product, data=request.data)
            if not serializer.is_valid():
                return Response({
                    "error": serializer.errors,
                }, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            return Response({
                "message": "Product updated is sucess!",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            traceback.print_exc()
            return Response({
                "ERROR": f"Exception {e}"
            }, status=status.HTTP_403_FORBIDDEN)

    def destroy(self, request, pk=None):
        sellerId = self.request.user.id
        # find product base on sellerId
        try:
            product = Products.objects.get(pk=pk, seller_id=sellerId)
            product.delete()
            return Response({
                "message": "Product deleted is success!"
            }, status=status.HTTP_200_OK)

        except Exception as e:
            traceback.print_exc()
            return Response({
                "error": f" {e}!"
            }, status=status.HTTP_403_FORBIDDEN)

    @action(methods=['GET'], detail=False, permission_classes=[AllowAny], url_path="filters")
    def get_filters(self, request):
        return Response({
            "filters": listFilters
        }, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=True, permission_classes=[AllowAny], url_path="images")
    def get_images(self, request, pk=None):
        try:
            images= ImgProducts.objects.filter(product=pk)
            serializers = ImgProductSerializer(instance= images,many=True)
            return Response({
                'data': serializers.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            traceback.print_exc()
            return Response({
                "ERROR": f'Exception: {e}'
            }, status=status.HTTP_404_NOT_FOUND)

    @action(methods=['GET'], detail=True, permission_classes=[AllowAny], url_path="childs")
    def get_childs(self, request, pk=None):
        try:
            childs= ProductChilds.objects.filter(product=pk)
            serializers = ProductChildSerializer(instance= childs,many=True)
            return Response({
                'data': serializers.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            traceback.print_exc()
            return Response({
                "ERROR": f'Exception: {e}'
            }, status=status.HTTP_404_NOT_FOUND)

    @action(methods=['GET'], detail=True, permission_classes=[AllowAny], url_path="variants")
    def get_variants(self, request, pk=None):
        try:
            queryset = ProductVariants.objects.filter(product=pk)
            serializers = ProductVariantSerializer(queryset, many=True)
            return Response({
                'data': serializers.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            traceback.print_exc()
            return Response({
                "ERROR": f" {e}!"
            }, status=status.HTTP_403_FORBIDDEN)
    
    @action(methods=['GET'], detail=True, permission_classes=[AllowAny], url_path="interactives")
    def get_interatives(self, request, pk=None):
        try:
            interactives = Interactive.objects.filter(product=pk)
            serializers = InteractiveSerializer(interactives, many=True)
            return Response({
                'data': serializers.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            traceback.print_exc()
            return Response({
                "ERROR": f" {e}!"
            }, status=status.HTTP_403_FORBIDDEN)

class CategoryViewSet(viewsets.ViewSet):
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny(), ]
        elif self.action in ['create', 'update', 'destroy']:
            return [group_permission.IsAdmin(), group_permission.IsStaff()]
        return super().get_permissions()

    def list(self, request):
        queryset = Categories.objects.all()
        serializer = CategorySerializer(queryset, many=True)
        return Response({
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        try:
            category = Categories.objects.get(pk=pk)
            serializer = CategorySerializer(category)
            return Response({
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            traceback.print_exc()
            return Response({
                "ERROR": f'Exception: {e}'
            }, status=status.HTTP_404_NOT_FOUND)
        

    def create(self, request):
        data = request.data
        serializer = CategorySerializer(data=data)
        if not serializer.is_valid():
            return Response({
                "ERROR": serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response({
            'message': 'You create category is success!',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        category = Categories.objects.filter(pk=pk).get()
        data = request.data
        serializer = CategorySerializer(instance=category, data=data)
        if not serializer.is_valid():
            return Response({
                "ERROR": serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response({
            "message": "Updated is success!",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        category = Categories.objects.filter(pk=pk).get()
        category.delete()
        return Response({
            "message": "delete category is success!"
        }, status=status.HTTP_200_OK)

class SpeficicationViewSet(viewsets.ViewSet):
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny(), ]
        if self.action in ['create', 'update', 'destroy']:
            return [group_permission.IsSeller(), ]
        return super().get_permissions()

    def list(self, request):
        queryset = Speficication.objects.all()
        serializers = SpeficicationSerializer(queryset, many=True)
        return Response({
            'data': serializers.data
        }, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        speficication = Speficication.objects.filter(pk=pk).get()
        serializer = SpeficicationSerializer(speficication)
        return Response({
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    def create(self, request):
        data = request.data
        serializer = SpeficicationSerializer(data=data)
        if not serializer.is_valid():
            return Response({
                'message': 'Create speficication is failed!',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response({
            'message': 'Create speficication is Success!',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        data = request.data
        speficication = Speficication.objects.filter(pk=pk).get()
        serializer = SpeficicationSerializer(speficication, data=data)
        if not serializer.is_valid():
            return Response({
                'message': 'Update speficication is failed!',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response({
            'message': 'Update speficication is Success!',
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        speficication = Speficication.objects.filter(pk=pk).get()
        if speficication is not None:
            speficication.delete()
            return Response({
                'message': 'Delete speficication is Success!',
            }, status=status.HTTP_204_NO_CONTENT)
        return Response({
            'message': 'Update speficication is failed!',
            'errors': speficication.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class ImgProductViewSet(viewsets.ViewSet):
    serializer_class = ImgProductSerializer

    def get_permissions(self):
        if self.action in ['retrieve']:
            return [AllowAny(), ]
        elif self.action in ['create', 'update', 'destroy']:
            return [group_permission.IsSeller()]
        return super().get_permissions()


    def retrieve(self, request, pk=None):
        try:
            imgProduct = ImgProducts.objects.get(pk=pk)
            serializer = ImgProductSerializer(imgProduct)
            return Response({
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            traceback.print_exc()
            return Response({
                "ERROR": f'Exception: {e}'
            }, status=status.HTTP_404_NOT_FOUND)
        
    def create(self, request):
        try:
            sellerId = self.request.user.id
            product = Products.objects.get(pk=request.data['product_id'], seller_id=sellerId)
            count= product.img_products.all().count()
            for file in request.FILES.getlist('images'):
                count+=1
                name_image =f"product_{product.id}_{count}"
                default_storage.save("pictures/products/"+file.name, file)
                storage.child("product_images/"+name_image).put("pictures/products/"+file.name)
                # delete image after upload firebase
                default_storage.delete("pictures/products/"+file.name)
                url = storage.child("product_images/" + name_image).get_url(None)
                url += f'&tempstamp={int(time.time())}'
                data={'product': [product.id], 'link': [url], 'name': [name_image]}

                qdict = QueryDict('', mutable=True)
                qdict.update(MultiValueDict(data))
                serializer = ImgProductSerializer(data=qdict)
                if not serializer.is_valid():
                    return Response({
                        'ERROR': serializer.errors,
                    }, status=status.HTTP_400_BAD_REQUEST)
                serializer.save()

            return Response({
                'message': "Uploading product image is successful",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            traceback.print_exc()
            return Response({
                "ERROR": f"Exception {e}"
            }, status=status.HTTP_403_FORBIDDEN)

    def update(self, request, pk=None):
        try:
            sellerId = self.request.user.id
            Products.objects.get(pk=request.data['product_id'], seller_id=sellerId)            
            imgProduct = ImgProducts.objects.get(pk=pk)
            file = request.FILES['image']
            if file is not None and file.name != imgProduct.name:
                
                default_storage.save("pictures/products/"+file.name, file)
                storage.child("product_images/" +imgProduct.name).put("pictures/products/"+file.name)
                default_storage.delete("pictures/products/"+file.name)
                url = storage.child("product_images/" + imgProduct.name).get_url(None)

                data = {'product': [request.data['product_id']], 'link': [url], 'name': [imgProduct.name]}
                qdict = QueryDict('', mutable=True)
                qdict.update(MultiValueDict(data))

                serializer = ImgProductSerializer(instance=imgProduct, data=qdict)
                if not serializer.is_valid():
                    return Response({
                        'ERROR': serializer.errors,
                    }, status=status.HTTP_400_BAD_REQUEST)

                serializer.save()

            return Response({
                "message": "Updated product image is success!!",
            }, status=status.HTTP_202_ACCEPTED)

        except Exception as e:
            traceback.print_exc()
            return Response({
                "ERROR": f"Exception {e}"
            }, status=status.HTTP_403_FORBIDDEN)
    
    def destroy(self, request, pk=None):
        sellerId = self.request.user.id
        # find product base on sellerId
        try:
            imgProduct = ImgProducts.objects.get(pk=pk)
            Products.objects.get(seller_id=sellerId, img_products=imgProduct)
            if imgProduct.name is not None:
                imgProduct.delete()
                try:
                    storage.delete("product_images/" +imgProduct.name,None)
                except:
                    pass
                return Response({
                    'message': 'Delete imgProduct is Success!',
                }, status=status.HTTP_200_OK)
            return Response({
                'ERROR': imgProduct.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            traceback.print_exc()
            return Response({
                "ERROR": f" {e}!"
            }, status=status.HTTP_403_FORBIDDEN)
        

class ProductChildViewSet(viewsets.ViewSet):
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny(), ]
        if self.action in ['create', 'update', 'destroy']:
            return [group_permission.IsSeller(), ]
        return super().get_permissions()

    @action(methods=['GET'], detail=True, permission_classes=[AllowAny], url_path="product")
    def get_product_by_child(self, request,pk=None):
        try:
            product = Products.objects.get(product_childs_id=pk)
            serializers = ProductsSerializer(product)
            return Response({
                'data': serializers.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            traceback.print_exc()
            return Response({
                "ERROR": f'Exception: {e}'
            }, status=status.HTTP_404_NOT_FOUND)

    def retrieve(self, request, pk=None):
        try:
            productChild = ProductChilds.objects.get(pk=pk)
            serializers = ProductChildSerializer(productChild)
            return Response({
                'data': serializers.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            traceback.print_exc()
            return Response({
                "ERROR": f'Exception: {e}'
            }, status=status.HTTP_404_NOT_FOUND)
  
    def create(self, request):
        data = request.data
        sellerId = self.request.user.id
        try:
            product=Products.objects.get(pk=data['product_id'], seller_id=sellerId) 
            count= product.product_childs.all().count()+1  
            file = request.FILES['thumbnail_url']
            thumbnail_url= None
            name_url= None
            if file is not None:
                name_url =f"child_{product.id}_{count}"
                default_storage.save("pictures/products/"+file.name, file)
                storage.child("product_childs/" +name_url).put("pictures/products/"+file.name)
                default_storage.delete("pictures/products/"+file.name)
                thumbnail_url = storage.child("product_childs/" + name_url).get_url(None)

            data = {
                'seller': [sellerId],
                'product': [data['product_id']],
                'name': [data['name']],
                'price': [data['price']],
                'iventory_status': [data['iventory_status']],
                'thumbnail_url': [thumbnail_url],
                'name_url': [name_url]
                }
            qdict = QueryDict('', mutable=True)
            qdict.update(MultiValueDict(data))
            serializer = ProductChildSerializer(data=qdict)
            if not serializer.is_valid():
                return Response({                  
                    'ERROR': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            return Response({
                'message': 'Create speficication is Success!',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            traceback.print_exc()
            return Response({
                "ERROR": f"Exception {e}"
            }, status=status.HTTP_403_FORBIDDEN)
        
    def update(self, request, pk=None):
        data = request.data
        try:
            sellerId = self.request.user.id
            productChild = ProductChilds.objects.get(pk=pk, seller_id=sellerId)
            name_url = productChild.name_url
            if 'thumbnail_url' in request.FILES:
                file = request.FILES['thumbnail_url']
                default_storage.save("pictures/products/"+file.name, file)
                storage.child("product_childs/" +name_url).put("pictures/products/"+file.name)
                default_storage.delete("pictures/products/"+file.name)
                thumbnail_url = storage.child("product_childs/" + name_url).get_url(None)
                data['thumbnail_url']=thumbnail_url

            serializer = ProductChildSerializer(instance=productChild, data=data)

            if not serializer.is_valid():
                return Response({
                    'message': 'Update Product Child is failed!',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            return Response({
                'message': 'Update Product Child is Success!',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:          
            traceback.print_exc()
            return Response({
                "ERROR": f"Exception {e}"
            }, status=status.HTTP_403_FORBIDDEN)

    def destroy(self, request, pk=None):
        sellerId = self.request.user.id
        # find product base on sellerId
        try:
            productChild = ProductChilds.objects.get(pk=pk, seller_id=sellerId)
            if productChild.name_url is not None:
                productChild.delete()
                try:
                    storage.delete("product_childs/" +productChild.name_url,None)
                except:
                    pass
                return Response({
                    'message': 'Delete product child is Success!',
                }, status=status.HTTP_200_OK)
            return Response({
                'ERROR': productChild.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            traceback.print_exc()
            return Response({
                "ERROR": f" {e}!"
            }, status=status.HTTP_403_FORBIDDEN)


class ProductVariantViewSet(viewsets.ViewSet):

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny(), ]
        if self.action in ['create', 'update', 'destroy']:
            return [group_permission.IsSeller(), ]
        return super().get_permissions()

    def retrieve(self, request, pk=None):
        try:
            productVariant = ProductVariants.objects.get(pk=pk)           
            serializers = ProductVariantSerializer(productVariant)
            return Response({
                'data': serializers.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            traceback.print_exc()
            return Response({
                "ERROR": f" {e}!"
            }, status=status.HTTP_403_FORBIDDEN)

    def create(self, request):
        sellerId = self.request.user.id
        data = request.data
        try:
            Products.objects.get(pk=data['product'], seller_id=sellerId)
            serializer = ProductVariantSerializer(data=data)
            if not serializer.is_valid():
                return Response({
                    'ERROR': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response({
                'message': 'Create Product Variant is Success!',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            traceback.print_exc()
            return Response({
                "ERROR": f" {e}!"
            }, status=status.HTTP_403_FORBIDDEN)

    def update(self, request, pk=None):
        try:
            data = request.data
            sellerId = self.request.user.id
            productVariant = ProductVariants.objects.get(pk=pk)
            Products.objects.get(product_variants=productVariant, seller_id=sellerId)
            serializer = ProductVariantSerializer(instance=productVariant, data=data)
            if not serializer.is_valid():
                return Response({
                    'ERROR': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response({
                'message': 'Update ProductVariants is Success!',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            traceback.print_exc()
            return Response({
                "ERROR": f" {e}!"
            }, status=status.HTTP_403_FORBIDDEN)

    def destroy(self, request, pk=None):
        try:
            sellerId = self.request.user.id
            productVariant = ProductVariants.objects.get(pk=pk)
            Products.objects.get(product_variants=productVariant, seller_id=sellerId)
            productVariant.delete()
            return Response({
                'message': 'Delete ProductVariants is Success!',
            }, status=status.HTTP_200_OK)

        except Exception as e:
            traceback.print_exc()
            return Response({
                "ERROR": f" {e}!"
            }, status=status.HTTP_403_FORBIDDEN)

class OptionViewSet(viewsets.ViewSet):
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny(), ]
        if self.action in ['create', 'update', 'destroy']:
            return [group_permission.IsSeller(), ]
        return super().get_permissions()

    def retrieve(self, request, pk=None):
        try:
            productVariant = Options.objects.get(pk=pk)
            serializers = OptionSerializer(productVariant)
            return Response({
                'data': serializers.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            traceback.print_exc()
            return Response({
                "ERROR": f" {e}!"
            }, status=status.HTTP_403_FORBIDDEN)

    def create(self, request):
        data = request.data
        serializer = OptionSerializer(data=data)
        if not serializer.is_valid():
            return Response({
                'ERROR': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response({
            'message': 'Create Option is Success!',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        data = request.data
        try:
            option = Options.objects.get(pk=pk)
            serializer = OptionSerializer(instance=option, data=data)
            if not serializer.is_valid():
                return Response({
                    'ERROR': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response({
                'message': 'Update Options is Success!',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            traceback.print_exc()
            return Response({
                "ERROR": f" {e}!"
            }, status=status.HTTP_403_FORBIDDEN)

    def destroy(self, request, pk=None):
        try:
            option = Options.objects.get(pk=pk)
            if option is not None:
                option.delete()
                return Response({
                    'message': 'Delete Options is Success!',
                }, status=status.HTTP_200_OK)
            return Response({
                'ERROR': option.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            traceback.print_exc()
            return Response({
                "ERROR": f" {e}!"
            }, status=status.HTTP_403_FORBIDDEN)


class ProductListView(viewsets.ModelViewSet):
    queryset = Products.objects.all()
    serializer_class = ProductListSerializer
    filter_backends = [filters.DjangoFilterBackend, SearchFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'price']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny(), ]
        if self.action in ['create', 'update', 'destroy']:
            return [IsAdminUser()]
        return super().get_permissions()

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(methods=['GET'], detail=False, permission_classes=[AllowAny], url_path="hot")
    def list_hot_product(self, request, *args, **kwargs):
        query = self.get_queryset()
        index = query.count()
        serializer = ProductListSerializer(
            instance=query[index-10:index], many=True)
        return Response({
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=False, permission_classes=[AllowAny], url_path="similar")
    def list_similar_product(self, request, *args, **kwargs):
        query = self.filter_queryset(self.get_queryset())
        index = query.count()
        serializer = ProductListSerializer(instance=query[0:10], many=True)
        return Response({
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class CartItemViewSet(viewsets.ViewSet):
    def get_permissions(self):
        if self.action in ['list', 'create', 'update', 'destroy','delete_carts']:
            return [IsAuthenticated()]
        return super().get_permissions()

    def list(self, request):
        user = self.request.user.id
        try:
            cartItem = CartItem.objects.filter(user_id=user)
            serializers = CartItemSerializer(cartItem, many=True)
            return Response({
                'data': serializers.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            traceback.print_exc()
            return Response({
                "ERROR": f" {e}!"
            }, status=status.HTTP_403_FORBIDDEN)

    def create(self, request):
        data = request.data
        user = self.request.user.id
        if user == int(data['user']):
            variants = data['variants']
            quantity = data['quantity']
            cartItems = CartItem.objects.filter(user_id=user)
            childs = ProductChilds.objects.filter(product=data['product_id'])
            childs_option1 = childs.filter(option1 =variants[0]['value'])
            try:          
                child = childs_option1.get(option2=variants[1]['value'])
                # else:
                #     child = childs_option1[0]

            except:
                child = childs_option1[0]
                
            try:
                # if product child exists
                cartExist = cartItems.get(product_child=child)
                data = {
                    'user': [user],
                    'product_child': [child.pk],
                    'quantity': [quantity+cartExist.quantity]
                }
                qdict = QueryDict('', mutable=True)
                qdict.update(MultiValueDict(data))
                serializer = CartItemSerializer(instance=cartExist, data=qdict)

                if not serializer.is_valid():
                    return Response({
                        'ERROR': serializer.errors
                    }, status=status.HTTP_400_BAD_REQUEST)
                serializer.save()
                return Response({
                    'message': 'update product into cart is success!',
                    'data': serializer.data
                }, status=status.HTTP_200_OK)
            except:
                # else product child chưa exists
                data = {
                    'user': [user],
                    'product_child': [child.pk],
                    'quantity': [quantity]
                }
                qdict = QueryDict('', mutable=True)
                qdict.update(MultiValueDict(data))
                serializer = CartItemSerializer(data=qdict)

                if not serializer.is_valid():
                    return Response({
                        'ERROR': serializer.errors
                    }, status=status.HTTP_400_BAD_REQUEST)

                serializer.save()
                return Response({
                    'message': 'Add product into cart is success!',
                    'data': serializer.data
                }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                "ERROR": f" No permission!"
            }, status=status.HTTP_403_FORBIDDEN)

    def update(self, request, pk=None):
        data = request.data
        userId = self.request.user.id
        try:
            item = CartItem.objects.get(pk=pk, user_id =userId)
            serializer = CartItemSerializer(instance=item, data=data)

            if not serializer.is_valid():
                return Response({
                    'ERROR': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            return Response({
                'message': 'Update product into cart is success!',
                'data': serializer.data,
            }, status=status.HTTP_200_OK)
        except Exception as e:
            traceback.print_exc()
            return Response({
                "ERROR": f" {e}!"
            }, status=status.HTTP_403_FORBIDDEN)

    @action(methods=['POST'], detail=False, permission_classes=[IsAuthenticated], url_path="delete")
    def delete_carts(self,request):
        try:
            carts = request.data['carts']
            for cartId in carts:
                item = CartItem.objects.filter(pk=cartId)             
                item.delete()

            return Response({
                'message': 'Delete product out Cart Item is Success!',
            }, status=status.HTTP_200_OK)

               
        except Exception as e:
            traceback.print_exc()
            return Response({
                "ERROR": f" {e}!"
            }, status=status.HTTP_403_FORBIDDEN)
    def destroy(self, request, pk=None):
        try:
            item = CartItem.objects.get(pk=pk)
            if item is not None:
                item.delete()
                return Response({
                    'message': 'Delete product out Cart Item is Success!',
                }, status=status.HTTP_200_OK)

            return Response({
                'ERROR': item.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            traceback.print_exc()
            return Response({
                "ERROR": f" {e}!"
            }, status=status.HTTP_403_FORBIDDEN)


class InteractiveViewSet(viewsets.ViewSet):
    serializer_class = InteractiveSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny(), ]
        if self.action in ['create']:
            return [group_permission.IsUser()]
        return super().get_permissions()

    def create(self, request):
        data = request.data
        userId= self.request.user.id
        try:
            Interactive.objects.get(user_id=userId, product =data['product'])
            return Response({
                "ERROR": "Only evaluated one time!"
            }, status=status.HTTP_403_FORBIDDEN)
        except:
            try :
                # child = ProductChilds.objects.get(product=data['product'])
                PurchasedProduct.objects.get(user_id=userId,product_id =data['product'])           
                if 'link' in request.FILES:
                    file = request.FILES['link']
                    default_storage.save("pictures/products/"+file.name, file)
                    storage.child("comment_image/" +file.name).put("pictures/products/"+file.name)
                    default_storage.delete("pictures/products/"+file.name)
                    url = storage.child("comment_image/" + file.name).get_url(None)
                    data['link'] = url
                serializer = InteractiveSerializer(data=data)
                if not serializer.is_valid():
                    return Response({
                        'ERROR': serializer.errors,
                    }, status=status.HTTP_400_BAD_REQUEST)

                serializer.save()
                return Response({
                    'message': "Evaluate product is Success!",
                    'data': serializer.data
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                traceback.print_exc()
                return Response({
                    "ERROR": f"Not allowed to evaluate product! {e}"
                }, status=status.HTTP_403_FORBIDDEN)


listFilters = [
    {
        "Ram": [
            {"display_value": "1GB", "query_value": "ram=1GB"},
            {"display_value": "2GB", "query_value": "ram=2GB"},
            {"display_value": "4GB", "query_value": "ram=4GB"},
            {"display_value": "8GB", "query_value": "ram=8GB"},
            {"display_value": "16GB", "query_value": "ram=16GB"},
        ],
        "Rom": [
            {"display_value": "16GB", "query_value": "rom=16GB"},
            {"display_value": "32GB", "query_value": "rom=32GB"},
            {"display_value": "64GB", "query_value": "rom=64GB"},
            {"display_value": "128GB", "query_value": "rom=128GB"},
            {"display_value": "256GB", "query_value": "rom=256GB"},
        ],
        "Price": [
            {"display_value": "Dưới 2.500.000", "query_value": "price_lte=2500000"},
            {"display_value": "2.500.000 -> 6.000.000",
             "query_value": "price_gte=2500000&price_lte=6000000"},
            {"display_value": "6.000.000 -> 25.500.000",
             "query_value": "price_gte=6000000&price_lte=25500000"},
            {"display_value": "Trên 25.500.000",
                "query_value": "price_gte=25500000"},
        ]
    }
]
