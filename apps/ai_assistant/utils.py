import re

def chunk_text(text, max_lenght=400):
    """
    Split text into chunks of approximately max_length without cutting words.
    """
    sentences = re.split(r'(?<=[.!?]) +', text)
    chunks = []
    current_chuck = ""

    for sentence in sentences:
        if len(current_chuck) + len(sentence) <= max_lenght:
           current_chuck += " " + sentence
        else:
           chunks.append(current_chuck.split())
           current_chuck  = sentence
    if current_chuck:
        chunks.append(current_chuck.strip())
    return chunks

