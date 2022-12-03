
from datetime import date
from rest_framework.viewsets import ViewSet
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from order_payment.models import Order, OrderDetail, PayIn, PayOut, Payment
from order_payment.serializer import OrderDetailSerializer, OrderSerializer, PayInSerializer
from rest_framework import status
from rest_framework.decorators import action


class OrderViewSet(ViewSet):
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'create', 'destroy']:
            return [AllowAny(), ]
        return super().get_permissions()
    def list(self, request):
        queryset = Order.objects.all()
        serializer = OrderSerializer(queryset, many=True)
        return Response({'data': serializer.data}, status=status.HTTP_200_OK)
    def retrieve(self, request, pk=None):
        product = Order.objects.filter(pk=pk).get()
        serializer = OrderSerializer(product)
        return Response({'data': serializer.data}, status=status.HTTP_200_OK)
    def create(self, request):
        data_request = request.data
        serializer = OrderSerializer(data=data_request)
        if not serializer.is_valid():
            return Response({
                    'message':'Order is failed!',
                    'errors': serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer.save()
        return Response({
                'message':'Order is Success!',
                'data':serializer.data
            },
            status=status.HTTP_201_CREATED,
        )
    def destroy(self, request, pk=None):
        order = Order.objects.get(pk=pk)
        if order is None:
            return Response({
                'message':'Order do not Exists!',
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
        order.delete()
        return Response({
                'message':'Delete order is success',
            },
            status=status.HTTP_200_OK,
        )


class OrderDetailViewSet(ViewSet):
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny(), ]
        return super().get_permissions()

    def list(self, request):
        queryset = OrderDetail.objects.all()
        serializer = OrderDetailSerializer(queryset, many=True)
        return Response({'data': serializer.data}, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        product = OrderDetail.objects.filter(pk=pk).get()
        serializer = OrderDetailSerializer(product)
        return Response({'data': serializer.data}, status=status.HTTP_200_OK)


# ------------------------ Payment ------------------------
import base64
import requests
class PayPal():
    
    clientID = 'AWqzcw6J08w4vvSDPteMeUgKaa9WZQnRWNLkO1YM9w7krr2ijZO0iRrTJdUDfh2cLWo-ZlnQzuUpq_cD'
    clientSecret = 'EJZ_rd9YoHiCNRE_qZ2-CTMhIFhJrScgAMiWWqB_MZKrFEF0_JcIiuVrB3Y1-980R5eK-DxVTyWv69kM'
    token =''    

    # Get token paypal
    def PaypalToken(self):
        url = "https://api.sandbox.paypal.com/v1/oauth2/token"
        data = {
                    "client_id": self.clientID,
                    "client_secret": self.clientSecret,
                    "grant_type":"client_credentials"
                }
        headers = {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Authorization": "Basic {0}".format(base64.b64encode((self.clientID + ":" + self.clientSecret).encode()).decode())
                }

        token = requests.post(url, data, headers=headers)
        return token.json()['access_token']

    # Create a order to Paypal
    def CreateOrder(self,pay_in_id,money): 
        self.token = self.PaypalToken()
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer '+ self.token,
        }
        json_data = {
            "intent": "CAPTURE",
            "application_context": {
                # Return url when checkout successful
                "return_url": f"http://127.0.0.1:8000/tech/checkout-paypal/{pay_in_id}/succeeded?Authtoken={self.token}",
                "cancel_url": f"http://127.0.0.1:8000/tech/checkout-paypal/{pay_in_id}/failed", 
                "brand_name": "PBL6 Tech E",
                "shipping_preference": "NO_SHIPPING",
                "user_action": "CONTINUE"
            },
            "purchase_units": [
                {
                    "custom_id": "PBL5-Tech-E",
                    "amount": {
                        "currency_code": "USD",
                        "value": f"{money}" 
                    }
                }
            ]
        }
        response = requests.post('https://api-m.sandbox.paypal.com/v2/checkout/orders', headers=headers, json=json_data)
        linkForPayment = response.json()['links'][1]['href']
        return linkForPayment

def TransferMoneys(order):
    list_order_details = OrderDetail.objects.filter(order=order)
    # Get list of order details to transfer money for seller
    for order_detail in list_order_details:
        print(order_detail.seller)
        payOut = PayOut.objects.get(seller=order_detail.seller)
        payOut.current_balance += order_detail.total_price * 0.1        
        payOut.save()


class PayPalView(ViewSet):
    permission_classes = [AllowAny]

    # Customer successful paid
    @action(methods=['GET'],detail=True,permission_classes=[AllowAny],url_path="succeeded")
    def get_return_payment(self, request, pk=None):
        try:        
            # Post Paypal API to capture customer checkout
            Authtoken = request.query_params['Authtoken']
            order_id = request.query_params['token']
            captureurl = f'https://api.sandbox.paypal.com/v2/checkout/orders/{order_id}/capture'#see transaction status
            headers = {"Content-Type": "application/json", "Authorization": "Bearer "+Authtoken}
            response = requests.post(captureurl, headers=headers)

            payIn= PayIn.objects.get(pk=pk)
            Payment.objects.create(
                pay_in= payIn,
                money= payIn.number_money,
                )
            # Update status payment -> Payment successful
            payIn.status_payment =True
            payIn.received_time = date.today()
            payIn.save()
            
            # transfer money for seller
            TransferMoneys(payIn.order)
            return Response({'message':'Payment successful'}, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': 'Exception: {}'.format(e)}, status=status.HTTP_400_BAD_REQUEST)

    # customer cancels payment
    @action(methods=['GET'],detail=True,permission_classes=[AllowAny],url_path="failed")
    def get_cancel_payment(self, request, pk=None):
        try:
            payIn= PayIn.objects.get(pk=pk)
            payIn.status_payment =False
            payIn.save()
            return Response({'message': 'Checkout is cancel'}, status=status.HTTP_200_OK)
        except:
            return Response({'error': 'Pay In not exist'}, status=status.HTTP_400_BAD_REQUEST)

class PayInViewSet(ViewSet):
    permission_classes = [AllowAny]

    def list(self,request):
        payIn = PayIn.objects.all()
        ser= PayInSerializer(payIn,many=True)
        return Response(ser.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        payIn = PayIn.objects.get(pk=pk)
        serializer = PayInSerializer(payIn)
        return Response({'data': serializer.data}, status=status.HTTP_200_OK)

    def create(self, request):
        data= request.data
        serializer = PayInSerializer(data = data)

        if not serializer.is_valid():
            return Response({
                    'message':'Payment is failed!',
                    'errors': serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )       
        serializer.save()
        # print(serializer.data)
        if data.get('type_payment') == 'online':
            pay_in_id= serializer.data['id']
            money= serializer.data['number_money']          
            linkForPayment=PayPal().CreateOrder(pay_in_id, money)     
            return Response({'link_payment': linkForPayment}, status=status.HTTP_200_OK)
        return Response("oke", status=status.HTTP_200_OK)
        
 

