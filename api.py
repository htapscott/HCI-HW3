import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="HCI Mini Review App API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

questions = [{
                "id": 0,
                "q": "Is Fitts' Law an example of a predictive model or a descriptive model?",
                "a": "Predictive model"
                },
             {
                "id": 1,
                "q": "Does this course focus more on genius design, systems design, or user-centered design?",
                "a": "User-centered design"
                },
             {
                "id": 2,
                "q": "What is the main goal of the ideation phase of iterative design?",
                "a": "Generating as many possible design solutions as possible"
                }
            ]

class QuestionRequest(BaseModel):
    question: str
    answer: str

@app.get("/questions")
def get_questions():
    return questions

@app.post("/add")
def add_question(req: QuestionRequest):
    questions.append({ 
        "id": max((q["id"] for q in questions), default=-1) + 1, #added to prevent duplicare IDs when adding questions after deleting
        "q": req.question,
        "a": req.answer
    })

# TODO: Add a new route that can be used to delete a question/answer from the dataset. DONE
@app.delete("/delete/{id}")
def delete_question(id: int):
    for question in questions:
        if question["id"] == id:
            questions.remove(question)
            return {"message": f"Question with ID {id} deleted"}

    raise HTTPException(
        status_code=404,
        detail=f"Question with ID {id} not found"
    )
# TODO: Add a new route that can be used to update a question/answer within the dataset. DONE
@app.put("/update/{id}")
def update_question(id: int, req: QuestionRequest):
    for question in questions:
        if question["id"] == id:
            question["q"] = req.question
            question["a"] = req.answer
            return question

    raise HTTPException(
        status_code=404,
        detail=f"Question with ID {id} not found"
    )
if __name__ == "__main__":
    uvicorn.run(app, port=8005)