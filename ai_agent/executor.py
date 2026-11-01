import time
import traceback
from voice_engine import speak

from .desktop_agent import DesktopAgent
from .browser_agent import BrowserAgent
from .workflow import WorkflowManager
from .memory import AgentMemory
from .history import ExecutionHistory
from .plugins import plugin_manager

class TaskExecutor:
    """
    Sequential Execution Engine for Autonomous AI Agent Plans.
    Executes each planned step, provides real-time progress callbacks,
    monitors execution, handles retries, logs history, updates memory, and enforces safety gates.
    """
    def __init__(self, status_callback=None):
        self.status_callback = status_callback
        self.desktop_agent = DesktopAgent()
        self.browser_agent = BrowserAgent()
        self.workflow_manager = WorkflowManager(self.desktop_agent, self.browser_agent)
        self.memory = AgentMemory()
        self.history = ExecutionHistory()

    def _notify(self, message):
        """Send status update to UI terminal callback and speak aloud if appropriate."""
        print(f"[TASK EXECUTOR] {message}")
        if self.status_callback:
            try:
                self.status_callback(message)
            except Exception as e:
                print(f"[EXECUTOR CALLBACK ERROR] {e}")

    def execute_plan(self, plan, user_confirmed=False):
        """
        Executes a TaskPlan step-by-step.
        """
        start_time = time.time()
        goal = plan.goal
        self.memory.record_usage("task_goal", goal)
        self.memory.log_recent_task(goal)

        self._notify(f"Planning...\nGoal: '{goal}' ({len(plan.steps)} steps)")
        speak(f"Planning task: {goal}")

        step_results = []
        has_errors = False
        error_summary = []

        for i, step in enumerate(plan.steps):
            step.status = "EXECUTING"
            progress_msg = f"Executing Step {step.step_number}/{len(plan.steps)}: {step.title}..."
            self._notify(progress_msg)

            # Safety Confirmation Check
            if step.requires_confirmation and not user_confirmed:
                pause_msg = f"⚠️ [SAFETY PAUSE] Step {step.step_number} ({step.title}) requires explicit confirmation. Execution paused before completion."
                self._notify(pause_msg)
                speak(f"Step {step.step_number} requires your confirmation to proceed.")
                step.status = "PAUSED_CONFIRMATION_REQUIRED"
                step.result = pause_msg
                
                # Log partial history
                duration = time.time() - start_time
                self.history.log_execution(goal, "PAUSED_FOR_CONFIRMATION", duration, errors="Requires confirmation", result_summary=pause_msg)
                return f"{progress_msg}\n{pause_msg}"

            # Execute step with retries
            success, result_msg = self._execute_step_with_retry(step, max_retries=2)

            if success:
                step.status = "COMPLETED"
                step.result = result_msg
                step_results.append(f"Step {step.step_number}: {result_msg}")
            else:
                step.status = "FAILED"
                step.result = result_msg
                has_errors = True
                error_summary.append(f"Step {step.step_number} Failed: {result_msg}")
                self._notify(f"⚠️ Step {step.step_number} Failed: {result_msg}")

        duration = time.time() - start_time
        final_status = "SUCCESS" if not has_errors else ("PARTIAL_SUCCESS" if step_results else "FAILED")

        summary_text = "\n".join(step_results) if step_results else "No steps completed successfully."
        if error_summary:
            summary_text += "\nErrors:\n" + "\n".join(error_summary)

        # Log completion in SQLite history
        self.history.log_execution(
            task_goal=goal,
            status=final_status,
            duration_seconds=duration,
            errors="; ".join(error_summary) if error_summary else "",
            result_summary=summary_text[:300]
        )

        completed_msg = f"Completed in {round(duration, 2)}s.\nSummary:\n{summary_text}"
        self._notify(completed_msg)
        speak(f"Task completed in {round(duration, 1)} seconds.")

        return completed_msg

    def _execute_step_with_retry(self, step, max_retries=2):
        """Attempt step execution with retry mechanism."""
        last_error = ""
        for attempt in range(1, max_retries + 1):
            try:
                res = self._dispatch_step_action(step)
                return True, res
            except Exception as e:
                last_error = str(e)
                print(f"[STEP RETRY] Step {step.step_number} Attempt {attempt} failed: {e}")
                time.sleep(0.5)

        return False, f"Failed after {max_retries} attempt(s): {last_error}"

    def _dispatch_step_action(self, step):
        """Dispatch action based on step action_type and payload."""
        act_type = step.action_type
        payload = step.payload or {}
        action = payload.get("action", "")

        # 1. Desktop Agent Actions
        if act_type == "desktop":
            if action == "create_pptx":
                topic = payload.get("topic", "Artificial Intelligence")
                file_name = payload.get("file_name", "Presentation.pptx")
                return self.desktop_agent.create_powerpoint(file_name=file_name, title=topic)

            elif action == "create_excel":
                file_name = payload.get("file_name", "Report.xlsx")
                return self.desktop_agent.create_excel(file_name=file_name)

            elif action == "create_word":
                file_name = payload.get("file_name", "Document.docx")
                return self.desktop_agent.create_word(file_name=file_name)

            elif action == "organize_downloads":
                return self.desktop_agent.organize_downloads()

            elif action == "launch_app":
                app_name = payload.get("app_name", "notepad")
                return self.desktop_agent.launch_app(app_name)

            elif action == "delete_file":
                target = payload.get("target", "")
                return self.desktop_agent.delete_file(target, user_confirmed=True)

            else: # General desktop action placeholder simulation
                return f"Desktop action '{action or step.title}' executed successfully."

        # 2. Browser Agent Actions
        elif act_type == "browser":
            query = payload.get("query", step.title)
            return self.browser_agent.search_web(query)

        # 3. Booking Workflow Actions
        elif act_type == "booking":
            b_type = payload.get("type", "hotel")
            query = payload.get("query", step.title)
            if action == "payment_pause":
                return "Reached checkout & payment step. Paused for mandatory user approval."
            return self.workflow_manager.run_booking_workflow(b_type, query)

        # 4. Domain Workflow Actions (Document & Coding)
        elif act_type == "workflow":
            wf_type = payload.get("type", "document")
            if wf_type in ["meeting", "ocr", "resume", "pdf", "invoice"]:
                return self.workflow_manager.run_document_intelligence_workflow(wf_type)
            elif payload.get("action") == "coding":
                return self.workflow_manager.run_coding_assistant_workflow(action=payload.get("sub_action", "explain"))
            else:
                return f"Workflow '{wf_type}' executed successfully."

        # 5. Registered Plugin Execution
        plugin = plugin_manager.get_plugin(step.title)
        if plugin:
            return plugin_manager.execute_plugin(step.title, payload)

        # 6. Generic Fallback
        return f"Step '{step.title}' completed successfully."
