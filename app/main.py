import streamlit as st
from chains import Chain
from chains import extract_uml_info
from chains import generate_uml_diagram

if __name__ == "__main__":
   chain = Chain()

st.title("UML Generator")

input = st.text_input("Enter the Requirement: ", value=" ")

submit_button = st.button("Submit")

if submit_button:
    try:
         # Extract UML information
        uml_info = extract_uml_info(chain.llm, input)
        st.text("Extracted UML Information:")
        st.text(uml_info)
        
        # Generate UML diagram
        diagram_path = generate_uml_diagram(uml_info)
        st.image(diagram_path)  # Display the UML diagram
        st.success("UML diagram generated successfully!")
    except Exception as e:
        st.error("An Error Occured: {e}")

# if __name__ == "__main__":
    
#     st.set_page_config(layout="wide", page_title="UML Diagram Generator")
#     create_streamlit_app(chain, clean_text)


    # st.code("Hello User", language ='markdown')
