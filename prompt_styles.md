# Alpaca style (Instruction Tuning Format)

The Alpaca/Instruction‑tuning style structures each example with three fields:

- instruction: what the model should do
- input: optional additional context or data needed to complete the task
- output: the desired answer

This format is commonly used for creating training/evaluation datasets and can also be mimicked at inference time to get concise, task‑focused responses.

## Minimal template

Plain text form (no JSON):

```
Instruction:
{instruction}

Input:
{input}

Output:
```

Notes:
- If there is no extra context, you can omit the “Input” block or set it to "".
- The model is expected to write only the content of “Output”.

## JSON example (dataset style)

```json
{
  "instruction": "Write a Python function that returns the square of a number.",
  "input": "",
  "output": "def square(x: int) -> int:\n    return x * x"
}
```

## Example with non‑empty input

```
Instruction:
Extract all email addresses from the given text and return them as a JSON array.

Input:
Hello from ann@example.com and dev.team@mail.example.org; bounce: no-reply@invalid.

Output:
```

Expected model output:

```json
["ann@example.com", "dev.team@mail.example.org"]
```

## Using Alpaca style with this project

- For documentation/examples, you can copy the templates above directly.
- To combine with the Persona approach, prepend a short persona header before the Alpaca blocks, for example:

```
Persona: Senior Python library maintainer
Tone: concise, professional
Audience: intermediate developers

Instruction:
Refactor the function to be pure and add type hints.

Input:
def add(a, b):
    print(a + b)

Output:
```

Then paste your code as the Output.

Tip: If you want stricter output formats (e.g., always JSON), you can merge the Few‑shot rules from prompts.md with the Alpaca “Instruction/Input/Output” framing.


# CHATML style
ChatML is a conversation formatting style that uses explicit role markers to delimit messages. A common variant uses special tokens like `<|im_start|>` and `<|im_end|>` to wrap each message with its role (system, user, assistant). It’s frequently used for training or for APIs that accept a single prompt string instead of a structured messages array.

Notes:
- If your API already accepts `[{role, content}, ...]` messages (like OpenAI/Gemini chat), you usually do NOT need ChatML; the SDK handles roles for you.
- Use ChatML mainly when you must pack a full multi‑turn conversation into a single text field, or when a model was specifically trained/fine‑tuned on ChatML.

## Minimal ChatML template

```
<|im_start|>system
{system_content}
<|im_end|>
<|im_start|>user
{user_content}
<|im_end|>
```

Where `{system_content}` can include persona/tone/audience guidance, and `{user_content}` is the user’s request.

## Example: Persona + Zero‑shot guardrail in ChatML

```
<|im_start|>system
Persona: Senior Python library maintainer
Tone: concise, professional
Audience: intermediate developers

Guidance:
- Keep responses concise and professional.
- Prefer deterministic, safe solutions.
- If constraints conflict, prioritize correctness over style.

Answer only coding questions with code. If the request is not about programming, reply: 'sorry, no'.
<|im_end|>
<|im_start|>user
Write a Python function that returns the square of a number.
<|im_end|>
<|im_start|>assistant
def square(x: int) -> int:
    return x * x
<|im_end|>
```

## Few‑shot in ChatML
Embed multiple user/assistant exchanges to demonstrate behavior and formatting.

```
<|im_start|>system
You are a coding‑only assistant.
Rules:
- If the request is not about programming, reply exactly: "sorry, no".
- When it is a coding request, reply in JSON using the schema below.

Output JSON schema:
{
  "code": string | null,
  "isCodingQuestion": boolean
}
<|im_end|>

<|im_start|>user
tell a joke
<|im_end|>
<|im_start|>assistant
{"code": null, "isCodingQuestion": false}
<|im_end|>

<|im_start|>user
give me recipe for meal XY
<|im_end|>
<|im_start|>assistant
{"code": null, "isCodingQuestion": false}
<|im_end|>

<|im_start|>user
write a Python function that returns the square of a number
<|im_end|>
<|im_start|>assistant
{"code": "def square(x: int) -> int:\n    return x * x", "isCodingQuestion": true}
<|im_end|>
```

## When special tokens aren’t supported
Some systems don’t recognize `<|im_start|>`/`<|im_end|>`. You can still mimic ChatML with plain text role headers:

```
System:
{system_content}

User:
{user_content}

Assistant:
{assistant_content}
```

## Using ChatML with this project
- The included clients (`openai/client.py`, `gemini/client.py`) already send structured `messages=[{role, content}]`. Prefer that over packing ChatML into a single string.
- If you must send a single prompt (e.g., a different endpoint), compose the ChatML string using the templates above, optionally combining with the Persona guidance used elsewhere in this repo.

# INST Prompt style
The INST style uses bracketed instruction markers popularized by LLaMA/Mistral instruct models. It wraps the user instruction (optionally preceded by a system section) between opening and closing tags. This is useful when a single prompt string must encode roles and guardrails without a structured messages array.

Notes:
- Common tokens: `[INST] ... [/INST]` and optional system section `<<SYS>> ... <</SYS>>` inside the first instruction.
- Some model families expect BOS/EOS tokens like `<s>` and may emit `</s>`; your client/SDK usually handles them.
- Prefer your SDK’s structured messages when available; use INST only when a model is fine‑tuned on it or a single text field is required.

## Minimal template (single turn)

```
[INST]
{user_instruction}
[/INST]
```

Where `{user_instruction}` is the user’s request.

## With System section (LLaMA‑style)

Use a system block to encode persona/guardrails inside the first instruction:

```
[INST] <<SYS>>
{system_content}
<</SYS>>

{user_instruction}
[/INST]
```

Example `system_content` (aligns with this repo’s Persona + Zero‑shot guardrail):

```
Persona: Senior Python library maintainer
Tone: concise, professional
Audience: intermediate developers

Guidance:
- Keep responses concise and professional.
- Prefer deterministic, safe solutions.
- If constraints conflict, prioritize correctness over style.

Answer only coding questions with code. If the request is not about programming, reply: 'sorry, no'.
```

## Example: Persona + INST

```
[INST] <<SYS>>
Persona: Senior Python library maintainer
Tone: concise, professional
Audience: intermediate developers

Answer only coding questions with code. If the request is not about programming, reply: 'sorry, no'.
<</SYS>>

Write a Python function that returns the square of a number.
[/INST]
```

Possible model output:

```
def square(x: int) -> int:
    return x * x
```

## Few‑shot with INST (multi‑turn examples)
Demonstrate desired behavior by including several instruction/response pairs. The assistant’s response follows the closing `[/INST]` of each example.

```
[INST] <<SYS>>
You are a coding‑only assistant.
Rules:
- If the request is not about programming, reply exactly: "sorry, no".
- When it is a coding request, reply in JSON using the schema below.

Output JSON schema:
{
  "code": string | null,
  "isCodingQuestion": boolean
}
<</SYS>>

tell a joke
[/INST]
{"code": null, "isCodingQuestion": false}

[INST]
give me recipe for meal XY
[/INST]
{"code": null, "isCodingQuestion": false}

[INST]
write a Python function that returns the square of a number
[/INST]
{"code": "def square(x: int) -> int:\n    return x * x", "isCodingQuestion": true}
```

## When INST tokens aren’t recognized
If a model or endpoint doesn’t support `[INST]`/`[/INST]`/`<<SYS>>`, mimic the structure with plain headers:

```
System:
{system_content}

Instruction:
{user_instruction}
```

## Using INST with this project
- The included clients (`openai/client.py`, `gemini/client.py`) already support structured `messages=[{role, content}]`; prefer that when possible.
- If you must send a single prompt string (e.g., different endpoint or a finetuned INST model), compose the string using the templates above. You can reuse the Persona content from this repo in the `<<SYS>>` block.