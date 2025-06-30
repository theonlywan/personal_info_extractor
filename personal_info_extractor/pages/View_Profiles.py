import streamlit as st
import pandas as pd
import json
from typing import List, Dict, Any, Optional
from utils.chroma_utils import get_all_profiles_from_chroma
from schema.personal_profile import (
    PersonalProfile,
    LabeledString, LabeledInt, LabeledList
)

st.set_page_config(page_title="View Stored Profiles", layout="wide")

st.title("🗂️ Stored Personal Profiles")
st.markdown("View all extracted and stored personal profiles from the ChromaDB.")

# --- Load and Display Profiles ---
@st.cache_data
def load_profiles():
    return get_all_profiles_from_chroma()

all_profiles = load_profiles()

if not all_profiles:
    st.info("No profiles found in the database yet. Extract some profiles on the main page!")
else:
    st.success(f"Found {len(all_profiles)} profile(s) in the database.")

    # --- Display Filters (Optional, for future enhancement) ---
    # st.subheader("Filter Profiles (Coming Soon)")
    # # Example: Filter by Name (simple text search on the displayed name)
    # search_query = st.text_input("Search by Name or Keyword:", "")
    # if search_query:
    #     all_profiles = [p for p in all_profiles if search_query.lower() in (p.name.value.lower() if p.name and p.name.value else '').lower()]
    #     st.info(f"Displaying {len(all_profiles)} matching profile(s).")

    # --- Display Each Profile ---
    for i, profile in enumerate(all_profiles):
        st.markdown(f"---")
        st.subheader(f"Profile {i+1}: {profile.name if profile.name else 'Unnamed Profile'}")
        
        # Display as JSON for full detail
        with st.expander("View Raw JSON"):
            st.json(profile.model_dump(exclude_none=True))

        # --- Detailed Profile Fields Table ---
        st.markdown("##### Detailed Fields:")
        display_rows = []
        field_order = [
            "name", "age", "location", "education", "work_experience", "interests",
            "personality_traits", "skills", "languages_spoken", "achievements",
            "contact_info"
        ]

        for field_name in field_order:
            field_obj = getattr(profile, field_name, None)
            
            value = "N/A"
            sentiment = "N/A"
            confidence = "N/A"

            if field_obj is None:
                pass 
            elif isinstance(field_obj, str):
                value = field_obj if field_obj is not None else "N/A"
            elif isinstance(field_obj, int):
                value = str(field_obj) if field_obj is not None else "N/A"
            elif isinstance(field_obj, list):
                value = "; ".join(field_obj) if field_obj else "N/A"
            elif isinstance(field_obj, (LabeledString, LabeledInt)):
                value = field_obj.value if field_obj.value is not None else "N/A"
                sentiment = field_obj.sentiment if field_obj.sentiment is not None else "N/A"
                confidence = f"{field_obj.confidence:.0%}" if field_obj.confidence is not None else "N/A"
            elif isinstance(field_obj, LabeledList):
                value = "; ".join(field_obj.values) if field_obj.values is not None and field_obj.values != [] else "N/A"
                sentiment = field_obj.sentiment if field_obj.sentiment is not None else "N/A"
                confidence = f"{field_obj.confidence:.0%}" if field_obj.confidence is not None else "N/A"
            
            if field_name in ["name", "age", "location", "contact_info"]: 
                display_rows.append({
                    "Field": field_name.replace('_', ' ').title(),
                    "Value": value
                })
            else:
                display_rows.append({
                    "Field": field_name.replace('_', ' ').title(),
                    "Value": value,
                    "Sentiment": sentiment,
                    "Confidence": confidence
                })
        
        df_columns = ["Field", "Value"]
        if any(row.get("Sentiment") != "N/A" and row.get("Confidence") != "N/A" for row in display_rows): 
            df_columns.extend(["Sentiment", "Confidence"])
            
        processed_display_rows = []
        for row in display_rows:
            new_row = {}
            for col in df_columns:
                new_row[col] = row.get(col, "N/A")
            processed_display_rows.append(new_row)

        df = pd.DataFrame(processed_display_rows, columns=df_columns)
        st.dataframe(df, hide_index=True, use_container_width=True)

# Footer
st.markdown("---")
st.caption("Powered by Streamlit and ChromaDB.")
