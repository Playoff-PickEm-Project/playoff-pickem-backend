from flask import abort

def validate_prop_exists(prop, custom_message=None):
    """Validate that a prop object is not None."""
    if prop is None:
        message = custom_message or "Prop not found"
        abort(404, message)
    return prop

def validate_prop_id(prop_id):
    """Validate prop ID is not None."""
    if prop_id is None:
        abort(400, "Prop ID is required")
    return prop_id

def validate_answer(answer):
    """Validate answer is not None or empty string."""
    if answer is None or (isinstance(answer, str) and answer.strip() == ""):
        abort(400, "Answer is required and cannot be empty")
    return answer.strip() if isinstance(answer, str) else answer

def validate_question(question):
    """Validate question is not None or empty string."""
    if not question or (isinstance(question, str) and question.strip() == ""):
        abort(400, "Question is required and cannot be empty")
    return question.strip() if isinstance(question, str) else question
