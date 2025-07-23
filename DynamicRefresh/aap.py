import time
import streamlit as st
from snowflake.snowpark.context import get_active_session

# Start session
session = get_active_session()


# Optional: refresh every N seconds
REFRESH_INTERVAL = 3 # seconds

# Manual refresh button
if st.button("🔄 Refresh Data"):
    st.query_params.refreshed=str(time.time())

# UI header
st.title("🖥️ System Status Dashboard (Live Refresh)")

# Fetch current system data
df = session.table("system_status").to_pandas()

# Display each system's status block
for _, row in df.iterrows():
    with st.container():
        st.markdown("----")
        st.markdown(f"### 🛠️ System: **{row['SYSTEM_NAME']}**")
        st.markdown(f"- **Status**: `{row['STATUS']}`")
        st.markdown(f"- **Created Date**: {row['CREATED_DATE']}")
        st.markdown(f"- **Last Updated**: {row['UPDATE_DATE']}")
