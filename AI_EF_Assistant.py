import streamlit as st
import json
from openai import OpenAI
from dotenv import load_dotenv
import os

# Set up
load_dotenv()

client = OpenAI()

# Session State

if "plan" not in st.session_state:
    st.session_state.plan = None

# Load user profile 

profile_path = "user_profile.json"
if os.path.exists(profile_path):
    with open(profile_path, "r") as f:
        profile = json.load(f)
else:
    profile = {
    "preferences": {
    "likes": [],
    "dislikes": []
    }
    }

# Create profile dashboard

st.sidebar.title("User Profile")

likes = profile["preferences"]["likes"]
dislikes = profile["preferences"]["dislikes"]

st.sidebar.subheader("✅ Likes")
if likes:
    for item in likes:
        st.sidebar.write(f"• {item}")
else:
    st.sidebar.write("No preferences learned yet")

st.sidebar.subheader("❌ Dislikes")
if dislikes:
    for item in dislikes:
        st.sidebar.write(f"• {item}")
else:
    st.sidebar.write("No dislikes learned yet")

# UI

st.title("ADHD Executive Function Assistant")

energy = st.selectbox(
    "Energy Level", 
    ["Low", "Medium", "High"]
)

mood = st.selectbox(
    "Mood", 
    ["Overwhelmed", "Distracted", "Neutral", "Motivated"]
)

available_time = st.selectbox(
    "Time Available", 
    ["30 mins", "1 hour", "2 hours", "4+ hours"]
)

tasks = st.text_area(
    "Tasks (& due dates)",
    height = 200
)

# Generate Plan

if st.button("Generate Plan"):
    prompt = f"""
    You are an ADHD productivity coach. 

    User Preferences: {profile}

    Adap today's recommendations based on user preferences. 

    Current Energy: {energy}
    Current Mood: {mood}
    Available time: {available_time}
    Tasks: {tasks}

    Generate:
    - task breakdowns
    - priorities
    - work blocks of odd times between 13 and 37 minutes
    - sensory breaks
    - creative breaks
    - realistic sequencing

    The user has ADHD.

    To increase novelty and reduce task initiation barriers:

    - Never use standard productivity block lengths.
    - Never use 15, 20, 25, 30, 45 or 60 minute sessions.
    - Use unusual durations between 13 and 37 minutes.
    - Every focus block should have a different duration.
    - Match the duration to the effort required:
    - Very small tasks: 13-18 minutes
    - Small tasks: 19-24 minutes
    - Medium tasks: 25-31 minutes
    - Large tasks: 32-37 minutes

    Good examples:
    17 minutes
    22 minutes
    29 minutes
    33 minutes

    Bad examples:
    15 minutes
    20 minutes
    25 minutes
    30 minutes
    45 minutes

    Use supportive language.
    """

    response = client.chat.completions.create(
        model = "gpt-4o-mini",
        messages = [
            {
                "role": "system",
                "content": "You are an ADHD productivity coach"
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    st.session_state.plan = (response.choices[0].message.content)

if st.session_state.plan:
    # Display plan
    st.subheader("Today's Plan")
    st.write(
        st.session_state.plan
        )

    # Reflection form
    st.subheader("Reflection")
    with st.form("reflection_form"):
        
        helpfulness = st.slider(
                "How helpful was today's plan?", 
                1,
                5,
                3
            )

        liked = st.text_area(
            "What helped?",
            placeholder="""The short time blocks helped me start.\nThe movement breaks were useful.\n Breaking tasks down reduced overwhelm."""
        )

        disliked = st.text_area(
            "What didn't work?",
            placeholder="""The focus blocks were too short.\nThe creative breaks were dsitracting.\nI needed more structure."""
        )

        submitted = st.form_submit_button(
            "Save Reflection"
        )

        # store feedback
        if submitted:
            if liked.strip():
                profile["preferences"]["likes"].append(
                    liked
                )
            if disliked.strip():
                profile["preferences"]["dislikes"].append(
                    disliked
                )

            with open(profile_path, "w") as f:
                json.dump(
                    profile,
                    f,
                    indent = 4
                )
            st.success("User profile updated")
    
        
