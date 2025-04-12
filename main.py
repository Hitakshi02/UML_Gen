import streamlit as st
import subprocess
import os
import re
from openai import OpenAI

# Together.ai setup
client = OpenAI(
    api_key="YOUR-API-KEY",
    base_url="https://api.together.xyz/v1"
)

#  Track flow stage
flow_steps = ["greet", "name", "boundary", "purpose", "actors", "actions", "confirm", "done"]
if "step_index" not in st.session_state:
    st.session_state.step_index = 0

#  Data store
if "uc_data" not in st.session_state:
    st.session_state.uc_data = {
        "system_name": None,
        "purpose": None,
        "boundary": None,
        "actors": [],
        "use_cases": {}
    }

# 🧾 Teaching prompt builder
def get_prompt(step):
    prompts = {
        "greet": "Agent: Today’s lesson is about how to create a use case diagram. Are you ready?",
        "name": "Agent: Great! Let's begin by naming your system. This could be something like 'Online Banking System' or 'Library Management Tool'. What would you like to call it?",
        "boundary": "Agent: Good! Let's define what features or components are part of your system. For example, 'User login', 'Transaction processing', etc. What are yours?",
        "purpose": "Agent: What's the primary purpose of your system? Think of this as its goal. For example, 'To allow users to manage their bank accounts online.'",
        "actors": "Agent: Now, who interacts with this system? Actors can be users, admins, or external systems. Separate multiple actors with commas.",
        "actions": "Agent: For each actor, what actions do they perform? You can enter in this format: 'Customer: Check Balance, Transfer Funds' OR describe freely and I'll help you extract it!",
        "confirm": "Agent: Thanks! Type 'Generate' to create your diagram or 'Edit' to revise any step.",
    }
    return prompts.get(step, "Agent: Let's continue.")


def extract_use_cases_with_llm(text):
    try:
        prompt = f"""Extract actors and their use cases from the following text:

{text}

Return ONLY the result in this format — no explanations or extra content:
Actor1: Use case 1, Use case 2
Actor2: Use case 3
"""
        st.markdown("🧪 **Prompt sent to LLM:**")
        st.code(prompt)

        response = client.chat.completions.create(
            model="mistralai/Mistral-7B-Instruct-v0.2",  # Make sure this model exists
            messages=[{"role": "user", "content": prompt}]
        )

        output = response.choices[0].message.content.strip()

        st.markdown("🧠 **LLM Raw Response:**")
        st.code(output)

        return output

    except Exception as e:
        st.error(f"❌ LLM call failed: {e}")
        return None

# Entity extraction logic
def extract_entities(user_msg):
    step = flow_steps[st.session_state.step_index]
    data = st.session_state.uc_data

    if step == "name":
        data["system_name"] = user_msg.strip()
    elif step == "boundary":
        data["boundary"] = user_msg.strip()
    elif step == "purpose":
        data["purpose"] = user_msg.strip()
    elif step == "actors":
         actors = [a.strip() for a in user_msg.replace("\n", ",").split(",") if a.strip()]
         data["actors"] = actors

    elif step == "actions":
         llm_output = extract_use_cases_with_llm(user_msg)
         if not llm_output or not isinstance(llm_output, str):
             st.error("⚠️ LLM did not return any usable response. Please try again.")
             return
         lines = llm_output.strip().split("\n")
         for line in lines:
          if ":" in line:
            actor, actions = line.split(":", 1)
            actor = actor.strip().lower()
            matched_actor = next((a for a in data["actors"] if a.lower() == actor), None)

            if matched_actor:
                use_cases = [a.strip() for a in actions.split(",") if a.strip()]
                data["use_cases"].setdefault(matched_actor, []).extend(use_cases)
            else:
                st.warning(f"⚠️ Actor '{actor}' not matched to any declared actor.")

# 🌱 PlantUML Generator
def generate_use_case_diagram_plantuml(data):
    plantuml_text = "@startuml\n"
    plantuml_text += "left to right direction\n"

    for actor in data['actors']:
        actor_id = re.sub(r'[^a-zA-Z0-9_]', '_', actor.strip())
        plantuml_text += f'actor "{actor}" as {actor_id}\n'

    system_name = data['system_name'] or "System"
    plantuml_text += f'rectangle "{system_name}" {{\n'

    for actions in data['use_cases'].values():
        for action in actions:
            use_case_id = re.sub(r'[^a-zA-Z0-9_]', '_', action.strip())
            plantuml_text += f'  usecase "{action}" as {use_case_id}\n'

    plantuml_text += "}\n"

    for actor, actions in data['use_cases'].items():
        actor_id = re.sub(r'[^a-zA-Z0-9_]', '_', actor.strip())
        for action in actions:
            use_case_id = re.sub(r'[^a-zA-Z0-9_]', '_', action.strip())
            plantuml_text += f"{actor_id} --> {use_case_id}\n"

    plantuml_text += "@enduml\n"

    with st.expander("📄 Generated PlantUML Code"):
        st.code(plantuml_text, language="plantuml")

    puml_path = "use_case_diagram.puml"
    with open(puml_path, "w") as f:
        f.write(plantuml_text)

    plantuml_jar_path = os.path.join(os.path.expanduser("~"), "Downloads", "plantuml-1.2025.2.jar")
    try:
        subprocess.run(["java", "-jar", plantuml_jar_path, puml_path, "-o", "."], check=True)
        return puml_path.replace(".puml", ".png")
    except Exception as e:
        st.error(f"Error generating diagram: {e}")
        return None

# 🖼️ UI
st.title("🎓 Use Case Diagram Tutor")

user_input = st.chat_input("Say something to your assistant...")

if user_input:
    current_step = flow_steps[st.session_state.step_index]

    with st.chat_message("user"):
        st.markdown(user_input)

    if current_step == "greet":
        if user_input.lower().strip() in ["yes", "sure", "okay", "ok", "ready"]:
            st.session_state.step_index += 1
        else:
            st.warning("Please say 'yes' when you're ready to begin.")

    elif current_step in ["name", "boundary", "purpose", "actors", "actions"]:
        extract_entities(user_input)
        st.session_state.step_index += 1

    elif current_step == "confirm":
        if "generate" in user_input.lower():
            st.session_state.step_index += 1
        elif "edit" in user_input.lower():
            st.info("Please specify what you'd like to edit. Editing mode coming soon.")
        else:
            st.warning("Please type 'Generate' to continue or 'Edit' to revise.")

# 🤖 Assistant message
step_now = flow_steps[st.session_state.step_index]
if step_now != "done":
    with st.chat_message("assistant"):
        st.markdown(get_prompt(step_now))

# ✅ Final output
if step_now == "done":
    st.subheader("✅ Generated Use Case Diagram")
    img_path = generate_use_case_diagram_plantuml(st.session_state.uc_data)
    if img_path:
        st.image(img_path)
        st.success("Diagram complete! 🎉")
    st.markdown("You can restart by refreshing the app.")


# import streamlit as st
# from components.chatbot import chat_interface
# from components.step_manager import step_flow
# from components.diagram_generator import generate_use_case_diagram

# st.set_page_config(page_title="Graduate-Level Use Case Diagram Assistant", layout="wide")

# st.title("🎓 Use Case Diagram Teaching Assistant")

# # Initialize session state
# if 'step' not in st.session_state:
#     st.session_state.step = 1
# if 'inputs' not in st.session_state:
#     st.session_state.inputs = {
#         'system_name': '',
#         'system_purpose': '',
#         'system_boundary': '',
#         'actors': [],
#         'use_cases': {},
#         'relationships': []
#     }

# # Run the interactive step-by-step flow
# step_flow()

# # Show the chatbot on the side for feedback and brainstorming
# with st.sidebar:
#     chat_interface()

# # Generate diagram after the last step
# if st.session_state.step == 6:
#     generate_use_case_diagram(st.session_state.inputs)
#     st.success("Use case diagram generated!")

# from openai import OpenAI
# import streamlit as st
# from graphviz import Digraph

# client = OpenAI(
#     api_key="faaa019c709d794b55abd03f2aa2479f72492c945f36cf8dce14dc8d4e477ba7",  # or use st.secrets if set
#     base_url="https://api.together.xyz/v1"  # Together.ai's endpoint
# )
# # Initialize session state
# if "messages" not in st.session_state:
#     st.session_state.messages = [
#         {"role": "system", "content": """
# You are a teaching assistant guiding a student to design a use case diagram.

# - Collect information step-by-step: system name, purpose, system boundary, actors, and their actions.
# - Confirm before moving to next step.
# - Once you have all information, say: 'Awesome! Let's generate your diagram.' 
# - End your output with: [GENERATE]
# """}
#     ]

# if "uc_data" not in st.session_state:
#     st.session_state.uc_data = {
#         "system_name": None,
#         "purpose": None,
#         "actors": [],
#         "use_cases": {}
#     }

# def extract_structured_data(response):
#     # This is a very basic extraction prototype.
#     lines = response.split("\n")
#     for line in lines:
#         if "System name:" in line:
#             st.session_state.uc_data["system_name"] = line.split(":")[1].strip()
#         elif "Purpose:" in line:
#             st.session_state.uc_data["purpose"] = line.split(":")[1].strip()
#         elif "Actor:" in line:
#             actor = line.split(":")[1].strip()
#             if actor not in st.session_state.uc_data["actors"]:
#                 st.session_state.uc_data["actors"].append(actor)
#         elif "Action" in line or "Use case" in line:
#             parts = line.split(":")
#             if len(parts) == 2:
#                 actor, action = parts
#                 actor = actor.strip().replace("Action by", "").replace("Use case for", "").strip()
#                 action = action.strip()
#                 st.session_state.uc_data["use_cases"].setdefault(actor, []).append(action)

# def generate_diagram():
#     dot = Digraph()
#     dot.attr('node', shape='rectangle')
#     dot.node(st.session_state.uc_data["system_name"], style='filled', fillcolor='lightgrey')

#     dot.attr('node', shape='ellipse')
#     for actor in st.session_state.uc_data["actors"]:
#         dot.node(actor)
#         dot.edge(actor, st.session_state.uc_data["system_name"])

#         for use_case in st.session_state.uc_data["use_cases"].get(actor, []):
#             dot.node(use_case)
#             dot.edge(st.session_state.uc_data["system_name"], use_case)
#             dot.edge(actor, use_case)

#     return dot

# # UI
# st.title("🎓 Use Case Diagram Tutor (Chat Mode)")
# st.markdown("Chat with your assistant to build your use case diagram.")

# # Chat input
# user_input = st.chat_input("Say something to your assistant...")

# if user_input:
#     st.session_state.messages.append({"role": "user", "content": user_input})

#     with st.chat_message("user"):
#         st.markdown(user_input)

#     with st.spinner("Assistant is thinking..."):
#         response = client.chat.completions.create(
#     model="mistralai/Mistral-7B-Instruct-v0.1",
#     messages=[
#         {"role": "system", "content": "You are a helpful assistant."},
#         {"role": "user", "content": "Let's design a hostel management system."}
#     ]
# )
#         reply = response.choices[0].message.content
#         st.session_state.messages.append({"role": "assistant", "content": reply})

#         with st.chat_message("assistant"):
#             st.markdown(reply)

#         if "[GENERATE]" in reply:
#             extract_structured_data(reply)
#             st.session_state["ready_to_generate"] = True

# # Show final diagram
# if st.session_state.get("ready_to_generate"):
#     st.subheader("✅ Generated Use Case Diagram")
#     st.graphviz_chart(generate_diagram())
