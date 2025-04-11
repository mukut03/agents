# agents/googlemaps/googlemaps_agent.py

from agents.core_agent import Agent
from agents.ollama_client import OllamaClient
from agents.googlemaps.tools import TOOL_REGISTRY as GOOGLEMAPS_TOOLS
from agents.googlemaps.config.agent_behavior_spec import AGENT_BEHAVIOR_SPEC
from agents.googlemaps.config.system_prompt import SYSTEM_PROMPT
from agents.googlemaps.config.formatting import format_behavior_spec

import re
import json

class GoogleMapsAgent(Agent):
    """
    A specialized agent for working with geospatial queries and routing tasks.
    Inherits from the base Agent and injects Google Maps-related tools.
    """

    def __init__(self, model="llama3.2:latest"):
        super().__init__(model=model)
        self.client = OllamaClient(model=model)

        # Register all Google Maps-related tools
        for name, fn in GOOGLEMAPS_TOOLS.items():
            self.register_tool(name, fn)

        # Store behavior and prompt
        self.behavior_spec = AGENT_BEHAVIOR_SPEC
        self.system_prompt = SYSTEM_PROMPT + format_behavior_spec(AGENT_BEHAVIOR_SPEC)

    def extract_action(self, response_text):
        """
        Extract a structured tool call from the model's response.
        Fallbacks to returning the text as an answer.
        """
        self.log("Extracting action block from response")
        match = re.search(r"<action>(.*?)</action>", response_text, re.DOTALL)
        if not match:
            self.log("No <action> block found in response")
            return {
                "tool": "answer",
                "tool_input": response_text.strip(),
                "reasoning": "No <action> block found."
            }

        try:
            action = json.loads(match.group(1).strip())
            self.log("Parsed action:", action)
            return action
        except json.JSONDecodeError:
            self.log("Failed to parse JSON from <action> block")
            return {
                "tool": "answer",
                "tool_input": response_text.strip(),
                "reasoning": "Malformed <action> JSON."
            }

    def execute_action(self, action):
        """
        Executes a tool based on the parsed action.
        Also handles memory injection and summarizes the result using behavior spec.
        """
        tool = action.get("tool", "answer")
        tool_input = action.get("tool_input", {})
        reasoning = action.get("reasoning", "")

        self.log(f"Executing action: tool={tool}, reasoning={reasoning}")

        tool_input = self.inject_memory_if_missing(tool, tool_input)
        func = self.tools.get(tool)
        behavior = self.behavior_spec.get(tool)

        try:
            result = func(tool_input)
        except Exception as e:
            result = {"error": str(e)}

        self.after_tool(tool, result)

        summary = (
            behavior["summarize"](result)
            if behavior and "summarize" in behavior
            else str(result)
        )

        self.log(f"Final summarized result for tool '{tool}': {summary}")
        return f"Tool: {tool}\nReasoning: {reasoning}\nResult: {summary}"

    def process_query(self, query, stream=False):
        """
        Process a user query through the LLM and perform any tool actions.
        """
        if not self.client or not self.client.is_available():
            return "Ollama is not running. Please start the Ollama server."

        self.add_message("user", query)
        messages = [{"role": "system", "content": self.system_prompt}] + self.conversation_history

        if stream:
            full_response = ""
            print("Thinking", end="", flush=True)
            for chunk in self.client.stream_query(query, system_prompt=self.system_prompt):
                full_response += chunk
                print(".", end="", flush=True)
            print()
            response_text = full_response
        else:
            response = self.client.chat(messages)
            response_text = response.get("message", {}).get("content", "")

        self.log("Raw LLM response:", response_text[:500])

        action = self.extract_action(response_text)
        result = self.execute_action(action)
        self.add_message("assistant", result)
        return result

if __name__ == "__main__":
    agent = GoogleMapsAgent()
    agent.run_interactive()
