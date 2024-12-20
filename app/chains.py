import os
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
from graphviz import Digraph



load_dotenv() 
# //find .env and set as env variable then use os to retrive

class Chain:
    def __init__(self):
        self.llm = ChatGroq(temperature=0, groq_api_key=os.getenv("GROQ_API_KEY"), model_name="llama-3.1-70b-versatile")

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

# Step 3: Function to generate UML Diagram
def generate_uml_diagram(uml_info):
    print("Generating UML Diagram...")
    dot = Digraph(comment="UML Diagram")
    print("Parsing UML Info...")
    lines = uml_info.split("\n")

    for idx, line in enumerate(lines):
        line = line.strip()
    
    # Remove leading dash if present
    if line.startswith("-"):
        line = line[1:].strip()
        print(f"Processing line {idx + 1}: {line.strip()}")

        if "->" in line and ":" in line:  # Relationship
            parts = line.split("->")
            source, rest = parts[0].strip(), parts[1].strip()
             # Ensure there are two parts after the colon, else handle gracefully
            if ":" in rest:
                target, relationship = rest.split(":")
                dot.node(source, source)
                dot.node(target, target)
                dot.edge(source, target, relationship.strip())
                print(f"Added relationship: {source} -> {target} [label={relationship.strip()}]")

            else:
                # If no relationship, create a default or skip
                print(f"Skipping unrecognized line {idx + 1}: {line.strip()}")
                target = rest.strip()
                dot.node(source, source)
                dot.node(target, target)
                dot.edge(source, target, "default_relationship")  # Use a default label if no relationship

            target, relationship = rest.split(":")
            dot.node(source, source)
            dot.node(target, target)
            dot.edge(source, target, relationship.strip())
        elif ":" in line:  # Class
           try:
             class_name, details = line.split(":")
             attributes_methods = details.split("->")
             attributes = attributes_methods[0].strip()
             methods = attributes_methods[1].strip() if len(attributes_methods) > 1 else ""
             dot.node(class_name.strip(), f"{class_name.strip()}\n{attributes}\n{methods}")
             print(f"Added class: {class_name.strip()} with attributes [{attributes}] and methods [{methods}]")
           except Exception as e:
               print(f"Error processing class line {idx + 1}: {e}")
            # else: 
            #     print(f"Skipping unrecognized line {idx + 1}: {line}")
    output_file = "uml_diagram"
    print("Rendering diagram...")
    dot.render(output_file, format="png", cleanup=True)
    print(f"UML diagram saved as {output_file}.png")
    return f"{output_file}.png"

...

# # Step 4: Take Text Input from User
# user_input = input("Enter the description for UML diagram generation: ")

# # Step 5: Process Input and Generate Diagram
# uml_info = extract_uml_info(chain.llm, user_input)
# print("\nExtracted UML Information:\n")
# print(uml_info)

# diagram_path = generate_uml_diagram(uml_info)

# Step 6: Display the Path of the Generated Diagram
# print(f"\nGenerated UML diagram can be found at: {diagram_path}")



    