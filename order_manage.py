from fastapi.responses import JSONResponse
from database import DataBase
import re

db = DataBase()
orders_in_process = {}
default_dict = {item: 0 for item in db.get_menu()}


def create_response(items: dict) -> str:
    for _, quantity in items.items():
        if quantity > 0:
            return f"Your current order: " + \
                ", ".join([str(food_item) + ": " + str(int(quantity)) \
                for food_item, quantity in items.items() if quantity > 0]) + \
                ". Anything else? Or you can place your order by saying \"end of order\""
    return "Your order is empty. You can add something by saying: \"add\", " + \
           "e. g.: add one pasta"


def extract_session_id(output_contexts: list) -> str:
     context_name = output_contexts[0]['name']
     return re.search('sessions\/(.*?)\/contexts', context_name).group(1)


def add_to_order(parameters: dict, output_contexts: list) -> JSONResponse:
    food_items = parameters["food-items"]
    quantities = parameters["number"]
    session_id = extract_session_id(output_contexts)

    if len(food_items) != len(quantities):
        return JSONResponse(content={
            "fulfillmentText": "Sorry, I don't understand. " +
                               "Please, specify items and their quantities clearly, " +
                               "e. g.: Give me one soup and 2 salads"
        })
    food_dict = dict(zip(food_items, quantities))
    if session_id not in orders_in_process:
        orders_in_process[session_id] = default_dict

    for item, quantity in food_dict.items():
        orders_in_process[session_id][item] += quantity

    return JSONResponse(content={
        "fulfillmentText": create_response(orders_in_process[session_id])
    })


def remove_from_order(parameters: dict, output_contexts: list) -> JSONResponse:
    session_id = extract_session_id(output_contexts)
    try:
        food_items = parameters['food-items']
        for item in food_items:
            orders_in_process[session_id][item] = 0

        return JSONResponse(content={
            "fulfillmentText": create_response(orders_in_process[session_id])
        })

    except:
        return JSONResponse(content={
            "fulfillmentText": "Sorry, I didn't quite understand. " +
                               "You can remove items from your order by saying \"remove\", " +
                               "e. g.: remove salad and soup"
        })


def place_order(parameters: dict, output_contexts: list) -> JSONResponse:
    try:
        new_id = db.get_new_order_id()
        session_id = extract_session_id(output_contexts)
        for item, quantity in orders_in_process[session_id].items():
            if quantity > 0:
                db.add_to_orders(new_id, item, quantity)

        del orders_in_process[session_id]
        track_id = db.create_track_id(new_id)
        total_price = db.get_total_price(new_id)

        return JSONResponse(content={
            "fulfillmentText": f"Placed your order! Price: {total_price}, your tracking id: {track_id}"
        })

    except:
        return JSONResponse({
            "fulfillmentText": f"Sorry, something went wrong. Please, repeat your order"
        })
