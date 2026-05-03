# Expense_log_analytics
A platform for making logs of transactions and analyzing expenses using dashboards


This repository provides two distinct front-end implementations running over a unified local database architecture[cite: 1, 2]:
1. A **Web Application** built with [Streamlit](https://streamlit.io/)[cite: 1].
2. A **Cross-Platform Application** built with [Flet](https://flet.dev/)[cite: 2].

---

Project Overview:
This is a high-performance personal wealth management system that utilizes a dual-interface architecture to provide users with a cross-platform financial tracking experience. The project is designed with a mobile-first philosophy, prioritizing a dark glassmorphism aesthetic while maintaining a robust, offline-first backend for complete data privacy.  Technical Architecture and StackThe application leverages a modular Python-based stack to handle data persistence, processing, and visualization across different environments:
Data Persistence: A localized SQLite architecture manages all transactional data through wealth_manager.db.  
Web Framework: finance_app.py is built using Streamlit, featuring custom CSS injections for advanced UI styling and Inter typography.  
Application Framework: flet_main.py utilizes the Flet framework to provide a responsive, native-feeling application experience for desktop and mobile aspect ratios.  
Data Analysis: The system employs Pandas for complex data aggregations and filtering, specifically for monthly and categorical breakdowns.  
Visual Intelligence: Interactive charts are rendered via Plotly Express and Plotly Graph Objects in the web view, while the Flet implementation uses native vector-based pie charts.  
Core Technical Features:
The project incorporates sophisticated financial logic and UI components to assist with personal budgeting and wealth tracking:Unified CRUD Operations: Both interface files execute synchronized Create, Read, and Delete operations on the shared transactions table.  
Intelligent Savings Advisor: The backend logic evaluates spending against the 50/30/20 rule, categorizing expenses into "Needs" (Housing, Food, Transport, Utilities, Healthcare) and "Wants" (Entertainment, Other). 
Dynamic KPI Rendering: Real-time calculation of Income, Expenses, Net Balance, and Savings Rate percentages. 
Advanced Visualizations: Includes daily spending bar charts, categorical expense pie charts, and a gauge indicator for savings targets.  
State Management: Implements session state resets in Streamlit and asynchronous UI refreshing in Flet to ensure data consistency during transaction logging.  Database Schema SpecificationThe underlying database, wealth_manager.db, contains a primary transactions table with an idempotent initialization routine. 

The table structure includes:  
id: An auto-incrementing integer serving as the primary key.  
date: A text-based field storing dates in YYYY-MM-DD format for chronological sorting.  
description: A text field for user-defined transaction labels.  
category: A standardized text field restricted to pre-defined financial buckets. 
type: A text descriptor identifying the entry as either "Income" or "Expense".  
amount: A real-number field for precise financial values.  Implementation DetailsThe system is split into two primary execution entry points to accommodate different user workflows:
Web Dashboard (finance_app.py): Designed for deep analysis, this interface uses a tabbed layout to separate the dashboard, transaction entry, and log management sections. 
Mobile/Desktop App (flet_main.py): Optimized for quick entry, this implementation uses glass-card containers and linear gradients to provide a high-fidelity mobile experience with integrated date-grouped logging.  
