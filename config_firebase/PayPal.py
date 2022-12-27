import base64
import datetime 
import requests
class PayPal():
    
    clientID = 'AWqzcw6J08w4vvSDPteMeUgKaa9WZQnRWNLkO1YM9w7krr2ijZO0iRrTJdUDfh2cLWo-ZlnQzuUpq_cD'
    clientSecret = 'EJZ_rd9YoHiCNRE_qZ2-CTMhIFhJrScgAMiWWqB_MZKrFEF0_JcIiuVrB3Y1-980R5eK-DxVTyWv69kM'
    token =''    

    # Get token paypal
    def GetToken(self):
        url = "https://api.sandbox.paypal.com/v1/oauth2/token"
        data = {
                    "client_id": self.clientID,
                    "client_secret": self.clientSecret,
                    "grant_type":"client_credentials"
                }
        headers = {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Authorization": "Basic {0}".format(base64.b64encode((self.clientID
                    + ":" + self.clientSecret).encode()).decode())
                }

        token = requests.post(url, data, headers=headers)
        return token.json()['access_token']

    # Create a order to Paypal
    def CreateOrder(self,pay_in_id,money,user_id,currentSite): 
        token = self.GetToken()
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer '+ token,
        }
        jsonData = {
            "intent": "CAPTURE",
            "application_context": {
                # Return url when checkout successful
                "return_url": f"http://{currentSite}/tech/checkout-paypal/{pay_in_id}/succeeded/?user_id={user_id}",
                "cancel_url": f"http://{currentSite}/tech/checkout-paypal/{pay_in_id}/failed/", 
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
        response = requests.post('https://api-m.sandbox.paypal.com/v2/checkout/orders', 
            headers=headers, 
            json=jsonData
        )
        if response.status_code<400 :
            linkForPayment = response.json()['links'][1]['href']
            return linkForPayment
        else:
            return "ERROR"

            # Create a order to Paypal
    def PayOut(self,email,money): 
        # payOut= PayOut.objects.get(id=pay_out_id)
        token = self.GetToken()
        now = datetime.datetime.today()
        print(now)
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer '+ token,
        }
        jsonData = {
            "sender_batch_header": {
            "sender_batch_id": f"Payouts_{now}",
            "email_subject": "You have a payout!",
            "email_message": "You have received a payout! Thanks for using our service!"
            },
            "items": [
                {
                    "recipient_type": "EMAIL",
                    "amount": {
                        "value": f"{money}",
                        "currency": "USD"
                    },
                    "sender_item_id": f"{now}",
                    "receiver": f"{email}",
                    "notification_language": "vi-VN"
                }
            ]
        }
        response = requests.post(
            'https://api-m.sandbox.paypal.com/v1/payments/payouts',
            headers=headers, 
            json=jsonData
        )
        return response
        