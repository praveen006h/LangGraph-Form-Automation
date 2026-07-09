This is a purely technical challenge and it is mandatory to use the text stack outlined in the document. Let's talk about what you need to build. You need to create a replica of the screenshot provided. Imagine a split screen layout. On the left side, you have an interaction details panel with a form. On the right side, you have an AI assistant chat panel.

Here is the most important rule: You must not fill the left form manually. Instead, you must utilize the AI assistant on the right to control the form on the left. You need to implement a minimum of five tools using Langgraph.

Let's look at the first one, the log interaction tool. This works just like ChatGPT. You give a natural prompt to the AI assistant. For example, you might type, "Today I met with Dr. Smith and discussed product X efficiency. The sentiment was positive and I shared the brochures." The AI assistant must extract this information and automatically fill the fields in the left panel. It should populate the HCP name as Dr. Smith, the date as today, the sentiment as positive, and mark that brochures were shared.

The second mandatory tool is the edit interaction tool. Let's say the form is filled, but you realize there is a mistake. You don't click the form to fix it; you tell the AI. You might type, "Sorry, the name was actually Dr. John and the sentiment was negative." The AI assistant must then update only those specific fields on the left panel, changing the name to Dr. John and the sentiment to negative while keeping everything else the same.

Requirements and conclusion: To pass this assessment, you need to implement five Langgraph tools in total. We have defined the first two for you. The remaining three are up to you to define and build.

A final critical note: You must use Langgraph and an LLM to drive these tools. If the logic is hard-coded without these specific technologies, the task will not be considered. Important note: You must not fill out the left form manually, but utilize the AI assistant to fill the form. Good luck.
