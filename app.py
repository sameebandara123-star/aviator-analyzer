import streamlit as st
import json
import os

DATA_FILE = "aviator_data.json"

START_BALANCE = 1000
TEST_STAKE = 20
MAX_TEST_LOSS = 100


# -----------------------------
# DATA FUNCTIONS
# -----------------------------

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except:
            pass

    return {
        "rounds": [],
        "balance": START_BALANCE,
        "wins": 0,
        "losses": 0,
        "test_count": 0,
        "total_profit": 0
    }


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


# -----------------------------
# ANALYSIS
# -----------------------------

def analyze_rounds(rounds):

    if len(rounds) < 5:
        return {
            "signal": False,
            "message": "අවම වශයෙන් rounds 5ක් දාන්න."
        }

    last_10 = rounds[-10:]
    last_5 = rounds[-5:]

    below_2x = sum(x < 2.0 for x in last_10)
    below_1_5x = sum(x < 1.5 for x in last_5)

    signal = below_2x >= 6 and below_1_5x >= 3

    if signal:
        message = (
            "⚠️ EXPERIMENTAL SIGNAL\n\n"
            "පසුගිය rounds වල low multipliers වැඩි pattern එකක් තියෙනවා.\n"
            "ඊළඟ round එක HIGH multiplier එකකට යයි කියලා මෙයින් සහතිකයක් නෑ.\n"
            "Paper test එකක් විතරක් කරන්න."
        )
    else:
        message = "දැනට experimental signal එකක් නැහැ."

    return {
        "signal": signal,
        "message": message,
        "below_2x": below_2x,
        "below_1_5x": below_1_5x
    }


# -----------------------------
# PAGE
# -----------------------------

st.set_page_config(
    page_title="Aviator Analyzer",
    page_icon="✈️",
    layout="centered"
)

st.title("✈️ AVIATOR ANALYZER")

st.write(
    "Historical round data analysis සහ paper testing සඳහා පමණි."
)

st.warning(
    "⚠️ මෙය prediction හෝ guaranteed winning system එකක් නොවේ. "
    "Real-money betting සඳහා භාවිතා නොකරන්න."
)


# -----------------------------
# LOAD DATA
# -----------------------------

data = load_data()

rounds = data["rounds"]


# -----------------------------
# ADD ROUND
# -----------------------------

st.header("📊 Add Round")

multiplier = st.number_input(
    "Round multiplier",
    min_value=1.00,
    max_value=10000.00,
    value=1.00,
    step=0.01
)

if st.button("➕ Add Round"):

    rounds.append(float(multiplier))

    data["rounds"] = rounds

    save_data(data)

    st.success(f"{multiplier:.2f}x round එක saved!")

    st.rerun()


# -----------------------------
# ROUND HISTORY
# -----------------------------

st.header("📋 Round History")

if rounds:

    st.write("Last 20 rounds:")

    display_rounds = rounds[-20:]

    st.code(
        " → ".join(f"{x:.2f}x" for x in display_rounds)
    )

else:

    st.info("තවම rounds එකක්වත් add කරලා නැහැ.")


# -----------------------------
# ANALYSIS
# -----------------------------

st.header("🔎 Analysis")

analysis = analyze_rounds(rounds)

if "below_2x" in analysis:

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Last 10 below 2x",
            analysis["below_2x"]
        )

    with col2:
        st.metric(
            "Last 5 below 1.5x",
            analysis["below_1_5x"]
        )


if analysis["signal"]:

    st.error(analysis["message"])

else:

    st.info(analysis["message"])


# -----------------------------
# PAPER TEST
# -----------------------------

st.header("🧪 Paper Test")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Paper Balance",
        f"Rs. {data['balance']:.2f}"
    )

with col2:
    st.metric(
        "Wins",
        data["wins"]
    )

with col3:
    st.metric(
        "Losses",
        data["losses"]
    )


st.write(
    f"Fixed test stake: Rs. {TEST_STAKE}"
)

st.write(
    f"Maximum experimental loss limit: Rs. {MAX_TEST_LOSS}"
)


# -----------------------------
# RECORD RESULT
# -----------------------------

if analysis["signal"]:

    st.subheader("🧪 Record Next Round")

    result = st.number_input(
        "Next round multiplier",
        min_value=1.00,
        max_value=10000.00,
        value=1.00,
        step=0.01,
        key="test_result"
    )

    if st.button("Record Paper Test"):

        if data["total_profit"] <= -MAX_TEST_LOSS:

            st.error(
                "Paper test loss limit reached. "
                "Testing stopped."
            )

        else:

            # Experimental target:
            # 2x or above = win
            if result >= 2.0:

                data["balance"] += TEST_STAKE
                data["wins"] += 1
                data["total_profit"] += TEST_STAKE

                st.success(
                    f"WIN ✅ +Rs. {TEST_STAKE}"
                )

            else:

                data["balance"] -= TEST_STAKE
                data["losses"] += 1
                data["total_profit"] -= TEST_STAKE

                st.error(
                    f"LOSS ❌ -Rs. {TEST_STAKE}"
                )

            data["test_count"] += 1

            save_data(data)

            st.rerun()


# -----------------------------
# STATISTICS
# -----------------------------

st.header("📈 Statistics")

if data["test_count"] > 0:

    total = data["test_count"]

    win_rate = (data["wins"] / total) * 100

    st.metric(
        "Total Tests",
        total
    )

    st.metric(
        "Win Rate",
        f"{win_rate:.2f}%"
    )

    st.metric(
        "Total Profit/Loss",
        f"Rs. {data['total_profit']:.2f}"
    )

else:

    st.info(
        "Paper tests record කළාම statistics මෙතන පෙන්වයි."
    )


# -----------------------------
# RESET
# -----------------------------

st.header("⚙️ Controls")

if st.button("🗑️ Reset Paper Test"):

    data["balance"] = START_BALANCE
    data["wins"] = 0
    data["losses"] = 0
    data["test_count"] = 0
    data["total_profit"] = 0

    save_data(data)

    st.success("Paper test reset කළා.")

    st.rerun()
