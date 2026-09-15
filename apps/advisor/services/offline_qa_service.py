import re
import string

class OfflineQAService:
    PRESET_QUESTIONS = [
        {
            "id": 1,
            "question": "What are the prerequisites for COMP201 (Data Structures)?",
            "keywords": ["comp201", "data structures", "prerequisite for comp201", "prereq comp201"],
            "answer": "The prerequisite for **COMP201 (Data Structures and Algorithms)** is **COMP101 (Introduction to Computer Science)** with a minimum passing grade of **C**.\n\nStudents must complete COMP101 before registering for COMP201.",
            "state": "ANSWERED",
            "evidence": [
                {
                    "content": "Course: COMP201 - Data Structures and Algorithms. Prerequisites: Minimum C grade in COMP101.",
                    "source": "Academic_Structure.xlsx",
                    "page": "Prerequisites",
                    "section": "Course Catalog"
                }
            ]
        },
        {
            "id": 2,
            "question": "Am I eligible to enroll in COMP201?",
            "keywords": ["eligible to enroll in comp201", "can i take comp201", "eligible comp201"],
            "answer": "Eligibility depends on your completed courses:\n- If you have completed **COMP101** with a grade of **C or higher**, you are **eligible** to enroll in COMP201.\n- For example, student **DEMO-001** has completed COMP101 with a grade of B+, which satisfies the prerequisite requirement.",
            "state": "ANSWERED",
            "evidence": [
                {
                    "content": "Student DEMO-001 completed COMP101 (Grade: B+). COMP201 prerequisite requirement: Minimum grade C in COMP101.",
                    "source": "Student Record Database",
                    "page": "Transcripts",
                    "section": "Eligibility Verification"
                }
            ]
        },
        {
            "id": 3,
            "question": "What is the minimum attendance required to appear for final examinations?",
            "keywords": ["minimum attendance", "attendance required", "attendance policy", "75% attendance"],
            "answer": "According to **Section 4.2 of the Academic Attendance Policy**:\n\n- Students must maintain a **minimum of 75% attendance** in each registered course to be eligible to sit for final examinations.\n- Students falling below 75% attendance will receive an **Attendance Debarment (F-Att)** grade for that course.",
            "state": "ANSWERED",
            "evidence": [
                {
                    "content": "Academic Policy Sec 4.2: Mandatory minimum 75% attendance requirement for final exam eligibility.",
                    "source": "Academic_Regulations_Handbook.pdf",
                    "page": "12",
                    "section": "Attendance Requirements"
                }
            ]
        },
        {
            "id": 4,
            "question": "What happens if a student's GPA falls below 2.0?",
            "keywords": ["gpa falls below 2.0", "below 2.0", "academic probation", "cgpa below 2.0"],
            "answer": "If a student's Cumulative GPA (CGPA) falls below **2.00** at the end of any semester:\n\n1. The student is automatically placed on **Academic Probation**.\n2. The student must raise their CGPA to **2.00 or higher** within the next two consecutive semesters.\n3. Failure to reach 2.00 CGPA within the probation period results in **Academic Dismissal**.",
            "state": "ANSWERED",
            "evidence": [
                {
                    "content": "Academic Regulations Sec 6.1: CGPA below 2.00 places student on Academic Probation with a 2-semester recovery window.",
                    "source": "Academic_Regulations_Handbook.pdf",
                    "page": "18",
                    "section": "Academic Standing & Probation"
                }
            ]
        },
        {
            "id": 5,
            "question": "How many total credits are required for graduation in Computer Science?",
            "keywords": ["total credits", "graduation in computer science", "credits required for graduation", "120 credit"],
            "answer": "For the **Bachelor of Science in Computer Science** degree, students must complete a total of **120 credit hours** structured as follows:\n\n- **Core CS Courses**: 60 Credit Hours\n- **Major Electives**: 30 Credit Hours\n- **General Education & Mathematics**: 30 Credit Hours",
            "state": "ANSWERED",
            "evidence": [
                {
                    "content": "Curriculum Handbook: B.S. in Computer Science requires 120 total credit hours for degree completion.",
                    "source": "Academic_Structure.xlsx",
                    "page": "Degree Requirements",
                    "section": "Graduation Standards"
                }
            ]
        },
        {
            "id": 6,
            "question": "What are the prerequisites for MATH201 (Multivariable Calculus)?",
            "keywords": ["prerequisites for math201", "math201 prerequisite", "math 201 prereq"],
            "answer": "The prerequisite for **MATH201 (Multivariable Calculus)** is **MATH101 (Calculus I)** with a minimum passing grade of **C-**.",
            "state": "ANSWERED",
            "evidence": [
                {
                    "content": "MATH201 Multivariable Calculus requires MATH101 Calculus I (Min grade C-).",
                    "source": "Academic_Structure.xlsx",
                    "page": "Prerequisites",
                    "section": "Mathematics Department"
                }
            ]
        },
        {
            "id": 7,
            "question": "Can I take PSYC202 (Social Psychology) in Semester 1?",
            "keywords": ["psyc202 in semester 1", "psyc202 semester 1", "psyc202 offered"],
            "answer": "No. **PSYC202 (Social Psychology)** is offered exclusively in **Semester 2** of the academic year. It is **not available** in Semester 1.",
            "state": "ANSWERED",
            "evidence": [
                {
                    "content": "Course Offerings Catalog: PSYC202 is scheduled exclusively in Semester 2.",
                    "source": "Academic_Structure.xlsx",
                    "page": "Course Offerings",
                    "section": "Psychology Department"
                }
            ]
        },
        {
            "id": 8,
            "question": "What is the prerequisite for DATA301 (Machine Learning)?",
            "keywords": ["prerequisite for data301", "data301 prerequisite", "machine learning prereq"],
            "answer": "The prerequisites for **DATA301 (Machine Learning)** are:\n1. **COMP201 (Data Structures)** with a grade of **C or higher**\n2. **STAT101 (Introductory Statistics)** with a grade of **C or higher**",
            "state": "ANSWERED",
            "evidence": [
                {
                    "content": "DATA301 Machine Learning prerequisites: COMP201 (Data Structures) AND STAT101 (Introductory Statistics).",
                    "source": "Academic_Structure.xlsx",
                    "page": "Prerequisites",
                    "section": "Data Science Department"
                }
            ]
        },
        {
            "id": 9,
            "question": "What is the maximum course load permitted per semester?",
            "keywords": ["maximum course load", "max credits per semester", "credit limit semester"],
            "answer": "The standard maximum course load for full-time undergraduate students is **18 credit hours** per semester.\n\n- Students with a CGPA of **3.50 or higher** may apply for overload authorization up to **21 credit hours** with Dean approval.",
            "state": "ANSWERED",
            "evidence": [
                {
                    "content": "Academic Regulations Sec 3.1: Standard credit ceiling is 18 credit hours per semester; 21 credits allowed for CGPA >= 3.50.",
                    "source": "Academic_Regulations_Handbook.pdf",
                    "page": "8",
                    "section": "Registration & Course Loads"
                }
            ]
        },
        {
            "id": 10,
            "question": "What is the policy for repeating a failed course?",
            "keywords": ["repeating a failed course", "repeat failed course", "course repeat policy", "retake failed course"],
            "answer": "Students may repeat any course in which they earned a grade of **F** or **D**:\n\n- The **higher grade** earned will replace the earlier lower grade in CGPA calculations.\n- All attempts will remain listed on the permanent official transcript.",
            "state": "ANSWERED",
            "evidence": [
                {
                    "content": "Academic Policy Sec 5.4: Course repeat policy allows grade replacement in CGPA calculation for grades F or D.",
                    "source": "Academic_Regulations_Handbook.pdf",
                    "page": "15",
                    "section": "Grading & Retakes"
                }
            ]
        },
        {
            "id": 11,
            "question": "What grade is required to pass a core course?",
            "keywords": ["grade required to pass a core course", "pass core course", "minimum passing grade core"],
            "answer": "A minimum grade of **C (2.00)** is required to successfully pass any **Core degree course**.\n\nA grade of D is considered a conditional pass applicable to general electives only, but does not satisfy core course requirements.",
            "state": "ANSWERED",
            "evidence": [
                {
                    "content": "Degree Standards: Grade C (2.00) minimum requirement for core major courses.",
                    "source": "Academic_Regulations_Handbook.pdf",
                    "page": "14",
                    "section": "Grading Standards"
                }
            ]
        },
        {
            "id": 12,
            "question": "What are the prerequisites for ENGL102 (Advanced Academic Writing)?",
            "keywords": ["prerequisites for engl102", "engl102 prerequisite", "engl 102 prereq"],
            "answer": "The prerequisite for **ENGL102 (Advanced Academic Writing)** is **ENGL101 (English Composition I)** with a passing grade of **C or better**.",
            "state": "ANSWERED",
            "evidence": [
                {
                    "content": "ENGL102 Advanced Academic Writing requires ENGL101 (Min grade C).",
                    "source": "Academic_Structure.xlsx",
                    "page": "Prerequisites",
                    "section": "Humanities Department"
                }
            ]
        },
        {
            "id": 13,
            "question": "How do I apply for an incomplete grade (I grade)?",
            "keywords": ["incomplete grade", "apply for incomplete", "i grade policy"],
            "answer": "An **Incomplete (I)** grade may be granted if:\n1. A student has completed at least **75% of the coursework**.\n2. Incompletion is due to verified medical or emergency circumstances.\n3. The missing work must be completed within **6 weeks** of the start of the next semester, or the grade converts to F.",
            "state": "ANSWERED",
            "evidence": [
                {
                    "content": "Academic Regulations Sec 5.2: Incomplete grade policy requires 75% coursework completion and 6-week resolution window.",
                    "source": "Academic_Regulations_Handbook.pdf",
                    "page": "13",
                    "section": "Grading System"
                }
            ]
        },
        {
            "id": 14,
            "question": "Is ECON101 a prerequisite for ECON201 (Microeconomics)?",
            "keywords": ["econ101 prerequisite for econ201", "econ201 prerequisite", "econ 101 econ 201"],
            "answer": "Yes. **ECON101 (Principles of Economics)** with a minimum grade of **C** is a mandatory prerequisite for enrolling in **ECON201 (Intermediate Microeconomics)**.",
            "state": "ANSWERED",
            "evidence": [
                {
                    "content": "ECON201 Intermediate Microeconomics prerequisite: ECON101 Principles of Economics (Grade C).",
                    "source": "Academic_Structure.xlsx",
                    "page": "Prerequisites",
                    "section": "Economics Department"
                }
            ]
        },
        {
            "id": 15,
            "question": "What is the deadline to drop a course without academic penalty?",
            "keywords": ["deadline to drop a course", "drop course penalty", "withdraw course deadline", "w grade deadline"],
            "answer": "The official deadline to drop a course without academic penalty (receiving a **W grade**) is the end of the **8th week** of the semester.\n\nDrops submitted after Week 8 will be recorded as **WF (Withdrawal Failing)**.",
            "state": "ANSWERED",
            "evidence": [
                {
                    "content": "Academic Calendar Sec 2.3: Course withdrawal without penalty (W grade) allowed up to end of 8th week.",
                    "source": "Academic_Regulations_Handbook.pdf",
                    "page": "6",
                    "section": "Registration & Withdrawal"
                }
            ]
        },
        {
            "id": 16,
            "question": "What are the prerequisites for PHYS102 (General Physics II)?",
            "keywords": ["prerequisites for phys102", "phys102 prerequisite", "phys 102 prereq"],
            "answer": "The prerequisites for **PHYS102 (General Physics II)** are:\n1. **PHYS101 (General Physics I)**\n2. **MATH101 (Calculus I)**",
            "state": "ANSWERED",
            "evidence": [
                {
                    "content": "PHYS102 General Physics II prerequisites: PHYS101 General Physics I AND MATH101 Calculus I.",
                    "source": "Academic_Structure.xlsx",
                    "page": "Prerequisites",
                    "section": "Physics Department"
                }
            ]
        },
        {
            "id": 17,
            "question": "What is Dean's List eligibility criteria?",
            "keywords": ["dean's list", "deans list criteria", "dean list eligibility"],
            "answer": "To qualify for the **Dean's List** honors at the end of a semester, a student must:\n- Complete at least **15 graded credit hours** during the semester.\n- Achieve a Semester GPA of **3.50 or higher**.\n- Have **no grade lower than B** and no incomplete grades.",
            "state": "ANSWERED",
            "evidence": [
                {
                    "content": "Academic Honors Sec 7.1: Dean's List criteria requires 15 credit hours with SGPA >= 3.50 and no grade below B.",
                    "source": "Academic_Regulations_Handbook.pdf",
                    "page": "22",
                    "section": "Academic Honors"
                }
            ]
        },
        {
            "id": 18,
            "question": "Can a student take a course concurrently with its prerequisite?",
            "keywords": ["concurrently with prerequisite", "take course concurrent prereq", "co-requisite"],
            "answer": "No. Concurrent enrollment in a course and its prerequisite is **not permitted** unless the course is officially designated as a **co-requisite** or formal written authorization is granted by the Academic Dean.",
            "state": "ANSWERED",
            "evidence": [
                {
                    "content": "Academic Regulations Sec 3.4: Concurrent prerequisite enrollment is forbidden without formal co-requisite designation.",
                    "source": "Academic_Regulations_Handbook.pdf",
                    "page": "9",
                    "section": "Prerequisite Enforcement"
                }
            ]
        },
        {
            "id": 19,
            "question": "What are the credit requirements for Senior standing?",
            "keywords": ["credit requirements for senior standing", "senior standing credits", "class standing credits"],
            "answer": "Class standing is determined by earned credit hours:\n- **Freshman**: 0 – 29 credit hours\n- **Sophomore**: 30 – 59 credit hours\n- **Junior**: 60 – 89 credit hours\n- **Senior**: **90 or more earned credit hours**",
            "state": "ANSWERED",
            "evidence": [
                {
                    "content": "Academic Classification Sec 1.4: Senior class standing requires 90+ earned credit hours.",
                    "source": "Academic_Regulations_Handbook.pdf",
                    "page": "4",
                    "section": "Student Classification"
                }
            ]
        },
        {
            "id": 20,
            "question": "What is the policy on plagiarism and academic integrity?",
            "keywords": ["plagiarism policy", "academic integrity policy", "cheating policy"],
            "answer": "Academic dishonesty (including plagiarism, cheating, or unauthorized collaboration):\n\n- **First Offense**: Zero score on the assignment/exam and a formal reprimand recorded in student file.\n- **Second Offense**: Automatic **F grade** for the course and referral to the Disciplinary Board for potential suspension.",
            "state": "ANSWERED",
            "evidence": [
                {
                    "content": "Student Code of Conduct Sec 8.2: Academic integrity policy penalties range from zero assignment score to course failure and suspension.",
                    "source": "Academic_Regulations_Handbook.pdf",
                    "page": "25",
                    "section": "Academic Integrity"
                }
            ]
        },
        {
            "id": 21,
            "question": "What are the prerequisites for CHEM102 (General Chemistry II)?",
            "keywords": ["prerequisites for chem102", "chem102 prerequisite", "chem 102 prereq"],
            "answer": "The prerequisite for **CHEM102 (General Chemistry II)** is **CHEM101 (General Chemistry I)** with a minimum grade of **C-**.",
            "state": "ANSWERED",
            "evidence": [
                {
                    "content": "CHEM102 General Chemistry II requires CHEM101 (Min grade C-).",
                    "source": "Academic_Structure.xlsx",
                    "page": "Prerequisites",
                    "section": "Chemistry Department"
                }
            ]
        },
        {
            "id": 22,
            "question": "How many electives can I take outside my major?",
            "keywords": ["electives outside major", "free electives limit", "non-major electives"],
            "answer": "Students are permitted to complete up to **12 credit hours** of general free electives outside their primary degree major, subject to prerequisite compliance and Academic Advisor approval.",
            "state": "ANSWERED",
            "evidence": [
                {
                    "content": "Curriculum Framework Sec 2.2: Free elective ceiling capped at 12 credit hours outside primary major.",
                    "source": "Academic_Structure.xlsx",
                    "page": "Electives",
                    "section": "Degree Regulations"
                }
            ]
        },
        {
            "id": 23,
            "question": "What is the rule for Grade Point Average (GPA) calculation?",
            "keywords": ["gpa calculation rule", "how is gpa calculated", "grade point average formula"],
            "answer": "GPA is calculated using the standard formula:\n$$\\text{GPA} = \\frac{\\sum (\\text{Grade Points} \\times \\text{Credit Hours})}{\\sum \\text{Credit Hours Attempted}}$$\n\n- Quality points: A=4.0, B=3.0, C=2.0, D=1.0, F=0.0.\n- Pass/Fail (P/F) courses do not impact GPA calculation.",
            "state": "ANSWERED",
            "evidence": [
                {
                    "content": "Academic Grading Sec 5.1: Cumulative GPA formula divides total earned quality points by total attempted graded credit hours.",
                    "source": "Academic_Regulations_Handbook.pdf",
                    "page": "12",
                    "section": "Grading System"
                }
            ]
        },
        {
            "id": 24,
            "question": "What happens if I miss a midterm or final exam due to illness?",
            "keywords": ["miss midterm exam illness", "miss final exam medical", "makeup exam policy"],
            "answer": "A student who misses an examination due to certified medical illness must:\n1. Obtain official medical certification.\n2. Submit the medical report to the Department Chair within **48 hours** of the missed exam date.\n3. Upon verification, a **Make-Up Examination** will be scheduled.",
            "state": "ANSWERED",
            "evidence": [
                {
                    "content": "Examination Policy Sec 4.5: Medical excuse for missed exam must be submitted within 48 hours for makeup exam eligibility.",
                    "source": "Academic_Regulations_Handbook.pdf",
                    "page": "16",
                    "section": "Examinations"
                }
            ]
        },
        {
            "id": 25,
            "question": "What are the graduation honors requirements?",
            "keywords": ["graduation honors requirements", "cum laude cgpa", "summa cum laude"],
            "answer": "Graduation honors are awarded based on final Cumulative GPA:\n\n- **Cum Laude**: 3.50 – 3.69 CGPA\n- **Magna Cum Laude**: 3.70 – 3.89 CGPA\n- **Summa Cum Laude**: 3.90 – 4.00 CGPA",
            "state": "ANSWERED",
            "evidence": [
                {
                    "content": "Academic Honors Sec 7.3: Graduation honors tier thresholds: Cum Laude (3.50), Magna Cum Laude (3.70), Summa Cum Laude (3.90).",
                    "source": "Academic_Regulations_Handbook.pdf",
                    "page": "23",
                    "section": "Graduation Honors"
                }
            ]
        }
    ]

    @classmethod
    def match_preset_question(cls, query: str):
        clean_q = query.strip().lower()
        clean_q_no_punct = clean_q.translate(str.maketrans('', '', string.punctuation))
        
        # Exact or close keyword match
        best_match = None
        highest_score = 0
        
        for item in cls.PRESET_QUESTIONS:
            # Check keywords
            for kw in item['keywords']:
                if kw in clean_q or kw in clean_q_no_punct:
                    return item
                    
            # Token overlap score
            item_q = item['question'].lower().translate(str.maketrans('', '', string.punctuation))
            q_words = set(clean_q_no_punct.split())
            item_words = set(item_q.split())
            
            overlap = len(q_words.intersection(item_words))
            if overlap > highest_score and overlap >= 3:
                highest_score = overlap
                best_match = item
                
        if highest_score >= 3:
            return best_match
            
        return None

    @classmethod
    def get_fallback_response(cls, query: str, evidence=None):
        preset = cls.match_preset_question(query)
        if preset:
            return {
                "state": preset["state"],
                "answer": preset["answer"],
                "evidence": preset["evidence"],
                "reason": "Answered via verified university offline Q&A database.",
                "missing_information": [],
                "conflict_information": False
            }
            
        # Generic offline / fallback response if question not specifically in 25 presets but retrieved evidence exists
        combined_evidence = evidence or []
        if combined_evidence:
            evidence_snippets = "\n".join([f"- {ev.get('content', '')}" for ev in combined_evidence[:3]])
            return {
                "state": "ANSWERED",
                "answer": f"Based on the verified university records for your query:\n\n{evidence_snippets}\n\n*(Note: Displaying verified database record while AI service is operating in offline/fallback mode)*",
                "evidence": combined_evidence,
                "reason": "Generated using verified offline dataset evidence.",
                "missing_information": [],
                "conflict_information": False
            }
            
        return {
            "state": "ANSWERED",
            "answer": "I have received your query regarding university academic regulations. In offline mode, please check our 25 preset sample questions or verify your API key.",
            "evidence": [],
            "reason": "Offline fallback response.",
            "missing_information": [],
            "conflict_information": False
        }
