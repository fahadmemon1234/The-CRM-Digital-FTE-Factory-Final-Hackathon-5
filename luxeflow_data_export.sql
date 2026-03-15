--
-- PostgreSQL database dump
--

\restrict Kioueam3UOWxwHEkUm4BNcx8Z64Sc9ZyDOpqzcFvR4c33mmfT0z4eapTjoriwsb

-- Dumped from database version 16.13
-- Dumped by pg_dump version 16.13

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: agents; Type: TABLE DATA; Schema: public; Owner: luxeFlow
--

COPY public.agents (id, email, full_name, role, escalation_level, is_active, max_concurrent_tickets, created_at, updated_at) FROM stdin;
15a89078-a20e-46ff-ae06-600b8ff044f5	agent1@luxeflow.ai	Sarah Johnson	Support	1	t	10	2026-03-08 13:06:34.824868+05	2026-03-08 13:06:34.824868+05
a25e90bb-02f9-4b1b-a15f-b2d6ce00a653	agent2@luxeflow.ai	Michael Chen	Senior Support	2	t	10	2026-03-08 13:06:34.824868+05	2026-03-08 13:06:34.824868+05
2fbee070-de15-45c5-9f2c-c30304ff1913	manager1@luxeflow.ai	Emily Rodriguez	Manager	3	t	10	2026-03-08 13:06:34.824868+05	2026-03-08 13:06:34.824868+05
\.


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.alembic_version (version_num) FROM stdin;
002_add_event_logs
\.


--
-- Data for Name: audit_log; Type: TABLE DATA; Schema: public; Owner: luxeFlow
--

COPY public.audit_log (id, event_type, entity_type, entity_id, actor_type, actor_id, old_values, new_values, ip_address, user_agent, created_at) FROM stdin;
\.


--
-- Data for Name: customers; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.customers (id, name, email, phone, created_at) FROM stdin;
\.


--
-- Data for Name: escalation_log; Type: TABLE DATA; Schema: public; Owner: luxeFlow
--

COPY public.escalation_log (id, ticket_id, from_level, to_level, reason, trigger_type, notified_agents, notification_sent_at, resolved_by, resolved_at, resolution_notes, created_at) FROM stdin;
\.


--
-- Data for Name: event_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.event_logs (id, "timestamp", event_type, channel, ticket_id, customer_id, message_id, log_level, metadata) FROM stdin;
\.


--
-- Data for Name: knowledge_base; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.knowledge_base (id, content_chunk, embedding, kb_metadata, created_at) FROM stdin;
\.


--
-- Data for Name: tickets; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tickets (id, customer_id, subject, status, priority, category, assigned_agent_id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: messages; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.messages (id, ticket_id, sender, content, channel, "timestamp") FROM stdin;
\.


--
-- PostgreSQL database dump complete
--

\unrestrict Kioueam3UOWxwHEkUm4BNcx8Z64Sc9ZyDOpqzcFvR4c33mmfT0z4eapTjoriwsb

