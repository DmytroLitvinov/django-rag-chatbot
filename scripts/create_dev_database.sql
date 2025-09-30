/*
This file is used to bootstrap development database locally.

Note: ONLY development database;
*/

CREATE USER "django-rag-chatbot" SUPERUSER;
CREATE DATABASE "django-rag-chatbot" OWNER "django-rag-chatbot" ENCODING 'utf-8';
