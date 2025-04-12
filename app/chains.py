import os
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
from graphviz import Digraph
from langchain_core.messages.human import HumanMessage
import plantuml
import subprocess


load_dotenv() 
# //find .env and set as env variable then use os to retrive
print("GROQ_API_KEY:", os.getenv("GROQ_API_KEY"))

class Chain:
    def __init__(self):
        self.llm = ChatGroq(temperature=0.7, groq_api_key=os.getenv("GROQ_API_KEY"), model_name="llama3-70b-8192")
     
# if __name__ == "__main__":
#     # Instantiate Chain
#     chain = Chain()  # Correct instantiation of the Chain class

def get_actors_from_llm(system_description):
    prompt = f"Identify the actors involved in a {system_description} system."
    response = llm.invoke(prompt)
    return response.content.strip().split("\n")  # Assuming the actors are returned as a newline-separated list.

EXPECTED_ACTORS = {
    "Banking System": ["User", "Admin", "Bank Teller", "Manager"],
    "E-Commerce System": ["Customer", "Seller", "Admin"]
}


# Step 2: Function to extract UML info using the LLM
def extract_uml_info(llm,text):
    prompt = f"""
    Extract UML components from the following text:
    {text}
    
    Provide the result in the following format:
    Classes: 
      - ClassName1: attributes -> methods
      - ClassName2: attributes -> methods
    Relationships:
      - ClassName1 -> ClassName2: relationship_type
    """
    response = llm.invoke(prompt)
    return response.content

def check_actors(system_name, user_actors):
    """Verify if the user provided all expected actors and suggest if any are missing."""
    
    # First, try generating actors from the LLM based on the system name
    system_description = f"{system_name} system"
    generated_actors = get_actors_from_llm(system_description)
    
    # Combine both expected and generated actors
    expected_actors = EXPECTED_ACTORS.get(system_name, [])
    all_actors = set(expected_actors + generated_actors)

    missing_actors = [actor for actor in all_actors if actor not in user_actors]
    
    if missing_actors:
        return f"You're missing the following actors: {', '.join(missing_actors)}. Please include them."
    else:
        return "All actors are identified. Let's move on!"


def generate_uml_diagram(uml_info):
    print("Generating UML Diagram...")
    dot = Digraph(comment="UML Diagram")
    print("Parsing UML Info...")

    lines = uml_info.split("\n")

    for idx, line in enumerate(lines):
        line = line.strip()
        
        if line.startswith("-"):  # This is either a class or relationship
            line = line[1:].strip()
            print(f"Processing line {idx + 1}: {line}")

            if "->" in line and ":" in line:  # Relationship
                parts = line.split("->")
                source, rest = parts[0].strip(), parts[1].strip()

                if ":" in rest:
                    target, relationship = rest.split(":")
                    target, relationship = target.strip(), relationship.strip()
                    dot.node(source, source)
                    dot.node(target, target)
                    dot.edge(source, target, relationship)
                    print(f"Added relationship: {source} -> {target} [{relationship}]")
                else:
                    print(f"Skipping unrecognized relationship format at line {idx + 1}: {line}")

            elif ":" in line:  # Class Definition
                try:
                    class_name, details = line.split(":")
                    class_name = class_name.strip()
                    attributes_methods = details.split("->")
                    attributes = attributes_methods[0].strip()
                    methods = attributes_methods[1].strip() if len(attributes_methods) > 1 else ""
                    dot.node(class_name, f"{class_name}\n{attributes}\n{methods}")
                    print(f"Added class: {class_name} with attributes [{attributes}] and methods [{methods}]")
                except Exception as e:
                    print(f"Error processing class line {idx + 1}: {e}")

    output_file = "uml_diagram"
    print("Rendering diagram...")
    dot.render(output_file, format="png", cleanup=True)
    print(f"UML diagram saved as {output_file}.png")
    return f"{output_file}.png"


def generate_uml_diagram_plantuml(uml_info):
    print("Generating PlantUML Diagram...")
    plantuml_text = "@startuml\n"

    lines = uml_info.split("\n")

    for idx, line in enumerate(lines):
        line = line.strip()

        if line.startswith("-"):  # Process lines starting with '-'
            line = line[1:].strip()
            print(f"Processing line {idx + 1}: {line}")

            if "->" in line and ":" in line:  # Relationship
                parts = line.split("->")
                source, rest = parts[0].strip(), parts[1].strip()

                if ":" in rest:
                    target, relationship = rest.split(":")
                    target, relationship = target.strip(), relationship.strip()

                    # Map your relationship descriptions to PlantUML syntax
                    if relationship.lower() == "association":
                        plantuml_text += f"{source} -- {target} : {relationship}\n"
                    elif relationship.lower() == "inheritance":
                        plantuml_text += f"{source} --|> {target} : {relationship}\n"
                    elif relationship.lower() == "composition":
                        plantuml_text += f"{source} *-- {target} : {relationship}\n"
                    elif relationship.lower() == "aggregation":
                        plantuml_text += f"{source} o-- {target} : {relationship}\n"
                    else:
                        plantuml_text += f"{source} --> {target} : {relationship}\n"  # Default to simple association

                    print(f"Added relationship: {source} -> {target} [{relationship}]")
                else:
                    print(f"Skipping unrecognized relationship format at line {idx + 1}: {line}")

            elif ":" in line:  # Class Definition
                try:
                    class_name, details = line.split(":")
                    class_name = class_name.strip()
                    attributes_methods = details.split("->")
                    attributes = attributes_methods[0].strip()
                    methods = attributes_methods[1].strip() if len(attributes_methods) > 1 else ""

                    plantuml_text += f"class {class_name} {{\n"
                    if attributes:
                        for attr in attributes.split(","):
                            plantuml_text += f"    {attr.strip()}\n"
                    if methods:
                        for method in methods.split(","):
                            plantuml_text += f"    {method.strip()}()\n"
                    plantuml_text += "}\n"

                    print(f"Added class: {class_name} with attributes [{attributes}] and methods [{methods}]")
                except Exception as e:
                    print(f"Error processing class line {idx + 1}: {e}")

    plantuml_text += "@enduml\n"

    output_file = "plantuml_diagram.png"
    temp_puml_file = "temp_diagram.puml"
    print("Rendering diagram...")

    plantuml_jar_path = os.path.join(os.path.expanduser("~"), "Downloads", "plantuml-1.2025.2.jar")

    try:
        with open(temp_puml_file, "w") as f:
            f.write(plantuml_text)

        command = [
            "java",
            "-jar",
            plantuml_jar_path,
            temp_puml_file,
            "-o",
            "."
        ]

        subprocess.run(command, check=True)

        if not keep_temp_puml:
            os.remove(temp_puml_file)

        print(f"PlantUML diagram saved as {output_file}")
        return output_file

    except subprocess.CalledProcessError as e:
        print(f"Error rendering PlantUML diagram: {e}")
        return None
    except FileNotFoundError:
        print(f"Error: plantuml.jar not found at {plantuml_jar_path}. or Java is not installed.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None
