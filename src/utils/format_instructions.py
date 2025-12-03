# function to fetch format_instructions of ArtIdeaSet
def artIdeaSet_format_instructions():
    format_instructions = '''
    Respond ONLY with a JSON object matching this structure:
    {
    "mood_or_focus": "string or null",
    "ideas": [
        {
        "id": "idea_1",
        "title": "short catchy title",
        "drawing_prompt": "detailed prompt of what to draw",
        "style_direction": "how to style it (mood, colors, composition)",
        "why_it_fits_you": "why this idea matches the artist's style/history",
        "recommended_format": "reel" | "image post" | "corousel post",
        "difficulty": "easy" | "medium" | "hard"
        },
        ...
    ]
    }
    Do NOT include $defs, schema definitions, or backticks.
    Make sure every idea object in ideas dictionary MUST have all the properties. Don't skip any.
    '''
    return format_instructions

# function to fetch format_instructions of ReplyBatch
def reply_batch_format_instructions():
    format_instructions = '''
    Respond ONLY with a JSON object matching this structure:
    {
    {
    "post_id": "<string or null>",
    "replies": [
        {
        "comment_id": "<id from input>",
        "original_comment": "<text from input>",
        "suggestions": [
            "first reply option",
            "second reply option",
            "third reply option"
        ]
        },
        ...
    ]
    }
    Do NOT include $defs, schema definitions, or backticks.
    Make sure every reply suggestion object in replies dictionary MUST have all the properties. Don't skip any.
    '''
    return format_instructions