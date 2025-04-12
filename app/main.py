import json
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from chains import generate_uml_diagram, check_actors, extract_uml_info, Chain, generate_uml_diagram_plantuml
from pydantic import BaseModel

# Initialize Chain object
chain = Chain()
llm = chain.llm #get the llm object from the chain.

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "webhook connected"}


# Store session state
session_data = {}

# Pydantic model for Dialogflow request
class DialogflowRequest(BaseModel):
    queryResult: dict

print("Today we are going to learn about UML Diagrams with your Use Cae are you ready?")
@app.post("/webhook")
async def webhook(request: Request, dialogflow_request: DialogflowRequest):
    try:
        req = dialogflow_request.dict()
        intent_name = req["queryResult"]["intent"]["displayName"]

        if intent_name == "System_purpose":
            return handle_system(req)
        elif intent_name == "Identify_actions":
            return handle_system(req)
        else:
            return {"fulfillmentText": "I am not sure what you meant."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def handle_system(req: dict):
    try:
        user_input = req["queryResult"]["queryText"]
        llm_response = extract_uml_info(llm, user_input)
        diagram_path = generate_uml_diagram_plantuml(llm_response)
        image_url = f"https://your-server-domain/{diagram_path}"

        return {
            "fulfillmentMessages": [
                {
                    "text": {"text": ["Here is the UML diagram:"]}
                },
                {"image": {"imageUri": image_url}},
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
