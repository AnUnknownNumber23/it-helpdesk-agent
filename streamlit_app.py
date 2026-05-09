import streamlit as st

import requests

from app.schemas.ticket import TicketCategory, TicketPriority, TicketStatus
from app.ui.streamlit_client import (
    API_BASE,
    ask_agent,
    ask_rag,
    fetch_ticket_stats,
    fetch_tickets,
    get_ticket,
    ingest_markdown,
    parse_response_payload,
    update_ticket,
)


st.set_page_config(page_title="Enterprise IT Helpdesk Agent")
st.title("Enterprise IT Helpdesk Agent")
st.caption("Upload Markdown for the knowledge base, ask RAG directly, or use the Agent workflow for a full helpdesk response.")

tab_ingest, tab_rag, tab_agent, tab_tickets, tab_dashboard = st.tabs(
    ["Ingest", "RAG", "Agent", "Tickets", "Dashboard"]
)

with tab_ingest:
    st.subheader("Upload Markdown")
    uploaded_file = st.file_uploader("Choose a Markdown file", type=["md"])

    if st.button("Ingest", use_container_width=True):
        if uploaded_file is None:
            st.warning("Please choose a Markdown file before ingesting.")
        else:
            try:
                response, payload = ingest_markdown(uploaded_file, api_base=API_BASE)
                if response.status_code == 200:
                    if isinstance(payload, dict):
                        st.success(payload.get("message", "Ingest succeeded."))
                        st.json(
                            {
                                "file": payload.get("file"),
                                "file_path": payload.get("file_path"),
                                "chunks": payload.get("chunks"),
                            }
                        )
                    else:
                        st.success("Ingest succeeded.")
                        st.write(payload)
                else:
                    st.error(f"Ingest failed ({response.status_code})")
                    if isinstance(payload, (dict, list)):
                        st.json(payload)
                    else:
                        st.write(payload)
            except requests.RequestException as exc:
                st.error(f"Could not reach backend API: {exc}")

with tab_rag:
    st.subheader("Ask RAG")
    question = st.text_input("Question", placeholder="What does the uploaded document say about RAG?")

    if st.button("Ask RAG", use_container_width=True):
        stripped_question = question.strip()
        if not stripped_question:
            st.warning("Please enter a question before asking.")
        elif len(stripped_question) < 3:
            st.warning("Question must be at least 3 characters.")
        else:
            try:
                response, payload = ask_rag(stripped_question, api_base=API_BASE)
                if response.status_code == 200:
                    if isinstance(payload, dict):
                        st.markdown("### Answer")
                        st.write(payload.get("answer"))
                        st.markdown("### Citations")
                        citations = payload.get("citations") or []
                        if citations:
                            for citation in citations:
                                st.markdown(f"- **{citation['source']}**: {citation['snippet']}")
                        else:
                            st.info("No citations returned.")
                    else:
                        st.markdown("### Answer")
                        st.write(payload)
                else:
                    st.error(f"Ask failed ({response.status_code})")
                    if isinstance(payload, (dict, list)):
                        st.json(payload)
                    else:
                        st.write(payload)
            except requests.RequestException as exc:
                st.error(f"Could not reach backend API: {exc}")

with tab_agent:
    st.subheader("Ask IT Agent")
    agent_question = st.text_input("Agent Question", placeholder="I cannot access GitLab and need help.")

    if st.button("Ask Agent", use_container_width=True):
        stripped_question = agent_question.strip()
        if not stripped_question:
            st.warning("Please enter a question before asking.")
        elif len(stripped_question) < 3:
            st.warning("Question must be at least 3 characters.")
        else:
            try:
                response, payload = ask_agent(stripped_question, api_base=API_BASE)
                if response.status_code == 200 and isinstance(payload, dict):
                    st.markdown("### Decision")
                    st.json(payload.get("decision"))
                    st.markdown("### Answer")
                    st.write(payload.get("answer"))
                    st.markdown("### Citations")
                    citations = payload.get("citations") or []
                    if citations:
                        for citation in citations:
                            st.markdown(f"- **{citation['source']}**: {citation['snippet']}")
                    else:
                        st.info("No citations returned.")
                    ticket = payload.get("ticket")
                    if ticket:
                        st.markdown("### Ticket")
                        st.json(ticket)
                else:
                    st.error(f"Agent request failed ({response.status_code})")
                    if isinstance(payload, (dict, list)):
                        st.json(payload)
                    else:
                        st.write(payload)
            except requests.RequestException as exc:
                st.error(f"Could not reach backend API: {exc}")

with tab_tickets:
    st.subheader("Tickets")
    status_options = ["All"] + [status.value for status in TicketStatus]
    category_options = ["All"] + [category.value for category in TicketCategory]
    priority_options = ["All"] + [priority.value for priority in TicketPriority]

    filter_columns = st.columns(3)
    selected_status = filter_columns[0].selectbox("Status", status_options)
    selected_category = filter_columns[1].selectbox("Category", category_options)
    selected_priority = filter_columns[2].selectbox("Priority", priority_options)

    params = {}
    if selected_status != "All":
        params["status"] = selected_status
    if selected_category != "All":
        params["category"] = selected_category
    if selected_priority != "All":
        params["priority"] = selected_priority

    try:
        tickets_response, tickets_payload = fetch_tickets(params=params, api_base=API_BASE)
        if tickets_response.status_code == 200 and isinstance(tickets_payload, list):
            if tickets_payload:
                display_rows = [
                    {
                        "id": ticket.get("id"),
                        "title": ticket.get("title"),
                        "status": ticket.get("status"),
                        "category": ticket.get("category"),
                        "priority": ticket.get("priority"),
                        "updated_at": ticket.get("updated_at"),
                    }
                    for ticket in tickets_payload
                ]
                st.dataframe(display_rows, use_container_width=True, hide_index=True)

                ticket_ids = [ticket["id"] for ticket in tickets_payload if ticket.get("id")]
                selected_ticket_id = st.selectbox("Inspect ticket", ticket_ids)

                detail_response, detail_payload = get_ticket(selected_ticket_id, api_base=API_BASE)
                if detail_response.status_code == 200 and isinstance(detail_payload, dict):
                    st.markdown("### Ticket Detail")
                    st.json(detail_payload)

                    current_status = detail_payload.get("status", TicketStatus.OPEN.value)
                    current_priority = detail_payload.get("priority", TicketPriority.MEDIUM.value)
                    current_resolution = detail_payload.get("resolution_note") or ""

                    with st.form(f"ticket_update_{selected_ticket_id}"):
                        update_status = st.selectbox(
                            "Status",
                            [status.value for status in TicketStatus],
                            index=[status.value for status in TicketStatus].index(current_status)
                            if current_status in [status.value for status in TicketStatus]
                            else 0,
                        )
                        update_priority = st.selectbox(
                            "Priority",
                            [priority.value for priority in TicketPriority],
                            index=[priority.value for priority in TicketPriority].index(current_priority)
                            if current_priority in [priority.value for priority in TicketPriority]
                            else 1,
                        )
                        resolution_note = st.text_area("Resolution note", value=current_resolution, height=120)
                        save_update = st.form_submit_button("Save Update")

                    if save_update:
                        try:
                            update_response, update_payload = update_ticket(
                                selected_ticket_id,
                                {
                                    "status": update_status,
                                    "priority": update_priority,
                                    "resolution_note": resolution_note,
                                },
                                api_base=API_BASE,
                            )
                            if update_response.status_code == 200 and isinstance(update_payload, dict):
                                st.success("Ticket updated.")
                                st.json(update_payload)
                            else:
                                st.error(f"Ticket update failed ({update_response.status_code})")
                                st.json(update_payload)
                        except requests.RequestException as exc:
                            st.error(f"Could not reach backend API: {exc}")
                else:
                    st.error(f"Ticket detail failed ({detail_response.status_code})")
                    if isinstance(detail_payload, (dict, list)):
                        st.json(detail_payload)
                    else:
                        st.write(detail_payload)
            else:
                st.info("No tickets found for the selected filters.")
        else:
            st.error(f"Ticket list failed ({tickets_response.status_code})")
            if isinstance(tickets_payload, (dict, list)):
                st.json(tickets_payload)
            else:
                st.write(tickets_payload)
    except requests.RequestException as exc:
        st.error(f"Could not reach backend API: {exc}")

with tab_dashboard:
    st.subheader("Dashboard")
    try:
        stats_response, stats_payload = fetch_ticket_stats(api_base=API_BASE)
        if stats_response.status_code == 200 and isinstance(stats_payload, dict):
            total = stats_payload.get("total", 0)
            by_status = stats_payload.get("by_status") or {}
            by_category = stats_payload.get("by_category") or {}
            by_priority = stats_payload.get("by_priority") or {}

            metric_columns = st.columns(3)
            metric_columns[0].metric("Total Tickets", total)
            metric_columns[1].metric("Open Tickets", by_status.get("open", 0))
            metric_columns[2].metric("Resolved Tickets", by_status.get("resolved", 0))

            st.markdown("### By Status")
            st.bar_chart(by_status)
            st.markdown("### By Category")
            st.bar_chart(by_category)
            st.markdown("### By Priority")
            st.bar_chart(by_priority)
        else:
            st.error(f"Dashboard data failed ({stats_response.status_code})")
            if isinstance(stats_payload, (dict, list)):
                st.json(stats_payload)
            else:
                st.write(stats_payload)
    except requests.RequestException as exc:
        st.error(f"Could not reach backend API: {exc}")
