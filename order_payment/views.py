import traceback
from datetime import date
from rest_framework.viewsets import ViewSet
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from authenticate import group_permission
from authenticate.models import UserProfile
from config_firebase.PayPal import PayPal
from order_payment.models import Order, OrderDetail, PayIn, PayOut, Payment, PurchasedProduct
from order_payment.serializer import OrderDetailSerializer, OrderSerializer, PayInSerializer, PayOutSerializer, PurchasedProductSerializer
from rest_framework import status
from rest_framework.decorators import action
import requests

class OrderViewSet(ViewSet):
    def get_permissions(self):
        if self.action in ['retrieve', 'create', 'destroy']:
            return [group_permission.IsUser() ]
        return super().get_permissions()

    def retrieve(self, request, pk=None):
        try:
            order = Order.objects.get(pk=pk, user_id=self.request.user.id)
            serializer = OrderSerializer(order)
            return Response({'data': serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "ERROR": f" {e}!"
            }, status=status.HTTP_403_FORBIDDEN)

    @action(methods=['GET'], detail=True, permission_classes=[AllowAny], url_path="details")
    def get_details(self, request, pk=None):
        try:
            orderDetails = OrderDetail.objects.filter(order_id= pk)
            serializer = OrderDetailSerializer(orderDetails)
            return Response({'data': serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "ERROR": f" {e}!"
            }, status=status.HTTP_403_FORBIDDEN)

    def create(self, request):       
        data = request.data
        userId = self.request.user.id
        try:
            profile = UserProfile.objects.get(pk=userId)
            if profile.address is not None:
                data['user']= userId
                serializer = OrderSerializer(data=data)
                if not serializer.is_valid():
                    return Response({
                        'ERROR': serializer.errors,
                    }, status=status.HTTP_400_BAD_REQUEST,)
                serializer.save()
                return Response({
                    'message':'Order is Success!',
                    'data':serializer.data
                }, status=status.HTTP_201_CREATED,)
            else:
                return Response({
                    'ERROR':'Address is not NULL',
                }, status=status.HTTP_403_FORBIDDEN,)
        except Exception as e:
            traceback.print_exc()
            return Response({              
                "ERROR": f"Exception {e}!"
            }, status=status.HTTP_403_FORBIDDEN)


    def destroy(self, request, pk=None):
        try:
            order = Order.objects.get(pk=pk, user_id=self.request.user.id)
            order.delete()
            return Response({
                'message':'Delete order is success',
            }, status=status.HTTP_200_OK,)
        except Exception as e:
            return Response({
                "ERROR": f" {e}!"
            }, status=status.HTTP_403_FORBIDDEN)


class OrderDetailViewSet(ViewSet):
    def get_permissions(self):
        if self.action in ['retrieve']:
            return [group_permission.IsUser() ]
        return super().get_permissions()


    def retrieve(self, request, pk=None):
        try:
            userId = self.request.user.id
            orderDetail = OrderDetail.objects.get(pk=pk)
            if orderDetail.order.user_id == userId:
                serializer = OrderDetailSerializer(orderDetail)
                return Response({
                    'data': serializer.data
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'ERROR': 'Not allowed!'
                }, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({
                "ERROR": f" {e}!"
            }, status=status.HTTP_403_FORBIDDEN)
        

def TransferMoneys(userId,order):
    listOrderDetails = OrderDetail.objects.filter(order=order)
    # Get list of order details to transfer money for seller
    for orderDetail in listOrderDetails:
        # add bought products
        PurchasedProduct.objects.create(
            user_id=userId, 
            seller=orderDetail.seller, 
            product_id = orderDetail.product_child.product_id,
            quantity = orderDetail.quantity,
            total_price = orderDetail.total_price)
        payOut = PayOut.objects.get(seller=orderDetail.seller)
        payOut.current_balance += orderDetail.total_price /25000        
        payOut.save()


class PayPalView(ViewSet):
    permission_classes = [AllowAny]
    def get_permissions(self):
        if self.action in ['Withdrawal']:
            return [group_permission.IsSeller() ]
        else:
            return [AllowAny() ]

    # Customer successful paid
    @action(methods=['GET'],detail=True,permission_classes=[AllowAny],url_path="succeeded")
    def get_return_payment(self, request, pk=None):
        try:        
            payIn= PayIn.objects.get(pk=pk)
            # Post Paypal API to capture customer checkout
            Authtoken = PayPal().GetToken()
            orderId = request.query_params['token']
            userId=request.query_params['user_id']
            captureurl = f'https://api.sandbox.paypal.com/v2/checkout/orders/{orderId}/capture'#see transaction status
            headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer "+Authtoken}
            response = requests.post(captureurl, headers=headers)
            Payment.objects.create(
                pay_in= payIn,
                money= payIn.number_money,
                )
            # transfer money for seller
            TransferMoneys(userId,payIn.order_id)
            # Update status payment -> Payment successful
            payIn.status_payment =True
            payIn.received_time = date.today()
            payIn.save()
            
            return Response({
                'message':'Payment successful'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': f'Exception: {e}'
            }, status=status.HTTP_400_BAD_REQUEST)

    # customer cancels payment
    @action(methods=['GET'],detail=True,permission_classes=[AllowAny],url_path="failed")
    def get_cancel_payment(self, request, pk=None):
        try:
            payIn= PayIn.objects.get(pk=pk)
            payIn.status_payment =False
            payIn.save()
            return Response({
                'message': 'Checkout is cancel'
            }, status=status.HTTP_200_OK)
        except:
            return Response({
                'error': 'Pay In not exist'
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['POST'],detail=False,permission_classes=[AllowAny],url_path="withdrawal") 
    def Withdrawal(self, request):
        try:
            money = float(request.data['money'])
            userId = self.request.user.id
            payOut= PayOut.objects.get(seller=userId)
            if payOut.current_balance < money:
                return Response({
                    'ERROR': 'Your account is not enough to make this transaction'
                }, status=status.HTTP_400_BAD_REQUEST)
            if payOut.account == None:
                return Response({
                    'ERROR': 'Your account is not null'
                }, status=status.HTTP_400_BAD_REQUEST)

            response=PayPal().PayOut(email= payOut.account,money= money)
            if response.status_code <400:
                link = response.json()['links'][0]['href']
                payOut.current_balance -= money
                payOut.save()
                Payment.objects.create(pay_out=payOut,money=money)
                return Response({
                    'message': f'Transaction is successfull {link}'
                }, status=status.HTTP_202_ACCEPTED)
            else:
                return Response({
                    'ERROR': 'Please enter account again'
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                'ERROR': f'Exception: {e}'
            }, status=status.HTTP_400_BAD_REQUEST)


class PayInViewSet(ViewSet):
    def get_permissions(self):
        if self.action in ['retrieve','create','destroy']:
            return [group_permission.IsUser()]
        return super().get_permissions()

    def retrieve(self, request, pk=None):
        try:
            userId = self.request.user.id
            payIn = PayIn.objects.get(pk=pk)
            if payIn.order.user_id == userId:
                serializer = PayInSerializer(payIn)
                return Response({
                    'data': serializer.data
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'ERROR': 'Not allowed!'
                }, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({
                "ERROR": f" {e}!"
            }, status=status.HTTP_403_FORBIDDEN)

    def create(self, request):
        try:
            data= request.data
            userId = self.request.user.id
            order=Order.objects.get(user_id=userId,pk= data['order'])
            serializer = PayInSerializer(data = data)

            if not serializer.is_valid():
                return Response({
                    'ERROR': serializer.errors,
                },status=status.HTTP_400_BAD_REQUEST)       
            serializer.save()
            

            if data['type_payment']=="online":
                pay_in_id= int(serializer.data['id'])
                money= float(serializer.data['number_money']) 

                linkForPayment=PayPal().CreateOrder(pay_in_id, money,userId)   
                if linkForPayment=="ERROR":  
                    return Response({'ERROR'}, status=status.HTTP_400_BAD_REQUEST)
                return Response({'link_payment': linkForPayment}, status=status.HTTP_200_OK)
            return Response({"message":"Check out is succesfull"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "ERROR": f" {e}!"
            }, status=status.HTTP_403_FORBIDDEN)
        
    def destroy(self, request, pk=None):
        try: 
            userId = self.request.user.id
            payIn= PayIn.objects.get(pk=pk)
            purchase=purchase.objects.get(user_id=userId, order=payIn.order)
            purchase.status_payment= 'canceled'
            purchase.save()
            payIn.delete()
        except Exception as e:
            return Response({
                "ERROR": f" {e}!"
            }, status=status.HTTP_403_FORBIDDEN)

class PurchasedProductView(ViewSet):
    queryset = PurchasedProduct.objects.all()
    serializer_class = PurchasedProductSerializer

    def get_permissions(self):
        if self.action in ['retrieve','list']:
            return [group_permission.IsUser()]
        if self.action in ['list_by_seller']:
            return [group_permission.IsSeller()]
        return super().get_permissions()
    def list(self, request):
        try:
            params=request.query_params 
            userId= self.request.user.id
            if 'status' in params:
                purchase= PurchasedProduct.objects.filter(user=userId, status_purchase = params['status'])
                serializers = PurchasedProductSerializer(instance=purchase,many=True)
                return Response({
                        'data': serializers.data
                    }, status=status.HTTP_200_OK) 
            else:
                purchase= PurchasedProduct.objects.filter(user=userId)
                serializers = PurchasedProductSerializer(instance=purchase,many=True)
                return Response({
                        'data': serializers.data
                    }, status=status.HTTP_200_OK) 
        except Exception as e:
            traceback.print_exc()
            return Response({              
                "ERROR": f"Exception {e}!"
            }, status=status.HTTP_403_FORBIDDEN)

    @action(methods=['GET'],detail=False,permission_classes=[AllowAny],url_path="seller")
    def list_by_seller(self, request):
        try:
            params=request.query_params 
            userId= self.request.user.id
            if 'status' in params:
                purchase= PurchasedProduct.objects.filter(seller=userId, status_purchase = params['status'])
                serializers = PurchasedProductSerializer(instance=purchase,many=True)
                return Response({
                        'data': serializers.data
                    }, status=status.HTTP_200_OK) 
            else:
                purchase= PurchasedProduct.objects.filter(seller=userId)
                serializers = PurchasedProductSerializer(instance=purchase,many=True)
                return Response({
                        'data': serializers.data
                    }, status=status.HTTP_200_OK) 
        except Exception as e:
            traceback.print_exc()
            return Response({              
                "ERROR": f"Exception {e}!"
            }, status=status.HTTP_403_FORBIDDEN)

    def retrieve(self, request,pk=None):
        try:
            userId= self.request.user.id
            purchase= PurchasedProduct.objects.get(pk=pk,user=userId)
            serializers = PurchasedProductSerializer(instance=purchase)
            return Response({
                    'data': serializers.data
                }, status=status.HTTP_200_OK) 
        except Exception as e:
            return Response({
                "ERROR": f" {e}!"
            }, status=status.HTTP_403_FORBIDDEN)

class PayOutView(ViewSet):

    def get_permissions(self):
        if self.action in ['list']:
            return [group_permission.IsSeller()]
        return super().get_permissions()

    def list(self, request):
        try: 
            sellerId= self.request.user.id
            purchase= PayOut.objects.filter(seller=sellerId)
            serializers = PayOutSerializer(instance=purchase,many=True)
            return Response({
                    'data': serializers.data
                }, status=status.HTTP_200_OK) 
            
        except Exception as e:
            traceback.print_exc()
            return Response({              
                "ERROR": f"Exception {e}!"
            }, status=status.HTTP_403_FORBIDDEN)