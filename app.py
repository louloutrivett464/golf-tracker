import os
import json
import streamlit as st

# Set up the web page title and icon
st.set_page_config(page_title="Golf Handicap Tracker", page_icon="⛳", layout="centered")

# Course Par Data
basset12 = ["4","3","4","3","5","4","4","4","4","4","4","5"]
broome9 = ["3","4","3","5","3","3","4","4","3"]
broome18 = ["5","4","3","4","4","3","4","4","4","4","3","5","4","4","3","4","5","4"]
basset18 = ["4","3","4","4","4","4","4","4","5","4","3","4","4","4","4","4","4","5"]
ogbourne18 = ["4","4","4","3","4","4","4","3","5","5","4","4","4","5","3","4","3","4"]
wragbarn18 = ["4","4","3","5","3","5","4","4","4","5","4","3","4","4","4","3","5","4"]

DATAFILE = "profiles.json"

# Helper functions for data management
def load_profiles():
    if os.path.exists(DATAFILE):
        with open(DATAFILE, "r") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return {}
    return {}

def save_profiles(data):
    with open(DATAFILE, "w") as file:
        json.dump(data, file, indent=4)

def scorecalculator(score, course):
    total = 0
    if course == "broome 9 hole":
        course_pars = broome9
    elif course == "basset 12 hole":
        course_pars = basset12
    elif course == "wragbarn":
        course_pars = wragbarn18
    elif course == "broome 18 hole":
        course_pars = broome18
    elif course == "basset 18 hole":
        course_pars = basset18
    elif course == "ogbourne":
        course_pars = ogbourne18
    else:
        return None
        
    if len(score) != len(course_pars):
        st.error(f"Error: You entered {len(score)} scores, but this course requires {len(course_pars)}.")
        return None

    for i in range(len(course_pars)):
        total += (score[i] - int(course_pars[i]))
    return total

def calculate_handicap_value(scores):
    roundsplayed = len(scores)
    if roundsplayed == 0:
        return "No rounds played"
        
    bestscores = sorted(scores)
    if roundsplayed < 3:   
        return sum(scores) / len(scores)
    elif roundsplayed <= 5:
        return float(bestscores[0])
    elif roundsplayed >= 20:
        recent20 = scores[-20:]
        best20sorted = sorted(recent20)
        best8 = best20sorted[:8]
        return sum(best8) / 8
    else:
        lowestthree = bestscores[:3]
        return sum(lowestthree) / 3

# --- MAIN APP INTERFACE ---
st.title("⛳ Golf Handicap Tracker")

profiles = load_profiles()

# 1. Login Sidebar (Handles dynamic and unlimited profiles)
st.sidebar.header("User Login")
name_input = st.sidebar.text_input("Enter Profile Name:").strip().lower()

if not name_input:
    st.info("Please enter a profile name in the sidebar to begin.")
else:
    display_name = name_input.capitalize()
    
    # Initialize profile if it doesn't exist
    if name_input not in profiles:
        profiles[name_input] = []
        save_profiles(profiles)
        st.sidebar.success(f"Created new profile for {display_name}!")
    else:
        st.sidebar.success(f"Logged in as {display_name}")

    # Tabs for modern web navigation instead of an input menu loop
    tab1, tab2, tab3, tab4 = st.tabs([
        "📝 Enter Score", 
        "📊 My Handicap", 
        "🏆 Leaderboard & Others", 
        "⚙️ Manage Data"
    ])

    # TAB 1: ENTER SCORES
    with tab1:
        st.header(f"Record a New Round for {display_name}")
        coursechose = st.selectbox(
            "Select the course you played:",
            ["basset 12 hole", "broome 9 hole", "basset 18 hole", "broome 18 hole", "ogbourne", "wragbarn"]
        )
        userinput = st.text_input("Enter your scores separated by commas (e.g., 4,5,3,4):")
        
        if st.button("Save Round"):
            if userinput:
                try:
                    player_scores = [int(s) for s in userinput.split(",") if s.strip()]
                    shotsover = scorecalculator(player_scores, coursechose)
                    
                    if shotsover is not None:
                        # Refresh data, append, and save
                        profiles = load_profiles()
                        profiles[name_input].append(shotsover)
                        save_profiles(profiles)
                        
                        if shotsover > 0:
                            st.success(f"Round saved! Today you scored {shotsover} over par.")
                        elif shotsover < 0:
                            st.success(f"Round saved! Today you scored {abs(shotsover)} under par.")
                        else:
                            st.success("Round saved! Today you shot even par.")
                except ValueError:
                    st.error("Invalid entry. Please use numbers and commas only.")
            else:
                st.warning("Please enter your scores first.")

    # TAB 2: MY HANDICAP SUMMARY
    with tab2:
        st.header(f"Handicap Metrics: {display_name}")
        user_scores = profiles.get(name_input, [])
        roundsplayed = len(user_scores)
        
        if roundsplayed == 0:
            st.warning("No rounds played yet. Use the 'Enter Score' tab to log your first game.")
        else:
            hc_val = calculate_handicap_value(user_scores)
            
            # Display important summary statistics prominently
            col1, col2 = st.columns(2)
            with col1:
                if isinstance(hc_val, float):
                    st.metric(label="Current Handicap Index", value=f"{hc_val:.1f}")
                else:
                    st.metric(label="Current Handicap Index", value=hc_val)
            with col2:
                st.metric(label="Rounds Played", value=roundsplayed)
                
            st.subheader("Round History")
            st.write(f"**Chronological scores (relative to par):** {user_scores}")
            st.write(f"**Sorted scores (best to worst):** {sorted(user_scores)}")

    # TAB 3: LEADERBOARD & INDIVIDUAL LOOKUPS
    with tab3:
        st.header("Overall Leaderboard")
        profiles = load_profiles() # Fetch latest updates
        
        if not profiles:
            st.write("No player records found.")
        else:
            # Build an elegant web table for the leaderboard
            leaderboard_data = []
            for p_name, p_scores in profiles.items():
                hc = calculate_handicap_value(p_scores)
                hc_display = f"{hc:.1f}" if isinstance(hc, float) else hc
                leaderboard_data.append({
                    "Player": p_name.capitalize(),
                    "Handicap Index": hc_display,
                    "Rounds Played": len(p_scores)
                })
            st.table(leaderboard_data)
            
        st.divider()
        st.header("Look Up Another Player")
        target_name = st.selectbox(
            "Select a profile to view:", 
            [k.capitalize() for k in profiles.keys()]
        ).lower()
        
        if st.button("View Target Profile"):
            target_scores = profiles.get(target_name, [])
            if target_scores:
                t_hc = calculate_handicap_value(target_scores)
                t_hc_display = f"{t_hc:.1f}" if isinstance(t_hc, float) else t_hc
                st.write(f"### Profile: {target_name.capitalize()}")
                st.write(f"• **Handicap Index:** {t_hc_display}")
                st.write(f"• **Total Rounds:** {len(target_scores)}")
                st.write(f"• **Scores History:** {target_scores}")
            else:
                st.write("This user has no score history to display yet.")

    # TAB 4: MANAGE DATA (DELETE & WIPE)
    with tab4:
        st.header("Data Management Tools")
        user_scores = profiles.get(name_input, [])
        
        st.subheader("Delete Last Round")
        if len(user_scores) > 0:
            st.write(f"Your most recent score entry is: **{user_scores[-1]}**")
            if st.button("Delete Most Recent Round"):
                profiles = load_profiles()
                removed = profiles[name_input].pop()
                save_profiles(profiles)
                st.success(f"Deleted round with score: {removed}. Refreshing page...")
                st.rerun()
        else:
            st.write("No scores available to delete.")
            
        st.divider()
        st.subheader("Wipe Profile History")
        confirm_wipe = st.checkbox("I heavily confirm that I want to wipe ALL scores for this profile.")
        if st.button("Completely Clear All Scores", type="primary"):
            if confirm_wipe:
                profiles = load_profiles()
                profiles[name_input] = []
                save_profiles(profiles)
                st.success("All data successfully wiped. Refreshing page...")
                st.rerun()
            else:
                st.error("Please check the confirmation checkbox first.")
