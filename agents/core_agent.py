from abc import ABC, abstractmethod

class Agent(ABC):
    def __init__(self, model="llama2"):
        self.model = model
        self.client = None
        self.tools = {}
        self.memory = {}
        self.conversation_history = []
        self.system_prompt = ""
        self.debug = True  # Toggle for logging

    def log(self, *args):
        if self.debug:
            print("[agent]", *args)

    def add_message(self, role, content):
        self.log(f"Adding message - role: {role}, content: {content[:100]}")
        self.conversation_history.append({"role": role, "content": content})
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]

    def register_tool(self, name, func):
        self.log(f"Registering tool: {name}")
        self.tools[name] = func

    def before_tool(self, tool, input):
        self.log(f"Preparing to call tool: {tool}")
        self.log(f"Tool input: [hidden for brevity]")

    def after_tool(self, tool, output):
        self.log(f"Finished tool: {tool}")
        self.log(f"Output: [hidden for brevity]")
        if tool == "get_route" and isinstance(output, dict):
            if "polyline" in output:
                self.memory["encoded_polyline"] = output["polyline"]
                self.log("Stored encoded_polyline in memory")
            if "polyline_coords" in output:
                self.memory["polyline_coords"] = output["polyline_coords"]
                self.log("Stored polyline_coords in memory")
        elif tool == "sample_polyline" and isinstance(output, list):
            self.memory["polyline_coords"] = output
            self.log("Updated polyline_coords from sampled polyline")
        elif tool == "get_places" and isinstance(output, list):
            self.memory["places"] = output
            self.log("Stored places in memory")
        elif tool == "get_natural_features" and isinstance(output, list):
            self.memory["features"] = output
            self.log("Stored features in memory")

    def extract_action(self, response_text):
        return {
            "tool": "answer",
            "tool_input": response_text,
            "reasoning": "No action format implemented."
        }

    def inject_memory_if_missing(self, tool_name, tool_input):
        tool_input = tool_input or {}

        if tool_name in ["sample_polyline"] and "encoded_polyline" not in tool_input:
            if "encoded_polyline" in self.memory:
                tool_input["encoded_polyline"] = self.memory["encoded_polyline"]
                self.log(f"Injected encoded_polyline into {tool_name}")

        if tool_name in ["get_places", "get_natural_features", "render_map"] and "polyline_coords" not in tool_input:
            if "polyline_coords" in self.memory:
                tool_input["polyline_coords"] = self.memory["polyline_coords"]
                self.log(f"Injected polyline_coords into {tool_name}")

        if tool_name == "render_map":
            if "places_path" not in tool_input and "places" in self.memory:
                tool_input["places_path"] = "places_along_route.json"
                self.log("Injected places_path into render_map")
            if "features_path" not in tool_input and "features" in self.memory:
                tool_input["features_path"] = "natural_features_along_route.json"
                self.log("Injected features_path into render_map")

        return tool_input

    def execute_action(self, action):
        tool = action.get("tool", "answer")
        tool_input = action.get("tool_input", {})
        reasoning = action.get("reasoning", "")

        self.log(f"Executing action for tool: {tool}")
        tool_input = self.inject_memory_if_missing(tool, tool_input)

        self.before_tool(tool, tool_input)
        func = self.tools.get(tool, lambda x: x)
        try:
            result = func(tool_input)
        except Exception as e:
            result = f"Tool execution error: {e}"
        self.after_tool(tool, result)
        return f"Tool: {tool}\nReasoning: {reasoning}\nResult: [output hidden]"

    @abstractmethod
    def process_query(self, query, stream=False):
        pass

    def run_interactive(self):
        print("Agent ready. Type 'exit' to quit.")
        if not self.client or not self.client.is_available():
            print("LLM client not available.")
            return
        print(f"Using model: {self.model}")
        while True:
            query = input("\nYou: ")
            if query.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
            print("\nAgent:", self.process_query(query, stream=True))
