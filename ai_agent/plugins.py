import inspect

class PluginManager:
    """
    Extensible Plugin System for the Autonomous AI Agent.
    Allows registering custom tool plugins dynamically without modifying core agent code.
    """
    def __init__(self):
        self._plugins = {}

    def register_plugin(self, name, handler_func, description="", category="general"):
        """Register a custom tool plugin function."""
        if not callable(handler_func):
            raise ValueError(f"Plugin handler for '{name}' must be callable.")
        
        self._plugins[name.lower()] = {
            "name": name,
            "func": handler_func,
            "description": description,
            "category": category
        }
        print(f"[PLUGIN REGISTERED] '{name}' ({category}): {description}")

    def unregister_plugin(self, name):
        """Unregister a plugin by name."""
        key = name.lower()
        if key in self._plugins:
            del self._plugins[key]
            print(f"[PLUGIN UNREGISTERED] '{name}'")

    def get_plugin(self, name):
        """Get plugin object by name."""
        return self._plugins.get(name.lower())

    def execute_plugin(self, name, *args, **kwargs):
        """Execute a registered plugin by name."""
        plugin = self.get_plugin(name)
        if not plugin:
            raise KeyError(f"Plugin '{name}' is not registered.")
        
        print(f"[PLUGIN EXECUTE] Running plugin '{name}'...")
        return plugin["func"](*args, **kwargs)

    def list_plugins(self):
        """List metadata of all registered plugins."""
        return [
            {
                "name": p["name"],
                "description": p["description"],
                "category": p["category"]
            }
            for p in self._plugins.values()
        ]

# Global singleton plugin manager instance
plugin_manager = PluginManager()
