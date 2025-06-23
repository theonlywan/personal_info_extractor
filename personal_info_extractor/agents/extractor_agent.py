from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from schema.personal_profile import PersonalProfile, State
from typing import Dict

def extract_info(State: State) -> Dict[str, any]:
    extracted_info = {
        "name": None,
        "age": None,
        "location": None,
        "education": None,
        "interests": [],
        "personality_traits": []
    }

    with open("prompts/extractor_prompt.txt", "r") as file:
        prompt = file.read()

    llm = ChatOpenAI(model = "gpt-4o", temperature = 0)

    template = ChatPromptTemplate([
        ("system", prompt),
        ("human", "{dialogue}")
    ])

    extraction_chain = template | llm.with_structured_output(PersonalProfile)

    extracted_info = extraction_chain.invoke({"dialogue": State.preprocessed_text})

    return {
        "extracted_info": extracted_info,
        "current_state": "extraction_complete",
        "errors": State.errors
    }