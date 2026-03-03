from langchain_ollama import OllamaLLM
import time

# 🔥 IMPORT RETRIEVER FUNCTIONS
from retriever import (
    retrieve_docs,
    count_total_students,
    get_max_backlogs
)

# 🔥 Use Mistral
llm = OllamaLLM(
    model="mistral",
    temperature=0
)

def run_rag(query):

    total_start = time.time()
    q = query.lower().strip()

    # =====================================================
    # 🔹 RETRIEVAL
    # =====================================================
    retrieval_start = time.time()
    docs = retrieve_docs(query)
    print("retrieved context is", docs)
    print(f"📂 Retrieval Time: {time.time() - retrieval_start:.4f} seconds")
    if docs == "general":

        return (
        """Sorry,I couldn't find any relevant academic records for your query. 

Please choose one of the following categories:

• Student Marks  
• Subject lists
• Student Ranking,Topper,Backlogs
• Student Details  
• CGPA and Academic Performance  
• Semester Results  
• Total Student Strength  


Kindly enter your query with a valid roll number or category."""
    )


    # =====================================================
    # 🔹 GREETING MODE
    # =====================================================
    if q in ["hi", "hii", "hello", "hey", "good morning", "good evening"]:
        return (
            "👋 Hi! Welcome to RGMCET Academic Assistant.\n\n"
            "Academic Information Services:\n\n"
"📘 Student Records\n"
"1️⃣ Marks and Score Details\n"
"2️⃣ Semester Results\n"
"3️⃣ Subject List\n"
"4️⃣ Backlog Status\n"
"5️⃣ CGPA and Performance\n\n"

"📊 Institutional Data\n"
"6️⃣ Student Ranking and Top Performers\n"
"7️⃣ Total Student Strength\n\n"

"Please enter your request with a valid roll number where applicable."
        )

    # =====================================================
    # 🔹 HELP MODE
    # =====================================================
    if "help" in q or "what can you do" in q:
        return (
            "🤖 I can help with:\n"
            "• Student marks\n"
            "• CGPA & performance\n"
            "• Semester results\n"
            "• Ranking\n"
            "• Backlogs\n"
            "• Student details\n"
        )

    # =====================================================
    # 🔹 THANK YOU MODE
    # =====================================================
    if any(word in q for word in ["thank you", "thanks", "bye"]):
        return "😊 You're welcome! Let me know if you need any help."

    # =====================================================
    # 🔹 TOTAL STUDENTS
    # =====================================================
    if "total students" in q:
        return f"📊 Total Students: {count_total_students()}"

    # =====================================================
    # 🔹 MAX BACKLOGS
    # =====================================================
    if "highest backlogs" in q or "more backlogs" in q:
        return get_max_backlogs()

    # =====================================================
    # 🔹 STRING RESPONSE (Student Info / CGPA Chunk / Ranking)
    # =====================================================
    if isinstance(docs, str):

        context = docs

        # 🔥 BRANCH / COLLEGE MODE
        if "branch" in q or "college" in q:

            prompt = f"""
You are RGMCET Academic Assistant.

STRICT RULES:
- Use ONLY provided data.
- If branch asked → return ONLY branch name.
- If college asked → return ONLY college name.
- Do NOT include student name.
- No explanation.

DATA:
{context}

QUESTION:
{query}

ANSWER:
"""

            return llm.invoke(prompt)

        # 🔥 PERFORMANCE MODE
        if "performance" in q or "analysis" in q:

            prompt = f"""
You are RGMCET Academic Assistant.

STRICT RULES:
- Write paragraph format only.
- Minimum 120 words.
- Do NOT invent data.
- Use CGPA correctly.

DATA:
{context}

QUESTION:
{query}

ANSWER:
"""

            return llm.invoke(prompt)

        # 🔹 Otherwise return raw
        return context

    # =====================================================
    # 🔹 LIST RESPONSE (Subjects / Ranking List)
    # =====================================================
    if isinstance(docs, list) and docs:

        # 🔥 If ranking data (list of dict)
        if isinstance(docs[0], dict):

            prompt = f"""
You are RGMCET Academic Assistant.

Present the following ranking data clearly.
Do NOT modify CGPA.
Do NOT invent students.

DATA:
{docs}

ANSWER:
"""

            return llm.invoke(prompt)

        # 🔹 If subject documents
        context = "\n\n".join(doc.page_content for doc in docs)

    else:
        return "⚠️ No relevant data found. Please ask the above mentioned data."

    # =====================================================
    # 🔹 UNIVERSAL PROMPT
    # =====================================================
    prompt = f"""
You are RGMCET Academic Assistant.

GENERAL RULES:
- Use ONLY provided context.
- Do NOT invent marks.
- Keep numbers unchanged.

- If they are asking subjects list  → do not mention student name just give subejects and labs list only.dont keep like subjects of student with some name dont do like that .
-they as subject list you neeed to giv eit in list format like number 1 to upto n numbe rof subjects bro like heading should be keep as subjesct sin given semster
CONTEXT:

from retriever import retrieve_docs
from langchain_ollama import OllamaLLM

llm = OllamaLLM(model="tinyllama")


def run_rag(query):
    docs = retrieve_docs(query)

    if not docs:
        return "No records found."

    context = "\n".join([d.page_content for d in docs])

    prompt = f"""
You are a university academic records assistant.

TASK:
Answer ONLY using the student data in CONTEXT.

STRICT RULES:
- Do NOT explain
- Do NOT summarize
- Do NOT add extra words
- If asked for SUBJECTS → Return ONLY the subject names as a numbered list dont need of student id ,name 
- If data missing → Say exactly: Not available in records

STUDENT DATA:
{context}

QUESTION:
{query}

ANSWER:
"""

    return llm.invoke(prompt)

# =====================================================
# 🔹 CLI MODE
# =====================================================
if __name__ == "__main__":
    print("🎓 RGMCET Academic Assistant Ready\n")

    while True:
        q = input("Ask: ")

        if q.lower() == "exit":
            break

        print("\n📊 Answer:\n")
        print(run_rag(q))
        print("\n" + "=" * 60 + "\n")

if __name__ == "__main__":
    print("🎓 Student Academic RAG System Ready (type 'exit' to stop)\n")

    while True:
        q = input("Ask about a student: ")
        if q.lower() == "exit":
            break

        answer = run_rag(q)

        print("\n📊 Answer:\n")
        print(answer)
        print("\n" + "="*60 + "\n")
