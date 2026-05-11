import pyperclip

def detect_ai_insertion(previous_content: str, current_content: str, time_delta_ms: float, inserted_block: str):
    delta = len(current_content) - len(previous_content)
    is_ai_candidate = False
    score = 0.1

    # Heuristic 1: Velocity (Massive block of text appearing instantly)
    if delta >= 80 and time_delta_ms < 400:
        score = 0.8
        is_ai_candidate = True
    elif delta >= 80 and time_delta_ms < 800:
        score = 0.4

    # Heuristic 2: Clipboard cross-reference
    try:
        clipboard = pyperclip.paste()
        if clipboard and len(clipboard) > 40 and clipboard in current_content:
            score += 0.25
            if score >= 0.45:
                is_ai_candidate = True
    except Exception:
        pass

    return is_ai_candidate, score, delta