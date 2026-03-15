--
-- PostgreSQL database dump
--

\restrict 6WJIDZrqH4ELqRwLQGT28naf4xbXXeeFl4kDiaC3IUAPOqUcNvi4ZJhYiIU8TAz

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
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;


--
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';


--
-- Name: interaction_channel; Type: TYPE; Schema: public; Owner: luxeFlow
--

CREATE TYPE public.interaction_channel AS ENUM (
    'Gmail',
    'WhatsApp',
    'WebForm'
);


ALTER TYPE public.interaction_channel OWNER TO "luxeFlow";

--
-- Name: loyalty_tier; Type: TYPE; Schema: public; Owner: luxeFlow
--

CREATE TYPE public.loyalty_tier AS ENUM (
    'Free',
    'Silver',
    'Gold',
    'Platinum'
);


ALTER TYPE public.loyalty_tier OWNER TO "luxeFlow";

--
-- Name: messagechannel; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.messagechannel AS ENUM (
    'WEB',
    'GMAIL',
    'WHATSAPP'
);


ALTER TYPE public.messagechannel OWNER TO postgres;

--
-- Name: messagesender; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.messagesender AS ENUM (
    'CUSTOMER',
    'AI',
    'AGENT'
);


ALTER TYPE public.messagesender OWNER TO postgres;

--
-- Name: sentiment_score; Type: TYPE; Schema: public; Owner: luxeFlow
--

CREATE TYPE public.sentiment_score AS ENUM (
    'Very Negative',
    'Negative',
    'Neutral',
    'Positive',
    'Very Positive'
);


ALTER TYPE public.sentiment_score OWNER TO "luxeFlow";

--
-- Name: ticket_priority; Type: TYPE; Schema: public; Owner: luxeFlow
--

CREATE TYPE public.ticket_priority AS ENUM (
    'Low',
    'Medium',
    'High',
    'Critical'
);


ALTER TYPE public.ticket_priority OWNER TO "luxeFlow";

--
-- Name: ticket_status; Type: TYPE; Schema: public; Owner: luxeFlow
--

CREATE TYPE public.ticket_status AS ENUM (
    'Open',
    'Pending',
    'Escalated',
    'Resolved'
);


ALTER TYPE public.ticket_status OWNER TO "luxeFlow";

--
-- Name: ticketcategory; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.ticketcategory AS ENUM (
    'TECHNICAL_SUPPORT',
    'BILLING',
    'GENERAL_INQUIRY',
    'FEATURE_REQUEST',
    'BUG_REPORT',
    'ACCOUNT_ISSUE'
);


ALTER TYPE public.ticketcategory OWNER TO postgres;

--
-- Name: ticketpriority; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.ticketpriority AS ENUM (
    'LOW',
    'MEDIUM',
    'HIGH',
    'CRITICAL'
);


ALTER TYPE public.ticketpriority OWNER TO postgres;

--
-- Name: ticketstatus; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.ticketstatus AS ENUM (
    'OPEN',
    'IN_PROGRESS',
    'RESOLVED'
);


ALTER TYPE public.ticketstatus OWNER TO postgres;

--
-- Name: generate_ticket_number(); Type: FUNCTION; Schema: public; Owner: luxeFlow
--

CREATE FUNCTION public.generate_ticket_number() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.ticket_number := 'TKT-' || TO_CHAR(NEW.created_at, 'YYYYMMDD') || '-' || LPAD(NEW.id::text, 6, '0');
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.generate_ticket_number() OWNER TO "luxeFlow";

--
-- Name: update_updated_at_column(); Type: FUNCTION; Schema: public; Owner: luxeFlow
--

CREATE FUNCTION public.update_updated_at_column() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_updated_at_column() OWNER TO "luxeFlow";

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: agents; Type: TABLE; Schema: public; Owner: luxeFlow
--

CREATE TABLE public.agents (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    email character varying(255) NOT NULL,
    full_name character varying(255) NOT NULL,
    role character varying(100) NOT NULL,
    escalation_level integer DEFAULT 1 NOT NULL,
    is_active boolean DEFAULT true,
    max_concurrent_tickets integer DEFAULT 10,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.agents OWNER TO "luxeFlow";

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO postgres;

--
-- Name: audit_log; Type: TABLE; Schema: public; Owner: luxeFlow
--

CREATE TABLE public.audit_log (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    event_type character varying(100) NOT NULL,
    entity_type character varying(50) NOT NULL,
    entity_id uuid NOT NULL,
    actor_type character varying(50) NOT NULL,
    actor_id uuid,
    old_values jsonb,
    new_values jsonb,
    ip_address inet,
    user_agent text,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.audit_log OWNER TO "luxeFlow";

--
-- Name: customers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.customers (
    id character varying(36) NOT NULL,
    name character varying(255) NOT NULL,
    email character varying(255) NOT NULL,
    phone character varying(20),
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.customers OWNER TO postgres;

--
-- Name: COLUMN customers.phone; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.customers.phone IS 'WhatsApp phone number';


--
-- Name: escalation_log; Type: TABLE; Schema: public; Owner: luxeFlow
--

CREATE TABLE public.escalation_log (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    ticket_id uuid NOT NULL,
    from_level integer NOT NULL,
    to_level integer NOT NULL,
    reason character varying(500) NOT NULL,
    trigger_type character varying(50) NOT NULL,
    notified_agents jsonb DEFAULT '[]'::jsonb,
    notification_sent_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    resolved_by uuid,
    resolved_at timestamp with time zone,
    resolution_notes text,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.escalation_log OWNER TO "luxeFlow";

--
-- Name: event_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.event_logs (
    id character varying(64) NOT NULL,
    "timestamp" character varying(32) NOT NULL,
    event_type character varying(50) NOT NULL,
    channel character varying(20) NOT NULL,
    ticket_id character varying(36),
    customer_id character varying(36),
    message_id character varying(36),
    log_level character varying(10) NOT NULL,
    metadata jsonb
);


ALTER TABLE public.event_logs OWNER TO postgres;

--
-- Name: knowledge_base; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.knowledge_base (
    id character varying(36) NOT NULL,
    content_chunk text NOT NULL,
    embedding text,
    kb_metadata jsonb,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.knowledge_base OWNER TO postgres;

--
-- Name: COLUMN knowledge_base.content_chunk; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.knowledge_base.content_chunk IS 'Text content chunk for RAG';


--
-- Name: COLUMN knowledge_base.embedding; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.knowledge_base.embedding IS 'Vector embedding for semantic search (stored as text)';


--
-- Name: COLUMN knowledge_base.kb_metadata; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.knowledge_base.kb_metadata IS 'Additional metadata (source, tags, etc.)';


--
-- Name: messages; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.messages (
    id character varying(36) NOT NULL,
    ticket_id character varying(36) NOT NULL,
    sender public.messagesender NOT NULL,
    content text NOT NULL,
    channel public.messagechannel NOT NULL,
    "timestamp" timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.messages OWNER TO postgres;

--
-- Name: tickets; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tickets (
    id character varying(36) NOT NULL,
    customer_id character varying(36) NOT NULL,
    subject character varying(500) NOT NULL,
    status public.ticketstatus NOT NULL,
    priority public.ticketpriority NOT NULL,
    category public.ticketcategory NOT NULL,
    assigned_agent_id character varying(36),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.tickets OWNER TO postgres;

--
-- Name: COLUMN tickets.assigned_agent_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.tickets.assigned_agent_id IS 'ID of the assigned support agent';


--
-- Name: agents agents_email_key; Type: CONSTRAINT; Schema: public; Owner: luxeFlow
--

ALTER TABLE ONLY public.agents
    ADD CONSTRAINT agents_email_key UNIQUE (email);


--
-- Name: agents agents_pkey; Type: CONSTRAINT; Schema: public; Owner: luxeFlow
--

ALTER TABLE ONLY public.agents
    ADD CONSTRAINT agents_pkey PRIMARY KEY (id);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: audit_log audit_log_pkey; Type: CONSTRAINT; Schema: public; Owner: luxeFlow
--

ALTER TABLE ONLY public.audit_log
    ADD CONSTRAINT audit_log_pkey PRIMARY KEY (id);


--
-- Name: escalation_log escalation_log_pkey; Type: CONSTRAINT; Schema: public; Owner: luxeFlow
--

ALTER TABLE ONLY public.escalation_log
    ADD CONSTRAINT escalation_log_pkey PRIMARY KEY (id);


--
-- Name: customers pk_customers; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.customers
    ADD CONSTRAINT pk_customers PRIMARY KEY (id);


--
-- Name: event_logs pk_event_logs; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.event_logs
    ADD CONSTRAINT pk_event_logs PRIMARY KEY (id);


--
-- Name: knowledge_base pk_knowledge_base; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.knowledge_base
    ADD CONSTRAINT pk_knowledge_base PRIMARY KEY (id);


--
-- Name: messages pk_messages; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT pk_messages PRIMARY KEY (id);


--
-- Name: tickets pk_tickets; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tickets
    ADD CONSTRAINT pk_tickets PRIMARY KEY (id);


--
-- Name: idx_agents_active; Type: INDEX; Schema: public; Owner: luxeFlow
--

CREATE INDEX idx_agents_active ON public.agents USING btree (is_active) WHERE (is_active = true);


--
-- Name: idx_agents_escalation_level; Type: INDEX; Schema: public; Owner: luxeFlow
--

CREATE INDEX idx_agents_escalation_level ON public.agents USING btree (escalation_level);


--
-- Name: idx_audit_log_created_at; Type: INDEX; Schema: public; Owner: luxeFlow
--

CREATE INDEX idx_audit_log_created_at ON public.audit_log USING btree (created_at DESC);


--
-- Name: idx_audit_log_entity; Type: INDEX; Schema: public; Owner: luxeFlow
--

CREATE INDEX idx_audit_log_entity ON public.audit_log USING btree (entity_type, entity_id);


--
-- Name: idx_audit_log_event_type; Type: INDEX; Schema: public; Owner: luxeFlow
--

CREATE INDEX idx_audit_log_event_type ON public.audit_log USING btree (event_type);


--
-- Name: idx_escalation_log_created_at; Type: INDEX; Schema: public; Owner: luxeFlow
--

CREATE INDEX idx_escalation_log_created_at ON public.escalation_log USING btree (created_at DESC);


--
-- Name: idx_escalation_log_ticket_id; Type: INDEX; Schema: public; Owner: luxeFlow
--

CREATE INDEX idx_escalation_log_ticket_id ON public.escalation_log USING btree (ticket_id);


--
-- Name: idx_escalation_log_trigger_type; Type: INDEX; Schema: public; Owner: luxeFlow
--

CREATE INDEX idx_escalation_log_trigger_type ON public.escalation_log USING btree (trigger_type);


--
-- Name: ix_customers_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_customers_email ON public.customers USING btree (email);


--
-- Name: ix_customers_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_customers_id ON public.customers USING btree (id);


--
-- Name: ix_customers_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_customers_name ON public.customers USING btree (name);


--
-- Name: ix_event_logs_channel; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_event_logs_channel ON public.event_logs USING btree (channel);


--
-- Name: ix_event_logs_channel_timestamp; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_event_logs_channel_timestamp ON public.event_logs USING btree (channel, "timestamp");


--
-- Name: ix_event_logs_customer_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_event_logs_customer_id ON public.event_logs USING btree (customer_id);


--
-- Name: ix_event_logs_event_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_event_logs_event_type ON public.event_logs USING btree (event_type);


--
-- Name: ix_event_logs_log_level; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_event_logs_log_level ON public.event_logs USING btree (log_level);


--
-- Name: ix_event_logs_ticket_customer; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_event_logs_ticket_customer ON public.event_logs USING btree (ticket_id, customer_id);


--
-- Name: ix_event_logs_ticket_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_event_logs_ticket_id ON public.event_logs USING btree (ticket_id);


--
-- Name: ix_event_logs_timestamp; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_event_logs_timestamp ON public.event_logs USING btree ("timestamp");


--
-- Name: ix_knowledge_base_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_knowledge_base_id ON public.knowledge_base USING btree (id);


--
-- Name: ix_messages_channel; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_messages_channel ON public.messages USING btree (channel);


--
-- Name: ix_messages_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_messages_id ON public.messages USING btree (id);


--
-- Name: ix_messages_sender; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_messages_sender ON public.messages USING btree (sender);


--
-- Name: ix_messages_ticket_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_messages_ticket_id ON public.messages USING btree (ticket_id);


--
-- Name: ix_messages_timestamp; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_messages_timestamp ON public.messages USING btree ("timestamp");


--
-- Name: ix_tickets_assigned_agent_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tickets_assigned_agent_id ON public.tickets USING btree (assigned_agent_id);


--
-- Name: ix_tickets_category; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tickets_category ON public.tickets USING btree (category);


--
-- Name: ix_tickets_customer_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tickets_customer_id ON public.tickets USING btree (customer_id);


--
-- Name: ix_tickets_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tickets_id ON public.tickets USING btree (id);


--
-- Name: ix_tickets_priority; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tickets_priority ON public.tickets USING btree (priority);


--
-- Name: ix_tickets_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tickets_status ON public.tickets USING btree (status);


--
-- Name: agents update_agents_updated_at; Type: TRIGGER; Schema: public; Owner: luxeFlow
--

CREATE TRIGGER update_agents_updated_at BEFORE UPDATE ON public.agents FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: escalation_log escalation_log_resolved_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: luxeFlow
--

ALTER TABLE ONLY public.escalation_log
    ADD CONSTRAINT escalation_log_resolved_by_fkey FOREIGN KEY (resolved_by) REFERENCES public.agents(id);


--
-- Name: messages fk_messages_ticket_id_tickets; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT fk_messages_ticket_id_tickets FOREIGN KEY (ticket_id) REFERENCES public.tickets(id) ON DELETE CASCADE;


--
-- Name: tickets fk_tickets_customer_id_customers; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tickets
    ADD CONSTRAINT fk_tickets_customer_id_customers FOREIGN KEY (customer_id) REFERENCES public.customers(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict 6WJIDZrqH4ELqRwLQGT28naf4xbXXeeFl4kDiaC3IUAPOqUcNvi4ZJhYiIU8TAz

