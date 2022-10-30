from  flask import Flask ,render_template,url_for,redirect,request,flash
import numpy as np
import pyrebase
import pickle
import sys

import datetime
import json
import requests

config ={
    "apiKey": "AIzaSyAy_-B05G2AYFrOi0FUQAMHrbew7zThnc8",
    "authDomain": "food-chain1.firebaseapp.com",
    "databaseURL": "https://food-chain1-default-rtdb.firebaseio.com",
    "projectId": "food-chain1",
    "storageBucket": "food-chain1.appspot.com",
    "messagingSenderId": "465892674183",
    "appId": "1:465892674183:web:9340d2c92f2b8d50f08622",
    "measurementId": "G-HSSJE3JW49"
}

firebase= pyrebase.initialize_app(config)

db=firebase.database()
##db.child("message to r from wh").push({"msg":"have u recived??"})
##for x in ok:
##    print(ok[x]["msg"])

# Alternate node which hosts the blockchain server.
# Multiple nodes possible
CONNECTED_NODE_ADDRESS = "http://127.0.0.1:8000"

posts = []

app = Flask(__name__)

model=pickle.load(open("gradientboostmodel.pkl","rb"))

@app.route('/',methods=['POST','GET'])
def home():
    return render_template('landing.html')

@app.route("/login",methods=['POST'])
def login():
    data=request.form
    if(data['username'].upper() == 'SUPPLIER' and data['password'] == '12345'):
        return redirect(url_for('Supplier'))
    elif(data['username'].upper() == 'RESTAURANT' and data['password'] == '12345'):
        return redirect(url_for('Restaurant'))
    elif(data['username'].upper() == 'WAREHOUSE' and data['password'] == '12345'):
        return redirect(url_for('Warehouse'))
    else:
        return redirect(url_for('home'))

@app.route("/Supplier")
def Supplier():
    ok1=db.child("message to wh from s").get()
    ok1=ok1.val()
    ok2=db.child("message to s from wh").get()
    ok2=ok2.val()
    return render_template('Supplier.html',info1=ok1, info2=ok2)


@app.route("/Warehouse")
def Warehouse():
    ok1=db.child("message to s from wh").get()
    ok1=ok1.val()
    ok2=db.child("message to r from wh").get()
    ok2=ok2.val()
    ok3=db.child("message to wh from r").get()
    ok3=ok3.val()
    ok4=db.child("message to wh from s").get()
    ok4=ok4.val()
    return render_template('Warehouse.html', info1=ok1, info2=ok2, info3=ok3, info4=ok4)


@app.route("/Restaurant")
def Restaurant():
    ok1=db.child("message to wh from r").get()
    ok1=ok1.val()
    ok2=db.child("message to r from wh").get()
    ok2=ok2.val()
    return render_template('Restaurant.html',info1=ok1, info2=ok2)


##message to warehouse from supplier
@app.route("/msgtowhfs",methods=['POST'])
def msgtowhfs():
    data=request.form
    db.child("message to wh from s").push({"msg":data["mtwfs"]})
    return redirect(url_for('Supplier'))


##message to supplier from warehouse
@app.route("/msgtosfwh",methods=['POST'])
def msgtosfwh():
    data=request.form
    db.child("message to s from wh").push({"msg":data["mtsfw"]})
    return redirect(url_for('Warehouse'))


##message to restaurant from warehouse
@app.route("/msgtorfwh",methods=['POST'])
def msgtorfwh():
    data=request.form
    db.child("message to r from wh").push({"msg":data["mtrfw"]})
    return redirect(url_for('Warehouse'))


##message to warehouse fron restaurant
@app.route("/msgtowhfr",methods=['POST'])
def msgtowhfr():
    data=request.form
    db.child("message to wh from r").push({"msg":data["mtwfr"]})
    return redirect(url_for('Restaurant'))






@app.route("/predict",methods=['GET','POST'])
def predict():
    if request.method == "POST":
        category=request.form.get('category')
        if category=='Beverages':
            category_val=0
        elif category=="Extras":
            category_val=3
        elif category == "Soup":
            category_val = 12
        elif category == "Other Snacks":
            category_val = 5
        elif category == "Salad":
            category_val = 9
        elif category == "Rice Bowl":
            category_val = 8
        elif category == "Starters":
            category_val = 13
        elif category == "Sandwich":
            category_val = 10
        elif category == "Pasta":
            category_val = 6
        elif category == "Desert":
            category_val = 2
        elif category == "Biryani":
            category_val = 1
        elif category == "Pizza":
            category_val = 7
        elif category == "Fish":
            category_val = 4
        else:
            category_val=11

        cuisine=request.form.get('cuisine')
        if cuisine=='Thai':
            cuisine_val=3
        elif cuisine == 'Indian':
             cuisine_val=1
        elif cuisine =='Italian':
            cuisine_val=2
        else:
            cuisine_val=0
        week=request.form.get('weeks')
        checkout_price=request.form.get('checkout price')
        base_price = request.form.get('base price')
        em=request.form.get('Email Promotion')
        if em=='yes':
            email_promo=1
        else:
            email_promo=0
        hp=request.form.get('Homepage Featured')
        if hp=='yes':
            hp_featured=1
        else:
            hp_featured=0

        city_code=request.form.get("City Code")
        region_code=request.form.get("Region Code")
        op_area=request.form.get("Operational Area")
        ct=request.form.get('Operational Area')
        if ct=="TYPE_A":
            ct_val=0
        elif ct=="TYPE_B":
            ct_val=1
        else:
            ct_val=2
        list = [
            category_val,
            cuisine_val,
            week,
            checkout_price,
            base_price,
            email_promo,
            hp_featured,
            city_code,
            region_code,
            op_area,
            ct_val]

        print(category_val,
              cuisine_val,
              week,
              checkout_price,
              base_price,
              email_promo,
              hp_featured,
              city_code,
              region_code,
              op_area,
              ct_val)



        data = np.array([list])
        output = model.predict(data)
        output = int(output)
        return render_template('predict.html', prediction_text="Approximate Orders for "+ week+ " weeks. {}".format(output))
    return render_template('predict.html')




#blockchain routes+ API

def fetch_posts():
    """
    Function to fetch the chain from a blockchain node, parse the
    data and store it locally.
    """
    get_chain_address = "{}/chain".format(CONNECTED_NODE_ADDRESS)
    response = requests.get(get_chain_address)
    if response.status_code == 200:
        content = []
        chain = json.loads(response.content)
        for block in chain["chain"]:
            for tx in block["transactions"]:
                tx["index"] = block["index"]
                tx["hash"] = block["previous_hash"]
                content.append(tx)

        global posts
        posts = sorted(content, key=lambda k: k['timestamp'],
                       reverse=True)

@app.route('/find_my_food')
def index():
    fetch_posts()
    return render_template('index.html',
                           title='Find My Food ',
                           posts=posts,
                           node_address=CONNECTED_NODE_ADDRESS,
                           readable_time=timestamp_to_string)


@app.route('/submit', methods=['POST'])
def submit_textarea():
    """
    Endpoint to create a new transaction via our application.
    """
    post_content = request.form["content"]
    author = request.form["author"]

    post_object = {
        'author': author,
        'content': post_content,
    }

    # Submit a transaction
    new_tx_address = "{}/new_transaction".format(CONNECTED_NODE_ADDRESS)

    requests.post(new_tx_address,
                  json=post_object,
                  headers={'Content-type': 'application/json'})

    return redirect('/find_my_food')


def timestamp_to_string(epoch_time):
    return datetime.datetime.fromtimestamp(epoch_time).strftime('%H:%M')

if __name__=="__main__":
    app.run(port=5000)