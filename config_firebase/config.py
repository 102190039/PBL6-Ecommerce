
import pyrebase

config = {
    "apiKey": "AIzaSyCyxuo8QjPpaD6YAYYCRBtXbTWrwpmjZxI",
    "authDomain": "storeimg-50091.firebaseapp.com",
    "projectId": "storeimg-50091",
    "storageBucket": "storeimg-50091.appspot.com",
    "messagingSenderId": "290248241547",
    "appId": "1:290248241547:web:2d1e1d208816018847bf8e",
    "measurementId": "G-VZB81E2FTF",
    "databaseURL": ""
}

# khởi tạo kết nối firebase storage
firebase = pyrebase.initialize_app(config)
storage = firebase.storage()