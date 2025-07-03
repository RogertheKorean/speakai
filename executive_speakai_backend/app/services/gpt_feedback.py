def generate_feedback(transcript: str) -> str:
    # Simulated correction logic
    suggestions = []

    if "Hi" in transcript:
        suggestions.append("Consider using 'Hello' for more formality.")
    if "I'm happy" in transcript:
        suggestions.append("You could say 'It's a pleasure to be here'.")

    if not suggestions:
        return "Your response was clear and appropriate."

    return " ".join(suggestions)
