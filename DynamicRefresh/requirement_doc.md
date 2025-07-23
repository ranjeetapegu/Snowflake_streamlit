# Snowflake Streamlit App: Dynamic Table Status Viewer

This project is a Streamlit application hosted within Snowflake that displays the live status from a Snowflake table. The table's `status` column is updated dynamically each time a scheduled Snowflake task runs. The app provides a simple interface for viewing these status updates with a manual refresh mechanism.

---

## 🧩 Problem Statement

In this project, we aim to solve the following:

> A Snowflake table contains a `status` column that changes every time a background task executes. We want a Streamlit app inside Snowflake that reflects these updates automatically. However, native auto-refresh capabilities are restricted in the Snowflake Streamlit runtime environment.

---

## 🔍 Features

- ✅ Displays real-time status data from a Snowflake table
- 🔄 Provides a "Refresh" button to manually reload the table
- 🕒 Shows the "Last Updated" timestamp for user clarity
- ❌ Auto-refresh via timer is not natively supported in Snowflake Streamlit (explained below)

---

## 🚫 Why Auto-Refresh is Not Supported in Snowflake Streamlit

Due to the containerized and secure environment of Snowflake-hosted Streamlit apps:
- `st.experimental_rerun()` is currently **not available**
- Background timers, WebSocket listeners, and JavaScript-based intervals are **not allowed**

As a result, auto-refreshing based on time or events is **not natively possible** inside Snowflake.

---

## ✅ Recommended Solution

We implement a **manual refresh button** using `st.button()`:

```python
if st.button("🔄 Refresh Status"):
    st.rerun()
