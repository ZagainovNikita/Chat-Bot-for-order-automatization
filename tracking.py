from fastapi.responses import JSONResponse
from database import DataBase

db = DataBase()


def track_order(parameters: dict, output_contexts: list) -> JSONResponse:
    try:
        if len(parameters["number"]) != 1:
            return JSONResponse(content={
                "fulfillmentText":
                    "Please, enter one number representing your order id. e. g.: #12345"
            })

        order_status = db.get_order_status(parameters["number"][0])
        if not order_status:
            return JSONResponse(content={
                "fulfillmentText":
                    "Sorry, your this number does not exist"
            })

        return JSONResponse(content={
            "fulfillmentText": f"Your order status: {order_status[0]}"
        })

    except:
        return JSONResponse(content={
            "fulfillmentText":
                "Please, enter one number representing your order id. e. g.: #12345"
        })
