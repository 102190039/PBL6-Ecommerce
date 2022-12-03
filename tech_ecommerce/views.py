
from django.http.request import QueryDict, MultiValueDict
from rest_framework import generics, viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from authenticate import group_permission
from tech_ecommerce.filters import ProductFilter
from tech_ecommerce.models import Interactive, CartItem, Categories, ImgProducts, Options, ProductChilds, ProductVariants, Products, Speficication
from tech_ecommerce.serializers import CartItemSerializer, CategorySerializer, ImgProductSerializer, InteractiveSerializer, OptionSerializer, ProductChildSerializer, ProductVariantSerializer, ProductsSerializer, SpeficicationSerializer
from django_filters import rest_framework as filters
from rest_framework.decorators import action
from django.core.files.storage import default_storage
from config_firebase.config import storage

# Create your views here.


class ProductViewSet(viewsets.ViewSet):
    serializer_class = ProductsSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'create', 'update', 'destroy']:
            return [AllowAny(), ]
        return super().get_permissions()

    def list(self, request):
        queryset = Products.objects.all()
        serializer = ProductsSerializer(queryset, many=True)
        return Response({'data': serializer.data}, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        product = Products.objects.filter(pk=pk).get()
        serializer = ProductsSerializer(product)
        return Response({'data': serializer.data}, status=status.HTTP_200_OK)

    def create(self, request):
        serialier_product = ProductsSerializer(data=request.data)
        if not serialier_product.is_valid():
            return Response({
                "message": "Create product is Failed!",
                "errors": serialier_product.errors
            },
                status=status.HTTP_404_NOT_FOUND
            )
        product = serialier_product.save()
        for file in request.FILES.getlist('img_products'):
            file_save = default_storage.save("pictures/"+file.name, file)
            storage.child("multi/" + file.name).put("pictures/"+file.name)
            delete = default_storage.delete("pictures/"+file.name)
            url = storage.child("multi/" + file.name).get_url(None)
            data = {'product': [product.id], 'link': [url]}
            qdict = QueryDict('', mutable=True)
            qdict.update(MultiValueDict(data))
            serializer_img = ImgProductSerializer(data=qdict)
            if not serializer_img.is_valid():
                return Response({
                    'message': "File upload is failed!",
                    'error': serializer_img.errors,
                }, status=status.HTTP_400_BAD_REQUEST)
            serializer_img.save()

        return Response({
            "message": "Create product is success!"
        },
            status=status.HTTP_201_CREATED
        )

    def update(self, request, pk=None):
        product = Products.objects.filter(pk=pk).get()
        serializer = ProductsSerializer(instance=product, data=request.data)
        if not serializer.is_valid():
            return Response({
                "message": "Product updated is failed!",
                "errors": serializer.errors,
            }
            )
        serializer.save()
        return Response({
            "message": "Product updated is sucess!"
        },
            status=status.HTTP_204_NO_CONTENT
        )

    def destroy(self, request, pk=None):
        product = Products.objects.filter(pk=pk).get()

        category = product.category
        category.total = category.total-1
        seller = product.seller
        seller.product_count = seller.product_count-1

        seller.save()
        category.save()
        product.delete()
        return Response({
            "message": "Product deleted is success!"
        })

    @action(methods=['GET'], detail=False, permission_classes=[AllowAny], url_path="list-filters")
    def get_filters(self, request):
        return Response({"filters": list_filters}, status=status.HTTP_200_OK)


class CategoryViewSet(viewsets.ViewSet):
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'update', 'create', 'destroy']:
            return [AllowAny(), ]
        # elif self.action in ['create','update', 'delete']:
        #     return [group_permission.IsAdmin(), group_permission.IsStaff()]
        return super().get_permissions()

    def list(self, request):
        queryset = Categories.objects.all()
        serializer = CategorySerializer(queryset, many=True)
        return Response({'data':serializer.data}, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        category = Categories.objects.filter(pk=pk).get()
        serializer = CategorySerializer(category)
        return Response({'data':serializer.data}, status=status.HTTP_200_OK)

    def create(self, request):
        data = request.data
        serializer = CategorySerializer(data=data)
        if not serializer.is_valid():
            return Response({
                "message": "Create is Failed!",
                "error": serializer.errors,
            })
        serializer.save()
        return Response({
            'message': 'You create category is success!'
        },
            status=status.HTTP_200_OK
        )

    def update(self, request, pk=None):
        category = Categories.objects.filter(pk=pk).get()
        data = request.data
        serializer = CategorySerializer(instance=category, data=data)
        if not serializer.is_valid():
            return Response({
                "message": "Update is Failed!",
                "error": serializer.errors,
            })
        serializer.save()
        return Response({
            "message": "Updated is success!"
        },
            status=status.HTTP_204_NO_CONTENT
        )

    def destroy(self, request, pk=None):
        category = Categories.objects.filter(pk=pk).get()
        category.delete()
        return Response({"message": "delete category is success!"})


class ImgProductViewSet(viewsets.ViewSet):
    serializer_class = ImgProductSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'create', 'update', 'destroy']:
            return [AllowAny(), ]
        # elif self.action in ['create','update', 'delete']:
        #     return [group_permission.IsAdmin(), group_permission.IsStaff()]
        return super().get_permissions()

    def list(self, request):
        queryset = ImgProducts.objects.all()
        serializers = ImgProductSerializer(queryset, many=True)
        return Response({'data':serializers.data}, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        img_product = ImgProducts.objects.filter(pk=pk).get()
        img_products = ImgProducts.objects.filter(
            product_id=img_product.product)
        serializers = ImgProductSerializer(img_products, many=True)
        return Response({'data':serializers.data}, status=status.HTTP_200_OK)

    def create(self, request):
        for file in request.FILES.getlist('img'):
            file_save = default_storage.save("pictures/"+file.name, file)
            storage.child("img_product/" + file.name).put("pictures/"+file.name)
            delete = default_storage.delete("pictures/"+file.name)
            url = storage.child("img_product/" + file.name).get_url(None)
            data = {'product': [request.data['product_id']], 'link': [url]}
            qdict = QueryDict('', mutable=True)
            qdict.update(MultiValueDict(data))

            serializer = ImgProductSerializer(data=qdict)
            if not serializer.is_valid():
                return Response({
                    'message': "File upload in Firebase Storage faile!",
                    'error': serializer.errors,
                })
            serializer.save()
        return Response({
            'message': "File upload in Firebase Storage successful",
            'data': serializer.data
        },
            status=status.HTTP_200_OK
        )

    def update(self, request, pk=None):
        img_product = ImgProducts.objects.filter(pk=pk).get()
        file = request.FILES['img']
        if file is not None:
            file_save = default_storage.save("pictures/"+file.name, file)
            storage.child("img_product/" + file.name).put("pictures/"+file.name)
            delete = default_storage.delete("pictures/"+file.name)
            url = storage.child("img_product/" + file.name).get_url(None)
            data = {'product': [request.data['product_id']], 'link': [url]}
            qdict = QueryDict('', mutable=True)
            qdict.update(MultiValueDict(data))

            serializer = ImgProductSerializer(instance=img_product, data=qdict)
            if not serializer.is_valid():
                return Response({
                    'message': "Updated img_product is failed!",
                    'error': serializer.errors,
                })
            serializer.save()
        else:
            url = request.data['link']
            data = {'product': [request.data['product_id']], 'link': [url]}
            qdict = QueryDict('', mutable=True)
            qdict.update(MultiValueDict(data))

            serializer = ImgProductSerializer(instance=img_product, data=qdict)
            if not serializer.is_valid():
                return Response({
                    'message': "Updated img_product is failed!",
                    'error': serializer.errors,
                })
            serializer.save()
        return Response({
            "message": "Updated img_product is success!!"
        },
            status=status.HTTP_204_NO_CONTENT
        )

    def destroy(self, request, pk=None):
        img_product = ImgProducts.objects.filter(pk=pk).get()
        if img_product is not None:
            img_product.delete()
            return Response({
                'message': 'Delete img_product is Success!',
            },
                status=status.HTTP_200_OK
            )
        return Response({
            'message': 'Delete img_product is failed!',
            'errors': img_product.errors
        },
            status=status.HTTP_400_BAD_REQUEST
        )


class SpeficicationViewSet(viewsets.ViewSet):
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'create', 'update', 'destroy']:
            return [AllowAny(), ]
        return super().get_permissions()

    def list(self, request):
        queryset = Speficication.objects.all()
        serializers = SpeficicationSerializer(queryset, many=True)
        return Response(serializers.data)

    def retrieve(self, request, pk=None):
        speficication = Speficication.objects.filter(pk=pk).get()
        serializer = SpeficicationSerializer(speficication)
        return Response({'data': serializer.data}, status=status.HTTP_200_OK)

    def create(self, request):
        data = request.data
        serializer = SpeficicationSerializer(data=data)
        if not serializer.is_valid():
            return Response({
                'message': 'Create speficication is failed!',
                'errors': serializer.errors
            },
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer.save()
        return Response({
            'message': 'Create speficication is Success!',
            'data': serializer.data
        },
            status=status.HTTP_201_CREATED
        )

    def update(self, request, pk=None):
        data = request.data
        speficication = Speficication.objects.filter(pk=pk).get()
        serializer = SpeficicationSerializer(speficication, data=data)
        if not serializer.is_valid():
            return Response({
                'message': 'Update speficication is failed!',
                'errors': serializer.errors
            },
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer.save()
        return Response({
            'message': 'Update speficication is Success!',
            'data': serializer.data
        },
            status=status.HTTP_200_OK
        )

    def destroy(self, request, pk=None):
        speficication = Speficication.objects.filter(pk=pk).get()
        if speficication is not None:
            speficication.delete()
            return Response({
                'message': 'Delete speficication is Success!',
            },
                status=status.HTTP_200_OK
            )
        return Response({
            'message': 'Update speficication is failed!',
            'errors': speficication.errors
        },
            status=status.HTTP_400_BAD_REQUEST
        )


class ProductChildViewSet(viewsets.ViewSet):
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'create', 'update', 'destroy']:
            return [AllowAny(), ]
        return super().get_permissions()

    def list(self, request):
        queryset = ProductChilds.objects.all()
        serializers = ProductChildSerializer(queryset, many=True)
        return Response(serializers.data)

    def retrieve(self, request, pk=None):
        product_child = ProductChilds.objects.filter(pk=pk).get()

        product_childs = ProductChilds.objects.filter(
            product_id=product_child.product, 
            seller_id=product_child.seller
        )
        serializers = ProductChildSerializer(product_childs, many=True)
        return Response(serializers.data)

    def create(self, request):
        data = request.data
        serializer = ProductChildSerializer(data=data)
        if not serializer.is_valid():
            return Response({
                'message': 'Create speficication is failed!',
                'errors': serializer.errors
            },
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer.save()
        return Response({
            'message': 'Create speficication is Success!',
            'data': serializer.data
        },
            status=status.HTTP_201_CREATED
        )

    def update(self, request, pk=None):
        data = request.data
        product_child = ProductChilds.objects.filter(pk=pk).get()
        serializer = ProductChildSerializer(instance=product_child, data=data)
        if not serializer.is_valid():
            return Response({
                'message': 'Update Product Child is failed!',
                'errors': serializer.errors
            },
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer.save()
        return Response({
            'message': 'Update Product Child is Success!',
            'data': serializer.data
        },
            status=status.HTTP_200_OK
        )

    def destroy(self, request, pk=None):
        product_child = ProductChilds.objects.filter(pk=pk).get()
        if product_child is not None:
            product_child.delete()
            return Response({
                'message': 'Delete product_child is Success!',
            },
                status=status.HTTP_200_OK
            )
        return Response({
            'message': 'Delete product_child is failed!',
            'errors': product_child.errors
        },
            status=status.HTTP_400_BAD_REQUEST
        )


class ProductVariantViewSet(viewsets.ViewSet):

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'create', 'update', 'destroy']:
            return [AllowAny(), ]
        return super().get_permissions()

    @action(methods=['GET'],detail=False,permission_classes=[AllowAny],url_path="list-variant")
    def list_variant(self, request):
        id=request.query_params['product_id']
        queryset = ProductVariants.objects.filter(product=id)
        serializers = ProductVariantSerializer(queryset, many=True)
        return Response(serializers.data)

    def retrieve(self, request, pk=None):
        product_variant = ProductVariants.objects.filter(pk=pk).get()
        serializers = ProductVariantSerializer(product_variant)
        return Response(serializers.data)

    def create(self, request):
        data = request.data
        serializer = ProductVariantSerializer(data=data)
        if not serializer.is_valid():
            return Response({
                'message': 'Create Product_Variant is failed!',
                'errors': serializer.errors
            },
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer.save()
        return Response({
            'message': 'Create Product_Variant is Success!',
            'data': serializer.data
        },
            status=status.HTTP_201_CREATED
        )

    def update(self, request, pk=None):
        data = request.data
        product_variant = ProductVariants.objects.filter(pk=pk).get()
        serializer = ProductVariantSerializer(
            instance=product_variant, data=data)
        if not serializer.is_valid():
            return Response({
                'message': 'Update ProductVariants is failed!',
                'errors': serializer.errors
            },
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer.save()
        return Response({
            'message': 'Update ProductVariants is Success!',
            'data': serializer.data
        },
            status=status.HTTP_200_OK
        )

    def destroy(self, request, pk=None):
        product_variant = ProductVariants.objects.filter(pk=pk).get()
        if product_variant is not None:
            product_variant.delete()
            return Response({
                'message': 'Delete ProductVariants is Success!',
            },
                status=status.HTTP_200_OK
            )
        return Response({
            'message': 'Delete ProductVariants is failed!',
            'errors': product_variant.errors
        },
            status=status.HTTP_400_BAD_REQUEST
        )


class OptionViewSet(viewsets.ViewSet):
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'create', 'update', 'destroy']:
            return [AllowAny(), ]
        return super().get_permissions()
    def retrieve(self, request, pk=None):
        product_variant = Options.objects.filter(pk=pk).get()
        serializers = OptionSerializer(product_variant)
        return Response(serializers.data)

    def create(self, request):
        data = request.data
        serializer = OptionSerializer(data=data)
        if not serializer.is_valid():
            return Response({
                'message': 'Create Option is failed!',
                'errors': serializer.errors
            },
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer.save()
        return Response({
            'message': 'Create Option is Success!',
            'data': serializer.data
        },
            status=status.HTTP_201_CREATED
        )

    def update(self, request, pk=None):
        data = request.data
        option = Options.objects.filter(pk=pk).get()
        serializer = OptionSerializer(instance=option, data=data)
        if not serializer.is_valid():
            return Response({
                'message': 'Update Options is failed!',
                'errors': serializer.errors
            },
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer.save()
        return Response({
            'message': 'Update Options is Success!',
            'data': serializer.data
        },
            status=status.HTTP_200_OK
        )

    def destroy(self, request, pk=None):
        option = Options.objects.filter(pk=pk).get()
        if option is not None:
            option.delete()
            return Response({
                'message': 'Delete Options is Success!',
            },
                status=status.HTTP_200_OK
            )
        return Response({
            'message': 'Delete Options is failed!',
            'errors': option.errors
        },
            status=status.HTTP_400_BAD_REQUEST
        )


class ProductList(generics.ListAPIView):
    queryset = Products.objects.all()
    serializer_class = ProductsSerializer
    permission_classes = [AllowAny]
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ProductFilter
    search_fields = ('^name', '=category', '=seller',)


class CartItemViewSet(viewsets.ViewSet):
    def get_permissions(self):
        if self.action in ['create', 'update', 'destroy']:
            return [AllowAny(), ]
        if self.action in ['list']:
            return [IsAuthenticated()]
        return super().get_permissions()
    def list(self, request):
        user = self.request.user.id
        cart_item = CartItem.objects.filter(user_profile_id=user)
        serializer = CartItemSerializer(cart_item, many=True)
        return Response({'data': serializer.data})
    def create(self, request):
        data = request.data
        obj_variants = data['variants']
        obj_product_id = data['product_id']
        obj_quantity = data['quantity']

        # id product => id variants
        variants = ProductVariants.objects.filter(product_id=obj_product_id)
        # id variant => value option
        arr_product_childs = []
        option = Options.objects.all()
        for idx in range(0, len(variants)):
            options = option.filter(
                product_variant_id=variants[idx].id, value=obj_variants[idx]['value'])
            if options.exists():
                arr_product_childs.append(options)
        # if exist value Dung Lượng => len = 2
        if len(arr_product_childs) > 1:
            list_product_child = arr_product_childs[0].union(
                arr_product_childs[1], all=True)
        # else don't exist value Dung Lượng => len = 1
        else:
            list_product_child = arr_product_childs[0]
        list_child_id = []
        for product_child in list_product_child:
            list_child_id.append(product_child.product_child_id)
        # tim id_child_Mau == id_child_DungLuong
        # K exist Dung Luong => id_Child_Mau
        child_id = list_child_id[0]
        for i in range(0, len(list_child_id)):
            for j in range(i+1, len(list_child_id)):
                if list_child_id[i] == list_child_id[j]:
                    child_id = list_child_id[i]
                    break

        userProfile = data['user_profile']
        cart_items = CartItem.objects.filter(user_profile_id=userProfile)
        try:
            cartExist = cart_items.get(product_child_id=child_id)
            data = {'user_profile': [userProfile], 'product_child': [
                child_id], 'quantity': [obj_quantity+cartExist.quantity]}
            qdict = QueryDict('', mutable=True)
            qdict.update(MultiValueDict(data))
            serializer = CartItemSerializer(instance=cartExist, data=qdict)

            if not serializer.is_valid():
                return Response({'message': 'Add product into cart is failed!',
                                 'errors': serializer.errors},
                                status=status.HTTP_400_BAD_REQUEST
                                )
            serializer.save()
            return Response({'message': 'update product into cart is success!',
                             'data': serializer.data},
                            status=status.HTTP_200_OK
                            )
        except:
            data = {'user_profile': [userProfile], 'product_child': [
                child_id], 'quantity': [obj_quantity]}
            qdict = QueryDict('', mutable=True)
            qdict.update(MultiValueDict(data))
            serializer = CartItemSerializer(data=qdict)
            if not serializer.is_valid():
                return Response({'message': 'Add product into cart is failed!',
                                 'errors': serializer.errors},
                                status=status.HTTP_400_BAD_REQUEST
                                )
            serializer.save()
            return Response({
                'message': 'Add product into cart is success!',
                'data': serializer.data
            },
                status=status.HTTP_200_OK
            )

    def update(self, request, pk=None):
        data = request.data
        item = CartItem.objects.get(pk=pk)
        serializer = CartItemSerializer(instance=item, data=data)
        if not serializer.is_valid():
            return Response({'message': 'Update product into cart is failed!',
                             'errors': serializer.errors
                             },
                            status=status.HTTP_400_BAD_REQUEST
                            )
        serializer.save()
        return Response({
            'message': 'Update product into cart is success!',
            'data': serializer.data,
        },
            status=status.HTTP_200_OK
        )

    def destroy(self, request, pk=None):
        item = CartItem.objects.filter(pk=pk).get()
        if item is not None:
            item.delete()
            return Response({
                'message': 'Delete product out Cart Item is Success!',
            },
                status=status.HTTP_200_OK
            )
        return Response({
            'message': 'Delete product out CartItem is failed!',
            'errors': item.errors
        },
            status=status.HTTP_400_BAD_REQUEST
        )


class InteractiveViewSet(viewsets.ViewSet):
    serializer_class = InteractiveSerializer
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'create', 'update', 'destroy']:
            return [AllowAny(), ]
        return super().get_permissions()
    def list(self, request):
        data = request.GET
        product = data['product_id']
        interactives = Interactive.objects.filter(product=product)
        serializers = InteractiveSerializer(interactives, many=True)
        return Response({'data':serializers.data}, status=status.HTTP_200_OK)
    def retrieve(self, request, pk=None):
        interactive = Interactive.objects.get(pk=pk)
        serializers = InteractiveSerializer(interactive)
        return Response({'data':serializers.data}, status=status.HTTP_200_OK)

    def create(self, request):
        data = request.data
        product = data['product_id']
        userProfile = data['user_profile']
        favorite = data['favorite']
        comment = data['comment']
        rating = data['rating']
        interactive_exist = Interactive.objects.filter(user_profile_id=userProfile)
        if interactive_exist.exists():
            return Response({
                'message': "interactive product is failed!",
                'error': "interactive product invalid!",
            })
        try:
            file = request.FILES['img']
            file_save = default_storage.save("pictures/"+file.name, file)
            storage.child("img_interactive/" + file.name).put("pictures/"+file.name)
            delete = default_storage.delete("pictures/"+file.name)
            url = storage.child("img_interactive/" + file.name).get_url(None) 
        except:
            url = ''
        data = {
                'product': [product], 
                'user_profile' : [userProfile], 
                'favorite': [favorite],
                'comment': [comment],
                'link': [url],
                'rating': [rating]
            }
        qdict = QueryDict('', mutable=True)
        qdict.update(MultiValueDict(data))
        serializer = InteractiveSerializer(data=qdict)
        if not serializer.is_valid():
            return Response({
                'message': "Evaluate product is failed!",
                'error': serializer.errors,
            })
        serializer.save()
        return Response({
            'message': "Evaluate product is Success!",
            'data': serializer.data
        },
            status=status.HTTP_200_OK
        )


list_filters = [
{
    "Ram": [
        {"display_value": "1GB","query_value": "ram=1GB"},
        {"display_value": "2GB","query_value": "ram=2GB"},
        {"display_value": "4GB","query_value": "ram=4GB"},
        {"display_value": "8GB","query_value": "ram=8GB"},
        {"display_value": "16GB","query_value": "ram=16GB"},                                  
    ],
    "Rom":[
        {"display_value": "16GB","query_value": "rom=16GB"},
        {"display_value": "32GB","query_value": "rom=32GB"},
        {"display_value": "64GB","query_value": "rom=64GB"},
        {"display_value": "128GB","query_value": "rom=128GB"},
        {"display_value": "256GB","query_value": "rom=256GB"},  
    ],
    "Price":[
        {"display_value": "Dưới 2.500.000","query_value": "price_lte=2500000"},
        {"display_value": "2.500.000 -> 6.000.000","query_value": "price_gte=2500000&price_lte=6000000"},
        {"display_value": "6.000.000 -> 25.500.000","query_value": "price_gte=6000000&price_lte=25500000"},
        {"display_value": "Trên 25.500.000","query_value": "price_gte=25500000"},                   
    ]
}
]
