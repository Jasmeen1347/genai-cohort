import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

# Improved system prompt with clear rules and grammar
system_prompt = """
You are an AI assistant who is an expert in MERN stack technology. Your job is to help developers prepare for technical interviews.

TASK: Generate 7 technical MERN stack interview questions with concise answers.

Rules:
1. Follow the strict JSON output format: { "step": "string", "content": "string" }
2. Follow steps in sequence: analyse → think → output → validate → result
3. Keep answers brief, technical, and to the point
4. Tailor difficulty to user's experience level
5. Avoid unnecessary words or explanations in answers

Example:
Input: I am a MERN developer with 5 years of experience. Help me prepare for interviews.
Output: { "step": "analyse", "content": "Alright! This developer has 5 years of experience in MERN stack." }
Output: { "step": "think", "content": "I need to prepare question-answer pairs tailored to an experienced MERN developer." }
Output: { "step": "output", "content": "question: How would you handle scaling for a MERN Stack application? answer: Use MongoDB sharding, backend load balancing (e.g., PM2), and CDN for frontend." }
Output: { "step": "validate", "content": "This is a solid question for a developer with 5 years of experience." }
Output: { "step": "result", "content": "Here is your set of tailored interview questions." }
"""

# Initial messages
messages = [
    { "role": "system", "content": system_prompt }
]

query = input("> ").strip()
messages.append({ "role": "user", "content": query })

question_count = 0
target_questions = 7
all_questions = []

while question_count < target_questions:
    # Use minimal message context to save tokens
    trimmed_messages = [messages[0]] + messages[-4:]

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=trimmed_messages
        )

        parsed_response = json.loads(response.choices[0].message.content)

        step = parsed_response.get("step", "").strip()
        content = parsed_response.get("content", "").strip()

        print(f"🧠: {step} - {content}")

        messages.append({ "role": "assistant", "content": content })

        if step == "output":
            all_questions.append(content)
            question_count += 1
            print(f"✅ Question {question_count}/{target_questions} added")

            if question_count < target_questions:
                messages.append({ "role": "user", "content": "Next question." })

    except Exception as e:
        print("⚠️ Error:", e)
        break

# Print all collected questions and answers
print("\n📋 All Questions and Answers:")
for i, qa in enumerate(all_questions, 1):
    print(f"{i}. {qa}")
