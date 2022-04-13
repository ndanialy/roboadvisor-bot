### Required Libraries ###
from datetime import datetime
from dateutil.relativedelta import relativedelta

### Functionality Helper Functions ###
def parse_int(n):
    """
    Securely converts a non-integer value to integer.
    """
    try:
        return int(n)
    except ValueError:
        return float("nan")


def build_validation_result(is_valid, violated_slot, message_content):
    """
    Define a result message structured as Lex response.
    """
    if message_content is None:
        return {"isValid": is_valid, "violatedSlot": violated_slot}

    return {
        "isValid": is_valid,
        "violatedSlot": violated_slot,
        "message": {"contentType": "PlainText", "content": message_content},
    }


### Dialog Actions Helper Functions ###
def get_slots(intent_request):
    """
    Fetch all the slots and their values from the current intent.
    """
    return intent_request["currentIntent"]["slots"]


def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    """
    Defines an elicit slot type response.
    """

    return {
        "sessionAttributes": session_attributes,
        "dialogAction": {
            "type": "ElicitSlot",
            "intentName": intent_name,
            "slots": slots,
            "slotToElicit": slot_to_elicit,
            "message": message,
        },
    }


def delegate(session_attributes, slots):
    """
    Defines a delegate slot type response.
    """

    return {
        "sessionAttributes": session_attributes,
        "dialogAction": {"type": "Delegate", "slots": slots},
    }


def close(session_attributes, fulfillment_state, message):
    """
    Defines a close slot type response.
    """

    response = {
        "sessionAttributes": session_attributes,
        "dialogAction": {
            "type": "Close",
            "fulfillmentState": fulfillment_state,
            "message": message,
        },
    }

    return response

def validate_data(age, investment_amount):
    if 0 > parse_int(age) or parse_int(age) > 65:
        return build_validation_result(
            False,
            "age",
            "You need to be between 0 and 65 years of age to use this service."
        )

    #Validating the dollar amound
    if parse_int(investment_amount) < 5000:
        return build_validation_result(
            False,
            "investmentAmount",
            "The minimum valid investment is $5000."
            )
    #If both results are valid
    return build_validation_result(True, None, None)

#Defining the different risk tolerances and the replies 
def recommend(risk_level):
    tolerance = {
        "none" : "100% bonds (AGG), 0% equities (SPY)",
        "low" : "60% bonds (AGG), 40% equities (SPY)",
        "medium" : "40% bonds (AGG), 60% equities (SPY)",
        "high" : "20% bonds (AGG), 80% equities (SPY)"
    }
    return tolerance[risk_level]
    
### Intents Handlers ###
def recommend_portfolio(intent_request):
    """
    Performs dialog management and fulfillment for recommending a portfolio.
    """

    first_name = get_slots(intent_request)["firstName"]
    age = get_slots(intent_request)["age"]
    investment_amount = get_slots(intent_request)["investmentAmount"]
    risk_level = get_slots(intent_request)["riskLevel"]
    source = intent_request["invocationSource"]

    # Pulls the invocation source.
    source = intent_request["invocationSource"]
    
    if source == "DialogCodeHook":
        #Getting the slots
        slots = get_slots(intent_request)
        
        validation_result = validate_data(age,investment_amount)
      
        if not validation_result["isValid"]:
            slots[validation_result["violatedSlot"]]=None
            
            #returns elicit slot
            return elicit_slot(
                intent_request["sessionAttributes"],
                intent_request["currentIntent"]["name"],
                slots,
                validation_result["violatedSlot"],
                validation_result["message"],
                )
                
        output_session_attributes = intent_request["sessionAttributes"]
        
        return delegate(output_session_attributes, get_slots(intent_request))
    
    portfolio_composition = recommend(risk_level)
    
    return close(
        intent_request["sessionAttributes"],
        "Fulfilled",
        {
            "contentType": "PlainText",
            "content": """Thank you for using our serivce (),
            according to your investment amount and risk tolerance, you would like to invest {} ; based on this data, our recommendation is {}
            """.format(
                first_name, investment_amount, portfolio_composition
            ),
        },
    )     


### Intents Dispatcher ###
def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    intent_name = intent_request["currentIntent"]["name"]

    # Dispatch to bot's intent handlers
    if intent_name == "recommendPortfolio":
        return recommend_portfolio(intent_request)

    raise Exception("Intent with name " + intent_name + " not supported")


### Main Handler ###
def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """

    return dispatch(event)

