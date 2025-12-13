def build_prompt(question: str, contexts: list[dict]) -> str:
    if contexts:
        context_text = "\n\n".join(
            f"[Source {i+1} | score={c.get('score', 0):.3f}]\n{c['content']}"
            for i, c in enumerate(contexts)
        )
    else:
        context_text = "(no relevant sources found)"

    return f"""You are an IT Helpdesk assistant.

Use ONLY the sources below to answer the question.
If the answer is not in the sources, say: "I don't know based on the provided documents."

Sources:
{context_text}

Question:
{question}

Answer (be concise, actionable):
""".strip()
