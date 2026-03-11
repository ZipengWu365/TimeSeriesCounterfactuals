"""Example: exporting tscfbench function tools for OpenAI Responses API.

This example is not executed in tests because it requires an API key and the `openai`
package. It shows the intended orchestration pattern:

1. planning / retrieval turn with function tools,
2. separate edit turn without tools if you want predicted-output style regeneration.
"""

from tscfbench.agent import export_openai_function_tools


def main() -> None:
    tools = export_openai_function_tools(strict=True)
    for tool in tools[:3]:
        print(tool["name"])


if __name__ == "__main__":
    main()
