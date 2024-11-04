from typing import List, Optional, Dict
import openai


class OpenAIClient:
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        self.model = model
        if api_key:
            openai.api_key = api_key

    def get_ratings(self, prompt: str, options: List[str], temperature: float = 0.7, max_tokens: int = 50) -> Dict[
        str, float]:
        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant. Rate the match between the search parameter and options from 1 to 100.",
            }
        ]

        # Batch the options for fewer calls
        for option in options:
            messages.append({
                "role": "user",
                "content": f"Rate the match between '{prompt}' and '{option}' from 1 to 100.",
            })

        response = openai.ChatCompletion.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        scores = {}
        for i, option in enumerate(options):
            try:
                content = response["choices"][0]["message"]["content"]
                score = float(content.split("\n")[i])
                scores[option] = score
            except (IndexError, ValueError):
                scores[option] = 0

        return scores


def find_closest_match(
        search_param: str,
        options: List[str],
        client: OpenAIClient,
        temperature: Optional[float] = 0.7,
        max_tokens: Optional[int] = 50,
) -> Optional[str]:
    try:
        scores = client.get_ratings(search_param, options, temperature, max_tokens)
    except Exception as e:
        print(f"Error occurred in get_ratings: {e}")
        return None

    return max(scores, key=scores.get, default=None)