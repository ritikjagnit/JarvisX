import json

class TaskStep:
    """
    Represents an individual step in an Autonomous Task Plan.
    """
    def __init__(self, step_number, title, action_type, payload=None, requires_confirmation=False):
        self.step_number = step_number
        self.title = title
        self.action_type = action_type # desktop, browser, document, coding, booking, utility
        self.payload = payload or {}
        self.requires_confirmation = requires_confirmation
        self.status = "PENDING" # PENDING, EXECUTING, COMPLETED, FAILED
        self.result = None

    def to_dict(self):
        return {
            "step_number": self.step_number,
            "title": self.title,
            "action_type": self.action_type,
            "payload": self.payload,
            "requires_confirmation": self.requires_confirmation,
            "status": self.status,
            "result": self.result
        }

class TaskPlan:
    """
    Holds the complete goal and ordered list of TaskStep objects.
    """
    def __init__(self, goal, steps=None):
        self.goal = goal
        self.steps = steps or []

    def add_step(self, title, action_type, payload=None, requires_confirmation=False):
        step_num = len(self.steps) + 1
        step = TaskStep(step_num, title, action_type, payload, requires_confirmation)
        self.steps.append(step)
        return step

    def to_dict(self):
        return {
            "goal": self.goal,
            "total_steps": len(self.steps),
            "steps": [s.to_dict() for s in self.steps]
        }

class TaskPlanner:
    """
    Decomposes natural language goals into structured TaskPlan step sequences.
    """
    def __init__(self):
        pass

    def plan_goal(self, goal):
        goal_lower = goal.lower().strip()
        plan = TaskPlan(goal)

        # 1. PowerPoint Presentation Workflow
        if "presentation" in goal_lower or "powerpoint" in goal_lower or "ppt" in goal_lower:
            topic = goal.replace("Create", "").replace("create", "").replace("presentation", "").replace("on", "").replace("powerpoint", "").strip()
            topic = topic or "Artificial Intelligence"
            
            plan.add_step("Generate presentation content", "desktop", {"action": "generate_content", "topic": topic})
            plan.add_step("Generate slide titles", "desktop", {"action": "generate_titles", "topic": topic})
            plan.add_step("Create PowerPoint", "desktop", {"action": "create_pptx", "topic": topic, "file_name": f"{topic.replace(' ', '_')}_Presentation.pptx"})
            plan.add_step("Insert images and formatting", "desktop", {"action": "format_pptx"})
            plan.add_step("Save file in Documents", "desktop", {"action": "save_pptx"})
            plan.add_step("Open presentation", "desktop", {"action": "launch_app", "app_name": "POWERPNT.EXE"})

        # 2. Hotel / Flight / Event Booking Workflow
        elif any(k in goal_lower for k in ["hotel", "flight", "event", "movie ticket", "train", "book "]):
            booking_type = "hotel" if "hotel" in goal_lower else ("flight" if "flight" in goal_lower else "event")
            plan.add_step(f"Search for {booking_type} options", "booking", {"action": "search", "type": booking_type, "query": goal})
            plan.add_step("Show available options to user", "booking", {"action": "show_options"})
            plan.add_step("Fill booking details", "booking", {"action": "fill_details"})
            plan.add_step("Reach payment page and pause", "booking", {"action": "payment_pause"}, requires_confirmation=True)

        # 3. Download Folder Organization Workflow
        elif "organize" in goal_lower and "download" in goal_lower:
            plan.add_step("Scan Downloads directory", "desktop", {"action": "scan_downloads"})
            plan.add_step("Categorize files by extension", "desktop", {"action": "categorize_files"})
            plan.add_step("Move files to organized subfolders", "desktop", {"action": "organize_downloads"})

        # 4. Excel Report Creation Workflow
        elif "excel" in goal_lower or "spreadsheet" in goal_lower or "report" in goal_lower:
            report_name = "System_Report.xlsx"
            plan.add_step("Gather report data", "desktop", {"action": "gather_report_data"})
            plan.add_step("Format headers and rows", "desktop", {"action": "format_excel"})
            plan.add_step("Create Excel file in Documents", "desktop", {"action": "create_excel", "file_name": report_name})

        # 5. Meeting Notes Workflow
        elif "meeting" in goal_lower or "notes" in goal_lower:
            plan.add_step("Launch Meeting Notes Generator", "workflow", {"action": "document", "type": "meeting"})

        # 6. Document Intelligence Workflows (PDF, Resume, Invoice, Screenshot)
        elif any(k in goal_lower for k in ["pdf", "resume", "ocr", "invoice", "prescription", "screenshot"]):
            doc_type = "pdf" if "pdf" in goal_lower else ("resume" if "resume" in goal_lower else "ocr")
            plan.add_step(f"Execute Document Intelligence for {doc_type}", "workflow", {"action": "document", "type": doc_type})

        # 7. Coding Assistant Workflows (VS Code, error, bug)
        elif any(k in goal_lower for k in ["code", "bug", "error", "explain this", "react", "vs code"]):
            plan.add_step("Analyze workspace code and find bugs", "workflow", {"action": "coding", "sub_action": "explain"})

        # 8. Web Search & Browser Navigation
        elif any(k in goal_lower for k in ["search", "find", "open web", "weather", "map", "job", "internship", "college", "scheme"]):
            plan.add_step(f"Search web for '{goal}'", "browser", {"action": "search", "query": goal})

        # 9. Generic File Deletion / Confirmation Flow
        elif "delete" in goal_lower or "remove" in goal_lower:
            plan.add_step("Ask for user confirmation before deletion", "desktop", {"action": "confirm_delete", "target": goal}, requires_confirmation=True)
            plan.add_step("Perform deletion", "desktop", {"action": "delete_file", "target": goal})

        # 10. Fallback Single-Step Execution
        else:
            plan.add_step(f"Execute goal: '{goal}'", "utility", {"action": "generic", "query": goal})

        print(f"[TASK PLANNER] Generated plan with {len(plan.steps)} step(s) for goal: '{goal}'")
        return plan
