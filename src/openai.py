from typing import List, Optional

import openai


def find_closest_match(
    search_param: str,
    options: List[str],
    model: str = "gpt-4",
    openai_api_key: Optional[str] = None,
    temperature: Optional[float] = 0.7,
    max_tokens: Optional[int] = 50,
) -> str:
    if openai_api_key:
        openai.api_key = openai_api_key

    # Number of options to be rated in each API call
    batch_size = 3
    scores = {}

    # Initial message
    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant. Please rate the match between search parameters and options from 1 to 100. Only respond with a number.",
        }
    ]

    # Loop through the options in batches
    for i in range(0, len(options), batch_size):
        batched_options = options[i : i + batch_size]
        for option in batched_options:
            messages.append(
                {
                    "role": "user",
                    "content": f"Rate the match between '{search_param}' and '{option}' from 1 to 100.",
                }
            )

        # Make API call with the batched messages
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        # Extract scores from the response
        for j, option in enumerate(batched_options):
            try:
                scores[option] = float(
                    response["choices"][0]["message"]["role"] == "assistant"
                    and response["choices"][0]["message"]["content"].split("\n")[j]
                )
            except:
                scores[option] = 0
        print(f"Tokens used: {response['usage']['total_tokens']}")

    # Return option with the highest score
    return max(scores, key=scores.get)
