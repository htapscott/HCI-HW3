from nicegui import ui
import requests

API_URL = "http://localhost:8005"

questions = []
ui.query("body").style("background-color: #f1f5f9;") # 

page_body = ui.column().classes(
    "w-full max-w-3xl mx-auto p-6 gap-6"
)

def api_get(path):
    try:
        # Attempt to send GET request to API
        response = requests.get(f"{API_URL}{path}", timeout=5)
        # If we get an error code back, raise an exception
        response.raise_for_status()
        # Otherwise, GET was successful so return response data
        return response.json()
    except requests.RequestException as e:
        # GET request was unsuccessful
        # Send an alert with error details to the UI and return empty list
        ui.notify(f"Could not reach API: {e}", type="negative")
        return []

def api_post(path, data):
    try:
        # Attempt to send POST request to API with data payload
        response = requests.post(f"{API_URL}{path}", json=data, timeout=5)
        # If we get an error code back, raise an exception
        response.raise_for_status()
        # Otherwise, POST was successful so return True
        return True
    except requests.RequestException as e:
        # POST request was unsuccessful
        # Send an alert with error details to the UI and return False
        ui.notify(f"Could not reach API: {e}", type="negative")
        return False

# TODO: Create api_delete function that attempts to send a DELETE request to the API.   DONE
# The request method should use the string f"{API_URL}{path}/{id}" to access the correct path,
# where id refers to the id number of the question to be deleted. 
def api_delete(path, id):
    try:
        response = requests.delete(f"{API_URL}{path}/{id}", timeout=5)
        response.raise_for_status()
        return True
    except requests.RequestException as e:
        ui.notify(f"Could not delete question: {e}", type="negative")
        return False

# TODO: Create api_put function that attempts to send a PUT request to the API.   DONE
# The request method should use the string f"{API_URL}{path}/{id}" to access the correct path,
# where id refers to the id number of the question to be deleted. The data passed as an argument
# to this function must be sent with the request so that the API knows the updated values to add 
# to the dataset (similar to how data is sent in api_post).
def api_put(path, id, data):
    try:
        response = requests.put(
            f"{API_URL}{path}/{id}",
            json=data,
            timeout=5
        )
        response.raise_for_status()
        return True
    except requests.RequestException as e:
        ui.notify(f"Could not update question: {e}", type="negative")
        return False

def delete_question(id): #helper
    if api_delete("/delete", id):
        render_page()

def edit_question(question): # clicking Update question sends the changes, closes the dialog on success, and refreshes the page.
    with ui.dialog() as dialog, ui.card():
        ui.label("Edit question").classes("text-lg font-bold")

        new_q = ui.textarea(
            label="Question",
            value=question["q"]
        )
        new_a = ui.textarea(
            label="Answer",
            value=question["a"]
        )

        def save_changes():
            if api_put("/update", question["id"], {
                "question": new_q.value,
                "answer": new_a.value
            }):
                dialog.close()
                render_page()

        ui.button("Update question", on_click=save_changes)
        ui.button("Cancel", on_click=dialog.close)

    dialog.open()

# TODO: Add edit and delete buttons dynamically to each question card. DONE
def render_question(question):
    with ui.card().classes(
        "w-full p-5 gap-3 rounded-xl shadow-sm border border-slate-200"
    ) as card:
        card.on("click", lambda: toggle_answer(question["id"]))

        ui.label(question["q"]).classes(
            "text-lg font-semibold text-slate-900"
        )

        ui.label(f'Answer: {question["a"]}').classes(
            "text-base text-green-800 bg-green-50 p-3 rounded-lg w-full"
        ).bind_visibility_from(question["state"], "show_answer")

        with ui.row().classes("w-full justify-end gap-2"):
            ui.button("Edit", color="blue-8").props("outline").on(
                "click",
                lambda: edit_question(question),
                js_handler="(event) => { event.stopPropagation(); emit(event); }",
            )

            ui.button("Delete", color="red-8").props("outline").on(
                "click",
                lambda: delete_question(question["id"]),
                js_handler="(event) => { event.stopPropagation(); emit(event); }",
            )

def toggle_answer(id): # dont treat ID as list position
    for question in questions:
        if question["id"] == id:
            question["state"]["show_answer"] = (
                not question["state"]["show_answer"]
            )
            return

def add_new_question(question, answer):
    api_post("/add", {"question": question, "answer": answer})
    render_page()

def render_text_inputs():
    new_question_input = ui.input(label="New question").props("clearable")
    new_answer_input = ui.input(label="New answer").props("clearable")
    add_question_btn = ui.button(text="Add question", on_click=lambda: add_new_question(
        question=new_question_input.value,
        answer=new_answer_input.value
    ))

def init_page():
    render_page()

def render_page():
    global questions
    questions = api_get("/questions")
    page_body.clear()

    with page_body:
        with ui.column().classes("gap-1"):
            ui.label("HCI Review").classes(
                "text-3xl font-bold text-slate-900"
            )
            ui.label("Click a question card to show or hide its answer.").classes(
                "text-base text-slate-600"
            )

        with ui.column().classes("w-full gap-4"):
            for question in questions:
                question["state"] = {"show_answer": False}
                render_question(question)

        render_text_inputs()
    

init_page()
ui.run(port=8084, title="HCI Review Application")