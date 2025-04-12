import os
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
from graphviz import Digraph
from langchain_core.messages.human import HumanMessage


# load_dotenv() 
# # //find .env and set as env variable then use os to retrive
# print("GROQ_API_KEY:", os.getenv("GROQ_API_KEY"))

class Chain:
    def __init__(self):
        self.llm = ChatGroq(temperature=0.7, groq_api_key=os.getenv("GROQ_API_KEY"), model_name="llama3-70b-8192")
     
# if __name__ == "__main__":
#     # Instantiate Chain
#     chain = Chain()  # Correct instantiation of the Chain class

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
