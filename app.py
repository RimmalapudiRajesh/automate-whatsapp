from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from pymongo import MongoClient
from datetime import datetime

cluster = MongoClient(
    "mongodb+srv://raghu:raghu@cluster0.guea2.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")

db = cluster["Restaurant"]
users = db["users"]
orders = db["orders"]

app = Flask(__name__)


@app.route("/", methods=["get", "post"])
def reply():
    text = request.form.get("Body")
    number = request.form.get("From")
    number = number.replace("whatsapp:", "")
    res = MessagingResponse()
    user = users.find_one({"number": number})
    if bool(user) == False:
        msg = res.message("Hi, thanks for contacting Rajesh Restaurant.\nYou can choose from one of the options below: "
                          "\n\nType\n\n 1️⃣ To contact us \n 2️⃣ To order food \n 3️⃣ To know our working hours \n 4️⃣"
                          "To get our address")
        users.insert_one({"number": number, "status": "main", "messages": []})
    elif user["status"] == "main":
        try:
            option = int(text)
        except:
            res.message("Please enter a valid response")
            return str(res)

        if option == 1:
            res.message(
                "You can contact us through phone or e-mail.\n\nPhone: ********* \n E-mail :***####@gmail.com")
        elif option == 2:
            res.message("You have entered ordering mode.")
            users.update_one(
                {"number": number}, {"$set": {"status": "ordering" ""}})
            res.message(
                "You can select one of the following food to order: \n\n1️⃣ Veg Biryani (100/-)   \n2️⃣ Chicken Biryani (200/-) \n3️⃣ Chicken Spec.Biryani (220/-)"
                "\n4️⃣ Mutton Biryani (300/-) \n5️⃣ Chicken Wings (200/-) \n6️⃣ Paneer Biryani (200/-) \n7️⃣ Chicken Curry (150/-) \n8️⃣ Mutton Curry (200/-) \n9️⃣ Leg pieces (150/-)  \n0️⃣ Go Back")
        elif option == 3:
            res.message("We work from 9 a.m. to 5 p.m.")

        elif option == 4:
            res.message("Here we mention the Restaurant Address")
        else:
            res.message("Please enter a valid response")
    elif user["status"] == "ordering":
        try:
            option = int(text)
        except:
            res.message("Please enter a valid response")
            return str(res)
        if option == 0:
            users.update_one(
                {"number": number}, {"$set": {"status": "main"}})
            res.message("You can choose from one of the options below: "
                        "\n\nType\n\n 1️⃣ To contact us \n 2️⃣ To order food \n 3️⃣ To know our working hours \n 4️⃣ "
                        "To get our address")
        elif 1 <= option <= 9:
            food = ["Veg Biryani (100/-)", "Chicken Biryani (200/-)", "Chicken Spec.Biryani (220/-)",
                     "Mutton Biryani (300/-)", "Chicken Wings (200/-)", "Paneer Biryani (200/-)", "Chicken Curry (150/-)", "Mutton Curry (250/-)", "Leg piece (150/-)"]
            selected = food[option - 1]
            users.update_one({"number": number}, {"$set": {"status": "address"}})
            users.update_one({"number": number}, {"$set": {"item": selected}})
            res.message("Excellent choice 😉")
            res.message("Please enter your address to confirm the order")    
        else:
            res.message("Please enter a valid response")
    elif user["status"] == "address":
        selected = user["item"]
        res.message("Thanks for shopping with us 😊")
        res.message(f"Your order for {selected} has been received and will be delivered within an hour")
        
        orders.insert_one({"number": number, "item": selected, "address": text, "order_time": datetime.now()})
        users.update_one(
            {"number": number}, {"$set": {"status": "ordered"}})


    elif user["status"] == "ordered":
        res.message("Hi, thanks for contacting again.\nYou can choose from one of the options below: "
                    "\n\nType\n\n 1️⃣ To contact us \n 2️⃣ To order food \n 3️⃣ To know our working hours \n 4️⃣ "
                    "To get our address")

        users.update_one({"number": number}, {"$set": {"status": "main"}})
    users.update_one({"number": number}, {"$push": {"messages": {"text": text, "date": datetime.now()}}})
    return str(res)


if __name__ == "__main__":
    app.run()
