from flask import Flask ,Response ,request,redirect,url_for,render_template ,jsonify
from pymongo import MongoClient
import json
from bson.objectid import ObjectId   # we can use the object id as text 

global i 

i=94

app = Flask(__name__)                # creating an instance of app aplication 



try:  ##connect to database 
    mongo = MongoClient("mongodb+srv://nassim:zamoum@nodetuts.i6qazqe.mongodb.net/sensors_db")
    db = mongo.sensors_db
    mongo.server_info()  # trigger exception if  we can not connect to db 

 
except : 
    print("error _cznt not connect ot db")

document_count = db.sensors.count_documents({})

print("docsss ",document_count)


####################################################" updating  
@app.route("/api/sensors/<id>",methods =["PATCH"])
def update_users(id):
    try : 
        h= request.json["humidity"]
        dbResponse = db.sensors.update_one({"_id": ObjectId(id)},
        {"$set": {"temp" :request.json["temp"],"humidity" :request.json["humidity"]  }}                          
                                         )
        return Response(
            response=json.dumps({"message":" user updated  successfully "}
             ), status=200,
            mimetype="application/json")    

    except Exception as ex :
        print(ex)
        return Response(
            response=json.dumps({"message":"cannot update"}
             ), status=500,
            mimetype="application/json")


####################################################" reading

#########################  creating ############################################### POSTINGGGG ###############################
@app.route("/api/sensors",methods=["POST"])
def create_user():
    global i 
   
    i+=1
    print("request from esp32 yooha")
    user={"id":request.json["id"],"temp":request.json["temp"] ,"humidity":request.json["humidity"] }
    dbResponse = db.sensors.insert_one(user)
    print(dbResponse.inserted_id)
        # for attr in dir(dbResponse):
            
        #     print(attr)
    data = list(db.buttons.find())
    data0 = data[0]
    relay_state = data0["state"]
    print("relaystate",relay_state)
    return Response(
            response=json.dumps({"relaystate": relay_state  }
             ), status=200,
                        mimetype="application/json")

            
########################################################################################################################    
    

@app.route("/home",methods=["GET"])
def home():
    return render_template('main.html')



@app.route("/DASHBOARD.html",methods=["GET"])
def homee():
    return render_template('DASHBOARD.html')


@app.route("/myfarm.html",methods=["GET"])
def myfarm():
    global i 
    document_count = db.sensors.count_documents({})
    data = list(db.sensors.find())
    first_document = data[document_count-1]
    temp = first_document['temp']
    humidity = first_document['humidity']
    
    t = temp if temp is not None else 0.0
    t = "{:.2f}".format(t)
    h = humidity if humidity is not None else 0.0
    h = "{:.2f}".format(h)
    
    print("i====",document_count)
    
    return render_template('myfarm.html',t=t,h=h)




@app.route('/submit', methods=['POST'])
def submit():
    user_input = request.json.get('userInput')
    pass_input = request.json.get('passinput')
    print(user_input)
    print(pass_input)
    # Insert data into MongoDB
    user_data = {
        'username': user_input,
        'password': pass_input
    }
    result = db.users.insert_one(user_data)
    
    return jsonify({'status': 'success', 'data': str(result.inserted_id)})





@app.route('/login', methods=['POST'])
def login():
    user_input = request.json.get('userInput')
    pass_input = request.json.get('passinput')

    # Find the user in the database
    user = db.users.find_one({'username': user_input})

    if user:
        # Compare passwords
        if user['password'] == pass_input:
            print("seuccess")
            return jsonify({'status': 'success', 'message': 'Login successful'})
            
        else:
            print("invalidpass")
            return jsonify({'status': 'error', 'message': 'Invalid password'})
            
    else:
        return jsonify({'status': 'error', 'message': 'User not found'})


@app.route("/relay_button",methods=['POST'])
def relay():
    state = request.json.get('state')
    print("statee=====",state)
    # Insert data into MongoDB
    user_data = {
        'button': "relay",
        'state': state
    }
    result = db.buttons.update_one({"_id": ObjectId("669045dce0c2baf7ff64caff")},
        {"$set": {"state" :state }}                          
                                         )
    
    return jsonify({'status': 'success', 'data': str(result)})   
   


####################################################
if __name__ == "__main__" :
    app.run(host='0.0.0.0' ,port=5555,debug=True)               # you choose any port you want above  65535