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
    user={"id":request.json["id"],"temp":request.json["temp"] ,"humidity":request.json["humidity"] , "level":request.json["level"] 
           , "light_val":request.json["light"], "tds": request.json["tds"] , "ph": request.json["ph"] ,"left": request.json["left"]  }
    dbResponse = db.sensors.insert_one(user)
    print(dbResponse.inserted_id)
        # for attr in dir(dbResponse):
            
        #     print(attr)

    data = list(db.buttons.find())
    data0 = data[0]
    relay_state = data0["state"]

    timer = list(db.time.find())
    time0 = timer[0]
    time = time0["time"]

    ph = list(db.thresh.find())
    ph1 = ph[0]
    low = ph1["lowph"]
    high = ph1["highph"]

    t = list(db.t_thresh.find())
    t1 = t[0]
    t2 = t1["t_thresh"]

    print("time",time)
    return Response(
            response=json.dumps({"timer": time  , "low" :low , "high" : high , "state" : relay_state , "t_thresh" : t2}
             ), status=200,
                        mimetype="application/json")

            
########################################################################################################################    
    

@app.route("/home",methods=["GET"])
def home():
    return render_template('main.html')



@app.route("/DASHBOARD.html",methods=["GET"])
def homee():
    return render_template('DASHBOARD.html')

@app.route("/control.html",methods=["GET"])
def control():
    global i 
    global timme 
    document_count = db.sensors.count_documents({})
    data = list(db.sensors.find())
    first_document = data[document_count-1]
   
    left = first_document['left']
    
    leftt = left if left is not None else 0.0
    leftt = "{:.2f}".format(left)
    print("left time ",left)

    leftt_float = float(leftt)
    val = leftt_float - int(leftt_float)
    val2 = val * 60 
    
    v = val2 if val2 is not None else 0.0
    if v >= 0 : 
        v = "{:.2f}".format(val2)
    else : 
        v= 0 

    leftt = int(leftt_float)
    return render_template('control.html',leftt=leftt,v=v)



@app.route("/myfarm.html",methods=["GET"])
def myfarm():
    global i 
    global timme 
    document_count = db.sensors.count_documents({})
    data = list(db.sensors.find())
    first_document = data[document_count-1]
    temp = first_document['temp']
    humidity = first_document['humidity']
    level = first_document['level']
    light_val = first_document['light_val']
    tdsval = first_document['tds']
    ph_val = first_document['ph']
    left = first_document['left']
    t = temp if temp is not None else 0.0
    t = "{:.2f}".format(t)
    h = humidity if humidity is not None else 0.0
    h = "{:.2f}".format(h)
    l = level if level is not None else 0.0
    l = "{:.2f}".format(l) 
    l= float(l)/150*100
    l= 100 -int(l) 
    if l < 0 :
        l= 0 
    if l > 100 : 
        l=100 
    liv = light_val if light_val is not None else 0.0
    liv = "{:.2f}".format(liv)
    tds = tdsval if tdsval is not None else 0.0
    tds = "{:.2f}".format(tdsval)
    ph = ph_val if ph_val is not None else 0.0
    ph = "{:.2f}".format(ph_val)
    leftt = left if left is not None else 0.0
    leftt = "{:.2f}".format(left)
    print("left time ",left)

    leftt_float = float(leftt)
    val = leftt_float - int(leftt_float)
    val2 = val * 60 
    
    v = val2 if val2 is not None else 0.0
    if v >= 0 : 
        v = "{:.2f}".format(val2)
    else : 
        v= 0 

    leftt = int(leftt_float)

    thresh_data = db.thresh.find_one()
    thresh_tds = float(thresh_data.get('tds', 0.0)) if thresh_data and thresh_data.get('tds') else 0.0

   

    
    
    return render_template('myfarm.html',t=t,h=h,l=l,liv=liv,tds=tds,ph=ph,leftt=leftt,v=v,thresh_tds=thresh_tds)




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

@app.route("/temp_thresh",methods=['POST'])
def t_thresh():
    t = request.json.get('t_thresh')
    print("thresh",t)
    # Insert data into MongoDB
    user_data = {
        't_thresh': t
        
    }
    result = db.t_thresh.update_one({"_id": ObjectId("66a5172007e45970c09d69e0")},
        {"$set": {"t_thresh" :t }}                          
                                         )
    
    return jsonify({'status': 'success', 'data': str(result)})   

@app.route("/time",methods=['POST'])
def time():
    global timme 
    timme = request.json.get('time')
    print("time=====",timme)
    # Insert data into MongoDB
    user_data = {
        'time': timme
    }
    result = db.time.update_one({"_id": ObjectId("669e5249f7f0c9e9b4c47ef2")},
        {"$set": {"time" :timme }}                          
                                         )
    
    return jsonify({'status': 'success', 'data': str(result)})  
   


@app.route('/GiveThresh', methods=['POST'])
def thresh():
    print("GiveThresh")
    
    lowph  = request.json.get('lowph')
    highph  = request.json.get('highph')

    # Insert data into MongoDB
    user_data = {
        
        'lowph': lowph ,
        'highph':  15 
    }
    result = db.thresh.update_one({"_id": ObjectId("669ef0232911e36d89c51f0f")},
        {"$set": {"lowph":lowph , "highph":highph  }})
    
    
    return jsonify({'status': 'success', 'data': str(result.inserted_id)})


@app.route('/GiveThresh1', methods=['POST'])
def thresh1():
    print("GiveThresh")
    tds = request.json.get('tds')
   

    # Insert data into MongoDB
    user_data = {
        'tds': tds,
       
    }
    result = db.thresh.update_one({"_id": ObjectId("669ef0232911e36d89c51f0f")},
        {"$set": {"tds" :tds  }})
    
    
    return jsonify({'status': 'success', 'data': str(result.inserted_id)})


####################################################
if __name__ == "__main__" :
    app.run(host='0.0.0.0' ,port=5555,debug=True)               # you choose any port you want above  65535