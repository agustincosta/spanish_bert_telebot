from fastapi import FastAPI
from pydantic import BaseModel
from transformers import pipeline
import time

#Instantiate api
app = FastAPI()

#Define request body class
class Message(BaseModel):
    name: str
    text: str

class Question(BaseModel):
    question: str
    context: str
    reset_context: bool

#Define QA response body class
class Answer(BaseModel):
    answer: str
    confidence: float

#Define classification response body class
class Classification(BaseModel):
    name: str
    text: str
    classification: str
    confidence: float

global_context = ""

#Use high level pipeline for sentiment analysis with BERT model trained on spanish
sentiment_analysis = pipeline("sentiment-analysis", model="pysentimiento/robertuito-sentiment-analysis")
question_answering = pipeline('question-answering', 
                            model='mrm8488/distill-bert-base-spanish-wwm-cased-finetuned-spa-squad2-es',
                            tokenizer=(
                                'mrm8488/distill-bert-base-spanish-wwm-cased-finetuned-spa-squad2-es',  
                                {"use_fast": False}
                            )
)

#Debugging endpoint
@app.post("/test/")
async def test_endpoint(msg: Message):
    msg = msg.model_dump()
    return msg

#Sentiment analysis endpoint
@app.post("/sent_analysis/", response_model=Classification)
async def analyze_sentiment(msg: Message):
    """Perform sentiment analysis on received message through POST request using pipeline

    Args:
        msg (Message): Message class with name of sender and text attributes

    Returns:
        Classification: Response incorporating predicted label and score to received message
    """
    
    start_time = time.perf_counter()

    #Perform sentiment analysis
    result = sentiment_analysis(msg.text)[0]

    end_time = time.perf_counter()      
    run_time = end_time - start_time
    print(f"Inference time for sentiment analysis {run_time}")    

    #Generate response object
    response_object = Classification(name=msg.name,
                                    text=msg.text,
                                    classification=result['label'],
                                    confidence=result['score'])
    return response_object

#Question answering endpoint
@app.post("/qa/", response_model=Answer)
async def answer_question(q: Question):
    """Answer question from received message through POST request using pipeline

    Args:
        msg (Message): Message class with name of sender and text attributes

    Returns:
        Answer: Response from the LLM
    """
    global global_context
    
    start_time = time.perf_counter()

    #Perform question answering
    if q.reset_context:
        qa ={"question":q.question, "context":q.context}
        global_context = q.context
    else:
        qa ={"question":q.question, "context":global_context}
    result = question_answering(qa)

    end_time = time.perf_counter()      
    run_time = end_time - start_time
    print(f"Inference time for question answering {run_time}")    

    #Generate response object
    response_object = Answer(answer=result['answer'], confidence=result['score'])

    return response_object