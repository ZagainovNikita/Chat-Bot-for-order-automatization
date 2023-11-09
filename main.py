from fastapi import FastAPI, Request
from tracking import track_order
from order_manage import add_to_order, remove_from_order, place_order

app = FastAPI()
intent_handler_dict = {
    "track.order - context: ongoing-tracking": track_order,
    "order.add - context: ongoing-order": add_to_order,
    "order.remove - context: ongoing-order": remove_from_order,
    "order.finish - context: ongoing-order": place_order,
}


@app.post("/")
async def handle_request(request: Request):
    payload = await request.json()
    intent = payload['queryResult']['intent']['displayName']
    parameters = payload['queryResult']['parameters']
    output_contexts = payload['queryResult']['outputContexts']

    return intent_handler_dict[intent](parameters, output_contexts)
