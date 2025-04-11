import re
import json
from agents.core_agent import Agent
from agents.ollama_client import OllamaClient
from agents.googlemaps.tools import TOOL_REGISTRY as GOOGLEMAPS_TOOLS
from agents.googlemaps.config.agent_behavior_spec import AGENT_BEHAVIOR_SPEC
from agents.googlemaps.config.system_prompt import SYSTEM_PROMPT
from agents.googlemaps.config.formatting import format_behavior_spec

class GoogleMapsAgent(Agent):
    """
    A specialized geospatial agent that:
      - Generates routes using the Google Maps API.
      - Renders HTML maps.
      - Queries places and natural features along a route.
      - Answers follow-up questions using stored context.
    
    This agent uses an iterative reasoning loop (Action–Observation–Thought) to
    determine and execute multiple tool calls until a final answer is reached.
    
    The design is inspired by industry-standard architectures (LangChain, ReAct, OpenAI Function Calling)
    while retaining full control over all implementation layers.
    """
    def __init__(self, model="llama3.2:latest"):
        super().__init__(model=model)
        self.client = OllamaClient(model=model)
        # Register tools from the registry
        for name, fn in GOOGLEMAPS_TOOLS.items():
            self.register_tool(name, fn)
        # Load behavior spec and system prompt with formatted tool info.
        self.behavior_spec = AGENT_BEHAVIOR_SPEC
        self.system_prompt = SYSTEM_PROMPT + format_behavior_spec(AGENT_BEHAVIOR_SPEC)

    def extract_action(self, response_text):
        """
        Extract a structured tool call action from the response text.
        If no <action> block is found, the response is interpreted as a direct answer.
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

    def process_query(self, query, stream=False):
        """
        Process a user query using a multi-step loop:
          1. Add the user query to memory.
          2. Build the conversation context (system prompt + message history).
          3. Query the LLM.
          4. If the response includes an action (a tool call), execute the tool,
             update memory with the summarized result, and re-query with the new context.
          5. Loop until the LLM returns a final answer (no tool action needed).
        """
        if not self.client or not self.client.is_available():
            return "Ollama is not running. Please start the Ollama server."

        # Add the user query
        self.add_message("user", query)
        # Build context for the LLM call
        messages = [{"role": "system", "content": self.system_prompt}] + self.memory.conversation

        # First LLM call
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
            # For our agent, we assume the response is in the field "message" -> "content"
            response_text = response.get("message", {}).get("content", "")

        self.log("Raw LLM response:", response_text[:500])
        action = self.extract_action(response_text)

        iterations = 0
        MAX_ITERATIONS = 5  # Prevent infinite loops
        # Loop until a final answer is reached
        while action["tool"] != "answer" and iterations < MAX_ITERATIONS:
            # Execute the tool specified by the action and update conversation with the result.
            result_str = self.execute_action(action)
            self.add_message("assistant", f"Observation: {result_str}")
            # Rebuild the context including the latest observation
            messages = [{"role": "system", "content": self.system_prompt}] + self.memory.conversation
            
            # Query the LLM with the updated context
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

            self.log("LLM response after tool execution:", response_text[:500])
            action = self.extract_action(response_text)
            iterations += 1

        # Assume the final action is an answer
        final_answer = action.get("tool_input", "").strip()
        self.add_message("assistant", final_answer)
        return final_answer

if __name__ == "__main__":
    agent = GoogleMapsAgent()
    agent.run_interactive()
