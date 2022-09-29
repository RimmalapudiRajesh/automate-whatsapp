
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from pymongo import MongoClient
from datetime import datetime
cluster = MongoClient("mongodb+srv://raghu:raghu@cluster0.guea2.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")

db = cluster["Restaurant"]
users = db["users"]
orders = db["orders"]

app = Flask(__name__)
@app.route("/", methods=["get", "post"])
def reply():
    bill = 0
    text = request.form.get("Body")
    number = request.form.get("From")
    number = number.replace("whatsapp:", "")
    res = MessagingResponse()
    user = users.find_one({"number": number})
    if bool(user) == False:
        msg = res.message("Hi, thanks for contacting ********* Restaurant.\nYou can choose from one of the options below: "
                          "\n\nType\n\n 1️⃣ To contact us \n 2️⃣ To order food \n 3️⃣ To know our working hours \n 4️⃣"
                          "To get our address")
        users.insert_one({"number": number, "status": "main", "messages": [],"bill":0})
    elif user["status"] == "main":
        try:
            option = int(text)
        except:
            res.message("Please enter a valid response")
            return str(res)

        if option == 1:
            res.message("You can contact us through phone or e-mail.\n\nPhone: ********* \n E-mail :***####@gmail.com")
        elif option == 2:
            res.message("You have entered ordering mode.")
            users.update_one({"number": number}, {"$set": {"status": "ordering" ""}})
            res.message("You can select one of the following food to order: \n\n1️⃣ Veg Biryani (100/-)   \n2️⃣ Chicken Biryani (200/-) \n3️⃣ Chicken Spec.Biryani (220/-)"
                "\n4️⃣ Mutton Biryani (300/-) \n5️⃣ Chicken Wings (200/-) \n6️⃣ Paneer Biryani (200/-) \n7️⃣ Chicken Curry (150/-) \n8️⃣ Mutton Curry (200/-) \n9️⃣ Leg pieces (150/-)  \n0️⃣ Go Back")
        elif option == 3:
            res.message("We work from 9 a.m. to 5 p.m.")

        elif option == 4:
            res.message("Here we mention the Restaurant Address")
        else:
            res.message("Please enter a valid response")
    elif user["status"] == "ordering":
        try:
            option = str(text)
        except:
            res.message("Please enter a valid response")
            return str(res)
        if option == '0':
            users.update_one({"number": number}, {"$set": {"status": "main"}})
            res.message("You can choose from one of the options below: "
                        "\n\nType\n\n 1️⃣ To contact us \n 2️⃣ To order food \n 3️⃣ To know our working hours \n 4️⃣ "
                        "To get our address")
        elif option!="Hi":
            x=""
            bill=0
            for i in option:
                if '1' <= i <= '9':
                    food = ["Veg Biryani (100/-)", "Chicken Biryani (200/-)", "Chicken Spec.Biryani (220/-)",
                            "Mutton Biryani (300/-)", "Chicken Wings (200/-)", "Paneer Biryani (200/-)",
                        "Chicken Curry (150/-)", "Mutton Curry (250/-)", "Leg piece (150/-)"]
                    selected = food[int(i) - 1]
                    x+=selected+"\n"
                    bill+=int(selected[-6:-3])
            users.update_one({"number": number}, {"$set": {"status": "address"}})
            users.update_one({"number": number}, {"$set": {"item": x}})
            users.update_one({"number": number}, {"$set": {"bill": bill}})
            res.message("Excellent choice 😉")
            res.message("Please enter your address to confirm the order")
        else:
            res.message("Please enter a valid response")

    elif user["status"] == "address":
        x = user["item"]
        bill=user["bill"]
        res.message(f"Your order for \n{x}Total bill amount is {bill}\n")
        orders.insert_one({"number": number, "item": x, "bill": bill , "address": text, "order_time": datetime.now()})
        users.update_one({"number":number},{"$set":{"status":"payment"}})
        res.message("Select the payment mode\n1️⃣Online Payment\n2️⃣Offline Payment\n")
    elif user["status"]=="payment":
        if text == "2":
            res.message("Thanks for shopping with us 😊")
            res.message("Your order is delivered within the few hours")
        elif text == "1":
            res.message("******* Payment-Link ******")
            res.message("Please send a payment for this above link")
            res.message("Thanks for shopping with us 😊")
            res.message("After your online payment your order is delivered within the few hours")
        else:
            res.message("Please enter a valid response")
        users.update_one({"number": number}, {"$set": {"status": "ordered"}})
    elif user["status"] == "ordered":
        res.message("Hi, thanks for contacting again.\nYou can choose from one of the options below: "
                    "\n\nType\n\n 1️⃣ To contact us \n 2️⃣ To order food \n 3️⃣ To know our working hours \n 4️⃣ "
                    "To get our address")

        users.update_one({"number": number}, {"$set": {"status": "main"}})
    users.update_one({"number": number}, {"$push": {"messages": {"text": text, "date": datetime.now()}}})
    return str(res)


if __name__ == "__main__":
    app.run()

