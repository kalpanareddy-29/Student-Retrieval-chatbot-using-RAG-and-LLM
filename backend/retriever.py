import os
import re
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

# ✅ Correct FAISS path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAISS_PATH = os.path.join(BASE_DIR, "DATA", "faiss_index")
CHUNK_PATH = os.path.join(BASE_DIR, "DATA", "chunks")
# ✅ Correct FAISS path (relative to backend folder)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAISS_PATH = os.path.join(BASE_DIR, "DATA", "faiss_index")


# ---------- LOAD VECTOR DB ----------
def load_vectorstore():
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    return FAISS.load_local(
        FAISS_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )
    return FAISS.load_local(FAISS_PATH, embeddings, allow_dangerous_deserialization=True)


db = load_vectorstore()
all_docs = list(db.docstore._dict.values())


# =====================================================
# 📊 TOTAL STUDENT COUNT (UNCHANGED)
# =====================================================

def count_total_students():
    student_ids = set()

    for doc in all_docs:
        sid = doc.metadata.get("student_id")
        if sid:
            student_ids.add(str(sid).upper())

    return len(student_ids)


# =====================================================
# 🎓 STUDENT ID DETECTION (UNCHANGED)
# =====================================================

   

def extract_name(query):
    q = query.lower()

    remove_words = {"marks", "grades", "cgpa", "of", "student", "show", "me"}
    words = [w for w in q.split() if w not in remove_words]

    return " ".join(words).strip() if words else None

def find_student_by_name(name):
    name = name.lower()

    for doc in all_docs:
        if doc.metadata.get("type") == "student_info":
            content = doc.page_content.lower()
            if name in content:
                return doc.metadata.get("student_id")
    return None

# ---------- STUDENT ID DETECTION ----------
def extract_student_id(query):
    query = query.upper().replace(" ", "")
    match = re.search(r'(22|23)\d{3}[A-Z]\d{4}', query)
    return match.group(0) if match else None


def extract_student_name(query):
    q = query.lower()

    for doc in all_docs:
        if doc.metadata.get("type") == "student_info":
            lines = doc.page_content.split("\n")
            name_line = [l for l in lines if "Student Name:" in l]

            if not name_line:
                continue

            full_name = name_line[0].split("Student Name:")[-1].strip().lower()
            name_parts = full_name.split()

            for part in name_parts:
                if len(part) > 3 and part in q:
            # ✅ match if ANY meaningful name part is in query
            for part in name_parts:
                if len(part) > 3 and part in q:
                    print(f"✅ Name match found: {part} → {doc.metadata.get('student_id')}")
                    return doc.metadata.get("student_id")

    return None

# ---------- SEMESTER DETECTION ----------
def extract_semester(query):
    q = query.lower().replace(" ", "").replace("-", "")

    mapping = {
        "1-1": "I Year I Sem",
        "1-2": "I Year II Sem",
        "2-1": "II Year I Sem",
        "2-2": "II Year II Sem",
        "3-1": "III Year I Sem",
        "3-2": "III Year II Sem",
        "firstyearfirstsem": "I Year I Sem",
        "firstyearsecondsem": "I Year II Sem",
        "secondyearfirstsem": "II Year I Sem",
        "secondyearsecondsem": "II Year II Sem",
        "thirdyearfirstsem": "III Year I Sem",
        "thirdyearsecondsem": "III Year II Sem",
        "1st year 1st sem": "I Year I Sem",
        "1styear1stsem": "I Year I Sem",
        "1st year 2nd sem": "I Year II Sem",
        "1styear2ndsem": "I Year II Sem",

        # 🔹 2nd Year
        "2nd year 1st sem": "II Year I Sem",
        "2ndyear1stsem": "II Year I Sem",
        "2nd year 2nd sem": "II Year II Sem",
        "2ndyear2ndsem": "II Year II Sem",

        # 🔹 3rd Year
        "3rd year 1st sem": "III Year I Sem",
        "3rdyear1stsem": "III Year I Sem",
        "3rd year 2nd sem": "III Year II Sem",
        "3rdyear2ndsem": "III Year II Sem",

        "firstsem": "I Year I Sem",
        "secondsem": "I Year II Sem",
        "thirdsem": "II Year I Sem",
        "fourthsem": "II Year II Sem",
        "fifthsem": "III Year I Sem",
        "sixthsem": "III Year II Sem",
    }

    for key, val in mapping.items():
        if key in q:
            return val

    return None


# =====================================================
# 🧠 INTENT DETECTION (ONLY ADD NEW ANALYTICS)
# =====================================================

# ---------- INTENT DETECTION ----------
def detect_intent(query):
    q = query.lower()

    if "father" in q:
        return "father_name"

    if ("student" in q and "name" in q) or ("student" in q and "details" in q) or "details" in q:
        return "student_details"

    if "branch" in q:
        return "branch"

    if "college" in q:
        return "college"
    
    if "subject" in q or "course" in q:
        return "subjects"

    if "total students" in q or "how many students" in q:
        return "total_students"
    
    if any(word in q for word in ["ranking", "rank"]):
        return "ranks"
    
    if "topper" in q and ("sem" in q or "all" in q):
                 # specific semester
            return "semester_topper"

    # 🔥 NEW ANALYTICS INTENTS

    if "topper" in q or "highest cgpa" in q:
        return "topper"

    if "maximum backlog" in q or "most backlogs" in q or "more backlogs" in q:
        return "max_backlogs"

    if "how many backlogs" in q :
        return "backlog_count"

    if "less cgpa" in q or "last" in q or "low cgpa" in q or "low marks" in q:
        return "low cgpa"
    
    if "cgpa" in q:
        return "cgpa"
    
    if "performance" in q or "analysis" in q or "summarise" in q:
        return "analysis"

    if "marks" in q or "grades" in q or "results" in q:
        return "all_marks"

    return "general"


def semester_topper(semester=None):

    semester_map = {
        "I Year I Sem": "I B.Tech. I Sem. R20",
        "I Year II Sem": "I B.Tech. II Sem. R20",
        "II Year I Sem": "II B.Tech. I Sem. R20",
        "II Year II Sem": "II B.Tech. II Sem. R20",
        "III Year I Sem": "III B.Tech. I Sem. R20",
        "III Year II Sem": "III B.Tech. II Sem. R20",
        "IV Year I Sem": "IV B.Tech. I Sem. R20",
    }

    # 🔹 If semester provided → convert using dictionary
    if semester:
        if semester in semester_map:
            semester_list = [semester_map[semester]]
        else:
            return "⚠ Semester not recognized."
    else:
        # 🔹 If no semester provided → check all semesters
        semester_list = list(semester_map.values())

    results = []

    for target_sem in semester_list:

        highest = -1
        topper = None

        for file in os.listdir(CHUNK_PATH):
            if not file.endswith("_cgpa.txt"):
                continue

            file_path = os.path.join(CHUNK_PATH, file)

            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Extract student ID & name
            id_match = re.search(r"Student ID:\s*(.*)", content)
            name_match = re.search(r"Student Name:\s*(.*)", content)

            if not id_match or not name_match:
                continue

            sid = id_match.group(1).strip()
            name = name_match.group(1).strip()

            # Find semester CGPA
            sem_pattern = rf"{re.escape(target_sem)}.*?CGPA:\s*(\d+\.\d+)"
            sem_match = re.search(sem_pattern, content)

            if sem_match:
                cgpa = float(sem_match.group(1))

                if cgpa > highest:
                    highest = cgpa
                    topper = (sid, name, cgpa)

        if topper:
            results.append((target_sem, topper))

    if not results:
        return "⚠ No semester data found."

    # 🔥 If only one semester requested
    if semester:
        sem, (sid, name, cgpa) = results[0]
        return f"""🏆 Topper in {sem}
Student ID: {sid}
Name: {name}
CGPA: {cgpa}"""

    # 🔥 If all semesters requested
    output = "🏆 Semester-wise Toppers\n\n"

    for sem, (sid, name, cgpa) in results:
        output += f"{sem}\n"
        output += f"Student ID: {sid}\n"
        output += f"Name: {name}\n"
        output += f"CGPA: {cgpa}\n\n"

    return output
# =====================================================
# 📂 CHUNK ANALYTICS FUNCTIONS (NEW)
# =====================================================

def load_all_chunk_data():
    students = []

    if not os.path.exists(CHUNK_PATH):
        return students

    for file in os.listdir(CHUNK_PATH):
        if file.endswith("_cgpa.txt"):
            student_id = file.replace("_cgpa.txt", "")
            path = os.path.join(CHUNK_PATH, file)

            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            cgpa_match = re.search(r"Final CGPA → (\d+\.\d+)", content)
            backlog_match = re.search(r"Total Backlogs → (\d+)", content)

            if cgpa_match and backlog_match:
                students.append({
                    "student_id": student_id,
                    "cgpa": float(cgpa_match.group(1)),
                    "backlogs": int(backlog_match.group(1))
                })

    return students

def get_last():
    students = load_all_chunk_data()
    if not students:
        return "No student data found."

    topper = min(students, key=lambda x: x["cgpa"])
    sid = topper["student_id"]

    student_name = "Not available"  # default value

    # 🔥 Get name from student_info document
    for doc in all_docs:
        if (
            str(doc.metadata.get("student_id", "")).upper() == sid.upper()
            and doc.metadata.get("type") == "student_info"
        ):
            content = doc.page_content
            match = re.search(r"Student Name:\s*(.*)", content)
            if match:
                student_name = match.group(1).strip()
            break

    return (
        f"🏆 Topper: {sid} | "
        f"Name: {student_name} | "
        f"CGPA: {topper['cgpa']} | "
        f"Backlogs: {topper['backlogs']}"
    )

def get_topper():
    students = load_all_chunk_data()
    if not students:
        return "No student data found."

    topper = max(students, key=lambda x: x["cgpa"])
    sid = topper["student_id"]

    student_name = "Not available"  # default value

    # 🔥 Get name from student_info document
    for doc in all_docs:
        if (
            str(doc.metadata.get("student_id", "")).upper() == sid.upper()
            and doc.metadata.get("type") == "student_info"
        ):
            content = doc.page_content
            match = re.search(r"Student Name:\s*(.*)", content)
            if match:
                student_name = match.group(1).strip()
            break

    return (
        f"🏆 ID : {sid} | "
        f"Name: {student_name} | "
        f"CGPA: {topper['cgpa']} | "
        f"Backlogs: {topper['backlogs']}"
    )

def get_max_backlogs():
    students = load_all_chunk_data()
    if not students:
        return "No student data found."

    worst = max(students, key=lambda x: x["backlogs"])
    sid = worst["student_id"]

    student= "Not available"
    if worst["backlogs"] == 0:
        return "✅ No student has any backlogs."
    for doc in all_docs:
        if (
            str(doc.metadata.get("student_id", "")).upper() == sid.upper()
            and doc.metadata.get("type") == "student_info"
        ):
            content = doc.page_content
            match = re.search(r"Student Name:\s*(.*)", content)
            if match:
                student = match.group(1).strip()
            break

    return (
        f"⚠ Student with Maximum Backlogs: {worst['student_id']} \n"
        f"Student name :{student}\n"
        f"Backlogs: {worst['backlogs']} \n "
        f"CGPA: {worst['cgpa']}\n"
    )

def count_students_with_backlogs():
    students = load_all_chunk_data()
    count = sum(1 for s in students if s["backlogs"] > 0)
    return f"📚 Students with backlogs: {count}"


def get_chunk_data(student_id):
    file_path = os.path.join(CHUNK_PATH, f"{student_id}_cgpa.txt")

    if not os.path.exists(file_path):
        return f"❌ No CGPA data found for {student_id}"

    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()
  

def get_class_ranking(top_n=None):

    students = []

    for file in os.listdir(CHUNK_PATH):
        if not file.endswith("_cgpa.txt"):
            continue

        with open(os.path.join(CHUNK_PATH, file), "r", encoding="utf-8") as f:
            content = f.read()

        id_match = re.search(r"Student ID:\s*(.*)", content)
        name_match = re.search(r"Student Name:\s*(.*)", content)
        cgpa_match = re.search(r"Final CGPA → (\d+\.\d+)", content)

        if id_match and name_match and cgpa_match:
            sid = id_match.group(1).strip()
            name = name_match.group(1).strip()
            cgpa = float(cgpa_match.group(1))

            students.append({
                "student_id": sid,
                "name": name,
                "cgpa": cgpa
            })

    # Sort descending by CGPA
    students.sort(key=lambda x: x["cgpa"], reverse=True)

    if top_n:
        students = students[:top_n]

    return students



def students_above_percentage(min_percentage):

    results = []

    for file in os.listdir(CHUNK_PATH):
        if not file.endswith("_cgpa.txt"):
            continue

        with open(os.path.join(CHUNK_PATH, file), "r", encoding="utf-8") as f:
            content = f.read()

        id_match = re.search(r"Student ID:\s*(.*)", content)
        name_match = re.search(r"Student Name:\s*(.*)", content)
        cgpa_match = re.search(r"Final CGPA → (\d+\.\d+)", content)

        if id_match and name_match and cgpa_match:
            sid = id_match.group(1).strip()
            name = name_match.group(1).strip()
            cgpa = float(cgpa_match.group(1))

            percentage = cgpa

            if percentage >= min_percentage:
                results.append((sid, name, cgpa, percentage))

    if not results:
        return f"No students above {min_percentage}%."

    # Sort highest first
    results.sort(key=lambda x: x[3], reverse=True)

    output = f"🎓 Students Above {min_percentage} CGPA in a class are :\n\n"

    for sid, name, cgpa, percent in results:
        output += f"{sid} | {name} | CGPA: {cgpa} | {percent:.2f}%\n"

    return output

# =====================================================
# 🚀 RETRIEVAL LOGIC (MINIMAL CHANGE)
# =====================================================

def retrieve_docs(query, k=1):

    student_id = extract_student_id(query)
    semester = extract_semester(query)
    intent = detect_intent(query)
    print(student_id,semester,intent)

    if not student_id:
        student_id = extract_student_name(query)
    
    # 🔹 Global Analytics
    #Topper sem wise 
    if "above" in query  and "cgpa" in query:
        match = re.search(r"(\d+)", query)
        if match:
            percent = int(match.group(1))
            return students_above_percentage(percent)
        
    if intent == "semester_topper":
    # If semester detected directly (like 2-2)
        if semester:
            return semester_topper(semester)

        # If user mentions semester word but no specific sem
        if "sem" in query:
            return semester_topper()
      
    if intent == "topper":
        return get_topper()
    
    if intent == "low cgpa":
        return get_last()
    
    if intent == "max_backlogs":
        return get_max_backlogs()

    if intent == "backlog_count":
        return count_students_with_backlogs()

    if intent == "total_students":
        return f"📊 Total students available: {count_total_students()}"

# 🔥 STUDENT METADATA DETAILS MODE
    # 🎯 Student specific
    if intent in ["cgpa", "analysis", "all_marks"]:
            if student_id:
                sid = student_id.upper()
                return get_chunk_data(sid)
            return "please provide student ID for knowing analysis and performance."
    if student_id:
        sid = student_id.upper()

    if "student" in q and "name" in q :
        return "student_name"
    if "id" in q or "register number" in q :
        return "student_name"
    if "subject" in q or "course" in q :
        return "subjects"
    marks_keywords = [
        "marks", "mark", "grade", "grades",
        "cgpa", "gpa", "result", "results",
        "score", "scores", "academic", "performance"
    ]
    if any(word in q for word in marks_keywords):
        return "all_marks"
    return "general"


# ---------- RETRIEVAL LOGIC ----------
def retrieve_docs(query, k=1):
    student_id = extract_student_id(query)
    semester = extract_semester(query)
    intent = detect_intent(query)
    if not student_id:
        student_id = extract_student_name(query)
    print(f"student id, semester, intent: {student_id}, {semester}, {intent}")
    
    # 🎯 If student ID is mentioned
    if student_id:
        sid = student_id.upper()
  
        student_docs = [
            doc for doc in all_docs
            if str(doc.metadata.get("student_id", "")).upper() == sid
        ]
<<<<<<< HEAD
        if intent in ["student_details", "branch", "college", "student_name", "father_name"]:

            for doc in all_docs:
                if (
                    str(doc.metadata.get("student_id", "")).upper() == sid
                    and doc.metadata.get("type") == "student_info"
                ):

                    content = doc.page_content

                    # 🔥 Extract details from chunk text
                    name_match = re.search(r"Student Name:\s*(.*)", content)
                    father_match = re.search(r"Father Name:\s*(.*)", content)
                    branch_match = re.search(r"Branch:\s*(.*)", content)
                    college_match = re.search(r"College:\s*(.*)", content)

                    student_name = name_match.group(1).strip() if name_match else "Not available"
                    father_name = father_match.group(1).strip() if father_match else "Not available"
                    branch = branch_match.group(1).strip() if branch_match else "Not available"
                    college = college_match.group(1).strip() if college_match else "Not available"

                    if intent == "student_details":
                        return (
                            f"🎓 Student ID: {sid}\n"
                            f"👤 Name: {student_name}\n"
                            f"👨 Father Name: {father_name}\n"
                            f"🏫 Branch: {branch}\n"
                            f"🏛 College: {college}"
                        )

                    if intent == "student_name":
                        return f"👤 Name: {student_name}"

                    if intent == "father_name":
                        return f"👨 Father Name: {father_name}"

                    if intent == "branch":
                        return f"🏫 Branch: {branch}"

                    if intent == "college":
                        return f"🏛 College: {college}"
                    

            return "❌ Student details not found."

        if intent in ["student_name", "father_name"]:
            return [doc for doc in student_docs if doc.metadata.get("type") == "student_info"]


        return "❌ Student data not found."

    # 🎯 Semester only
    
    if intent == "ranks":

        match = re.search(r"top\s*(\d+)", query)
        if match:
            top_n = int(match.group(1))
        else:
            top_n = None   # full ranking

        return get_class_ranking(top_n)

    if semester:
        return [doc for doc in all_docs if doc.metadata.get("semester") == semester][:1]
    
    if intent in ["college", "branch"]:

        for doc in all_docs:
            if doc.metadata.get("type") == "student_info":
                return doc.page_content

        return "Student information not found."

    return "general"
=======

        # 🔹 Name / Father → only student_info chunk
        if intent in ["student_name", "father_name"]:
            return [doc for doc in student_docs if doc.metadata.get("type") == "student_info"]

        # 🔹 Subjects / Marks
            # ---------- ALL SEMESTER MARKS ----------
        if intent == "all_marks":
            semester_docs = [
                d for d in student_docs if d.metadata.get("semester")
            ]
            #print("SEM DOCS:", semester_docs)

            if not semester_docs:
                return "❌ No semester data found."

            output = f"📘 All Semester Marks for {sid}:\n"

            for d in semester_docs:
                sem = d.metadata.get("semester")
                subjects = d.page_content.split("\n")[1:]

                output += f"\n🎓 {sem}\n"
                for i, sub in enumerate(subjects, 1):
                    output += f"{i}. {sub}\n"
            #print("OUTPUT:", output)
            return output

        if intent == "subjects":
            if semester:
                return [doc for doc in student_docs if doc.metadata.get("semester") == semester]
            return [doc for doc in student_docs if doc.metadata.get("semester")]

        return "NOT FOUND"

    # 🎯 Only semester mentioned
    if semester:
        return [doc for doc in all_docs if doc.metadata.get("semester") == semester][:1]

    # 🎯 General semantic search
    return db.similarity_search(query, k=1)
>>>>>>> 864c4dda27a64837d3159473b79122a16c9535e8


# ---------- CLI MODE ----------
if __name__ == "__main__":
    print("📚 Smart Student RAG Ready! Type 'exit' to stop.\n")

    while True:
        q = input("Ask something: ")

        if q.lower() == "exit":
            break

        docs = retrieve_docs(q)
<<<<<<< HEAD

=======
        #print("docs:",docs)
>>>>>>> 864c4dda27a64837d3159473b79122a16c9535e8
        print("\n🔎 Results:\n")

        if not docs:
            print("No matching data found.\n")

<<<<<<< HEAD
        else:
            print(docs)
=======
        # ✅ CASE 1 — formatted string (marks / cgpa / grades)
        elif isinstance(docs, str):
            print(docs)

        # ✅ CASE 2 — normal document list
        else:
            for d in docs:
                print("Metadata:", d.metadata)
                print(d.page_content)
                print("-" * 60)


>>>>>>> 864c4dda27a64837d3159473b79122a16c9535e8
