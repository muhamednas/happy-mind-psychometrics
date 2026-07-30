from pydantic import BaseModel
from fastapi import APIRouter

router = APIRouter()


class ChatMessage(BaseModel):
    message: str


class ChatReply(BaseModel):
    reply: str


# Pre-defined FAQ knowledge base with keyword matching
FAQ_ENTRIES = [
    {
        "keywords": ["hello", "hi", "hey", "good morning", "good afternoon"],
        "reply": "Hello! 👋 I'm your Happy Mind assistant. How can I help you today? You can ask me about getting started, access codes, test duration, or anything else!"
    },
    {
        "keywords": ["start", "begin", "how do i", "get started", "first step"],
        "reply": "To get started, enter your access code (format: HM-XXXX-X) and your email address on the login page. Once logged in, you'll see your assessment dashboard with all available tests."
    },
    {
        "keywords": ["access code", "code", "hm-", "login code", "where is my code"],
        "reply": "Your access code was provided by your organization or HR department. It follows the format HM-XXXX-X (e.g., HM-A7K2-B). If you haven't received one, please contact your organization administrator."
    },
    {
        "keywords": ["how long", "duration", "time", "minutes", "hours"],
        "reply": "Each test typically takes 15–30 minutes to complete. Your progress is saved automatically every few seconds, so you won't lose any work if you need to take a break."
    },
    {
        "keywords": ["save", "autosave", "progress", "lose", "lost"],
        "reply": "Don't worry! Your responses are automatically saved every 5 seconds as you work. You can safely close the browser and return later — your progress will be right where you left off."
    },
    {
        "keywords": ["stuck", "help", "problem", "issue", "error", "bug"],
        "reply": "I'm sorry you're having trouble! Try refreshing the page first. If the issue persists, please contact your organization administrator with a description of the problem."
    },
    {
        "keywords": ["result", "score", "report", "performance", "how did i do"],
        "reply": "Your results will be compiled into a comprehensive report and shared with your organization after you complete all assessments. Individual scores are not displayed during the test."
    },
    {
        "keywords": ["submit", "finish", "complete", "done", "end"],
        "reply": "When you've answered all questions in a test, click the 'Submit Test' button. You'll be asked to confirm before final submission. Once submitted, the test is marked as Completed and cannot be retaken."
    },
    {
        "keywords": ["skip", "go back", "previous", "change answer", "redo"],
        "reply": "You can navigate freely between questions using the Previous and Next buttons. Feel free to skip questions and come back to them later before submitting."
    },
    {
        "keywords": ["privacy", "data", "confidential", "secure", "safe"],
        "reply": "Your data is handled with strict confidentiality. All responses are stored securely and only accessible by authorized administrators within your organization. We take your privacy seriously."
    },
]


@router.post("/message", response_model=ChatReply)
async def chat_message(chat: ChatMessage):
    """Simple FAQ chatbot with keyword matching."""
    msg = chat.message.lower().strip()

    # Try to match against FAQ entries
    best_match = None
    best_score = 0

    for entry in FAQ_ENTRIES:
        score = sum(1 for kw in entry["keywords"] if kw in msg)
        if score > best_score:
            best_score = score
            best_match = entry

    if best_match and best_score > 0:
        return ChatReply(reply=best_match["reply"])

    return ChatReply(
        reply="I'm not sure about that. You can ask me about getting started, access codes, test duration, saving progress, or submitting tests. For other questions, please contact your organization administrator."
    )
