"""
AI Agent Package for Jarvis Autonomous System.
Provides end-to-end goal understanding, step planning, execution, desktop/browser automation,
document intelligence, memory persistence, execution history logging, and plugin management.
"""

from .planner import TaskPlanner, TaskPlan, TaskStep
from .executor import TaskExecutor
from .desktop_agent import DesktopAgent
from .browser_agent import BrowserAgent
from .workflow import WorkflowManager
from .memory import AgentMemory
from .history import ExecutionHistory
from .plugins import plugin_manager, PluginManager

class AutonomousAgent:
    """
    Unified Autonomous AI Agent Interface.
    Integrates Planner, Executor, Memory, History, Desktop/Browser Automations, Workflows & Plugins.
    """
    def __init__(self, status_callback=None):
        self.planner = TaskPlanner()
        self.executor = TaskExecutor(status_callback=status_callback)
        self.memory = AgentMemory()
        self.history = ExecutionHistory()
        self.desktop = self.executor.desktop_agent
        self.browser = self.executor.browser_agent
        self.workflow = self.executor.workflow_manager
        self.plugins = plugin_manager

    def run_goal(self, goal_text, user_confirmed=False):
        """
        Main Entry Point: Accepts natural language goal, generates plan,
        executes steps sequentially, logs history, and returns execution summary.
        """
        plan = self.planner.plan_goal(goal_text)
        return self.executor.execute_plan(plan, user_confirmed=user_confirmed)

    def get_history(self, limit=20):
        """Get recent execution logs."""
        return self.history.get_recent_history(limit=limit)

    def get_preferences(self):
        """Get stored long-term preferences."""
        return self.memory.get_all_preferences()

def run_agent_task(goal_text, status_callback=None, user_confirmed=False):
    """Convenience helper function to instantiate and run an autonomous goal."""
    agent = AutonomousAgent(status_callback=status_callback)
    return agent.run_goal(goal_text, user_confirmed=user_confirmed)
