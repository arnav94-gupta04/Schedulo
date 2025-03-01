import json
import time
from dotenv import load_dotenv
from groq import Groq
from database import ScheduloDatabase

load_dotenv()

class ChatbotService:
    def __init__(self, db=None, client=None):
        self.db = db or ScheduloDatabase()
        self.client = client or Groq()

    def build_extraction_prompt(self, input_text):
        prompt = f"""
You are an extractor for the Schedulo scheduling system. Given the following unstructured input text related to university scheduling data, extract and output a JSON object with exactly the following keys:
- "action": a string that is one of "create", "read", "update", "delete". This indicates the intended operation.
- "target": a string that is one of "academic_years", "divisions", "batches", "subjects", "teachers", "venues", or "all". This indicates which part of the database the operation applies to.
- "academic_years": an array of strings representing academic years (e.g., ["FE", "SE", "TE", "BE"]). Use an empty array if not applicable.
- "divisions": an array of objects, each with keys "year" and "division". Use an empty array if not applicable.
- "batches": an array of objects, each with keys "division" and "batch". Use an empty array if not applicable.
- "subjects": an array of objects, each with keys "code", "name", "year", "type", and "min_hours_per_week". Use an empty array if not applicable.
- "teachers": an array of objects, each with keys "code", "name", "max_workload", and "subjects" (an array of subject codes). Use an empty array if not applicable.
- "venues": an array of objects, each with keys "name" and "type". Use an empty array if not applicable.

For any field not applicable to the specified action and target, output null or an empty array as appropriate. Do not include any extra commentary or keys.

Input text:
{input_text}

Output:
"""
        return prompt.strip()

    def extract_information(self, input_text):
        extraction_prompt = self.build_extraction_prompt(input_text)
        completion = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": extraction_prompt}],
            temperature=0,
            max_completion_tokens=1024,
            top_p=1,
            stream=True,
            stop=None
        )
        response_text = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                response_text += chunk.choices[0].delta.content
                time.sleep(0.02)
        response_text = response_text.strip().replace('`', '').strip()
        try:
            info = json.loads(response_text)
            return info
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {str(e)}\nResponse was:\n{repr(response_text)}")
            try:
                response_text = response_text.encode().decode('utf-8-sig')
                response_text = response_text.replace('\r\n', '\n')
                info = json.loads(response_text)
                return info
            except Exception as e:
                print(f"Failed to parse JSON even after cleanup: {str(e)}")
                return None

    def prompt_for_missing(self, field_name, prompt_text):
        value = input(f"{prompt_text} (Enter {field_name}): ")
        return value

    def process_create(self, info):
        # Create academic years
        academic_years = info.get("academic_years", [])
        for year in academic_years:
            if year is None:
                year = self.prompt_for_missing("academic year", "Please provide an academic year")
            self.db.insert_academic_year(year)
        
        # Create divisions
        divisions = info.get("divisions", [])
        for d in divisions:
            year = d.get("year")
            division = d.get("division")
            if not year:
                year = self.prompt_for_missing("year", "Please provide the year for the division")
            if not division:
                division = self.prompt_for_missing("division", "Please provide the division name")
            self.db.insert_division(year, division)
        
        # Create batches
        batches = info.get("batches", [])
        for b in batches:
            division = b.get("division")
            batch = b.get("batch")
            if not division:
                division = self.prompt_for_missing("division", "Please provide the division for the batch")
            if not batch:
                batch = self.prompt_for_missing("batch", "Please provide the batch name")
            self.db.insert_batch(division, batch)
        
        # Create subjects
        subjects = info.get("subjects", [])
        for s in subjects:
            code = s.get("code")
            name = s.get("name")
            year = s.get("year")
            type_ = s.get("type")
            min_hours = s.get("min_hours_per_week")
            if not code:
                code = self.prompt_for_missing("code", "Please provide the subject code")
            if not name:
                name = self.prompt_for_missing("name", "Please provide the subject name")
            if not year:
                year = self.prompt_for_missing("year", "Please provide the academic year for the subject")
            if not type_:
                type_ = self.prompt_for_missing("type", "Please provide the subject type")
            try:
                min_hours = int(min_hours) if min_hours is not None else int(self.prompt_for_missing("min_hours_per_week", "Please provide minimum hours per week for the subject"))
            except:
                min_hours = int(self.prompt_for_missing("min_hours_per_week", "Invalid value. Please provide minimum hours per week for the subject"))
            self.db.insert_subject(code, name, year, type_, min_hours)
        
        # Create teachers and map subjects
        teachers = info.get("teachers", [])
        for t in teachers:
            code = t.get("code")
            name = t.get("name")
            max_workload = t.get("max_workload")
            if not code:
                code = self.prompt_for_missing("code", "Please provide the teacher code")
            if not name:
                name = self.prompt_for_missing("name", "Please provide the teacher name")
            try:
                max_workload = int(max_workload) if max_workload is not None else int(self.prompt_for_missing("max_workload", "Please provide the teacher's maximum workload"))
            except:
                max_workload = int(self.prompt_for_missing("max_workload", "Invalid value. Please provide the teacher's maximum workload"))
            self.db.insert_teacher(code, name, max_workload)
            subjects_list = t.get("subjects", [])
            if not subjects_list:
                subjects_input = input(f"Please provide subject codes for teacher {code} (comma-separated): ")
                subjects_list = [sub.strip() for sub in subjects_input.split(",") if sub.strip()]
            for subj in subjects_list:
                self.db.insert_teacher_subject(code, subj)
        
        # Create venues
        venues = info.get("venues", [])
        for v in venues:
            name = v.get("name")
            type_ = v.get("type")
            if not name:
                name = self.prompt_for_missing("name", "Please provide the venue name")
            if not type_:
                type_ = self.prompt_for_missing("type", "Please provide the venue type")
            self.db.insert_venue(name, type_)
        
        ack = (
            "Created records successfully:\n"
            f"Academic Years: {len(academic_years)}, Divisions: {len(divisions)}, Batches: {len(batches)}, "
            f"Subjects: {len(subjects)}, Teachers: {len(teachers)}, Venues: {len(venues)}."
        )
        return ack

    def process_read(self, info):
        target = info.get("target", "all")
        results = {}
        if target in ["academic_years", "all"]:
            results["academic_years"] = [dict(row) for row in self.db.get_academic_years()]
        if target in ["divisions", "all"]:
            results["divisions"] = [dict(row) for row in self.db.get_divisions()]
        if target in ["batches", "all"]:
            results["batches"] = [dict(row) for row in self.db.get_batches()]
        if target in ["subjects", "all"]:
            results["subjects"] = [dict(row) for row in self.db.get_subjects()]
        if target in ["teachers", "all"]:
            results["teachers"] = [dict(row) for row in self.db.get_teachers()]
        if target in ["venues", "all"]:
            results["venues"] = [dict(row) for row in self.db.get_venues()]
        return json.dumps(results, indent=4)

    def process_update(self, info):
        target = info.get("target")
        if target == "subjects":
            subjects = info.get("subjects", [])
            for s in subjects:
                code = s.get("code")
                if not code:
                    code = self.prompt_for_missing("code", "Please provide the subject code to update")
                # Find existing subject
                existing = None
                for row in self.db.get_subjects():
                    if row["code"] == code:
                        existing = row
                        break
                if not existing:
                    print(f"No subject found with code {code}. Skipping update for this record.")
                    continue
                # Use new values if provided; otherwise keep existing ones
                name = s.get("name") or existing["name"]
                year = s.get("year") or existing["year"]
                type_ = s.get("type") or existing["type"]
                try:
                    min_hours = int(s.get("min_hours_per_week")) if s.get("min_hours_per_week") is not None else existing["min_hours_per_week"]
                except:
                    min_hours = existing["min_hours_per_week"]
                self.db.update_subject(code, name, year, type_, min_hours)
            return "Subjects updated successfully."
        return "Update operation for the specified target is not implemented yet."

    def process_delete(self, info):
        target = info.get("target")
        if target == "subjects":
            subjects = info.get("subjects", [])
            for s in subjects:
                code = s.get("code")
                if not code:
                    code = self.prompt_for_missing("code", "Please provide the subject code to delete")
                # Verify the subject exists
                existing = None
                for row in self.db.get_subjects():
                    if row["code"] == code:
                        existing = row
                        break
                if not existing:
                    print(f"No subject found with code {code}. Skipping deletion for this record.")
                    continue
                self.db.delete_subject(code)
            return "Subjects deleted successfully."
        return "Delete operation for the specified target is not implemented yet."

    def conversation_loop(self):
        print("Welcome to Schedulo Chatbot. You can create, read, update, or delete scheduling data.")
        print("Type 'exit' to quit.\n")
        while True:
            user_input = input("Enter your command: ")
            if user_input.lower() in ["exit", "quit"]:
                print("Exiting Schedulo Chatbot.")
                break
            info = self.extract_information(user_input)
            if info is None:
                print("Could not extract valid information from your input. Please try again.")
                continue
            
            action = info.get("action", "create").lower()
            if action == "create":
                result = self.process_create(info)
            elif action == "read":
                result = self.process_read(info)
            elif action == "update":
                result = self.process_update(info)
            elif action == "delete":
                result = self.process_delete(info)
            else:
                result = "Unknown action specified. Please specify create, read, update, or delete."
            
            print(result)
            print("\n")  # Spacing between commands

if __name__ == "__main__":
    chatbot_service = ChatbotService()
    chatbot_service.conversation_loop()
