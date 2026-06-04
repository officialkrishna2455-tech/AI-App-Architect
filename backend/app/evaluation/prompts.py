from typing import Optional

PROMPTS = {
    # Production prompts (1-10)
    1: ("production", "Build a CRM with login, contacts, dashboard, role-based access, premium plans, payments, and analytics."),
    2: ("production", "Create an e-commerce platform with products, categories, shopping cart, checkout, order tracking, and admin panel."),
    3: ("production", "Build a project management tool with tasks, sprints, team members, kanban board, and time tracking."),
    4: ("production", "Design a social media app with posts, comments, likes, followers, notifications, and content moderation."),
    5: ("production", "Create a healthcare management system with patients, appointments, prescriptions, doctors, and medical records."),
    6: ("production", "Build a learning management system with courses, lessons, quizzes, enrollments, certificates, and instructor dashboards."),
    7: ("production", "Design a real estate platform with listings, agents, virtual tours, mortgage calculator, and saved searches."),
    8: ("production", "Create a restaurant management system with menu, orders, reservations, tables, kitchen display, and delivery tracking."),
    9: ("production", "Build a job board with postings, applications, company profiles, resume parsing, and interview scheduling."),
    10: ("production", "Design a SaaS billing platform with subscriptions, invoices, usage metering, payment methods, and revenue analytics."),
    
    # Adversarial prompts (11-20)
    11: ("adversarial", ""),
    12: ("adversarial", "Build everything"),
    13: ("adversarial", "Create a system where admins are also regular users but cannot access admin features"),
    14: ("adversarial", "Build an app with login but no users"),
    15: ("adversarial", "Create 500 microservices with real-time sync"),
    16: ("adversarial", "Build a CRM. Build a CRM. Build a CRM."),
    17: ("adversarial", "Build a system using blockchain, quantum computing, and telepathy"),
    18: ("adversarial", "SELECT * FROM users; DROP TABLE users;--"),
    19: ("adversarial", "Build an app where free users get premium features and premium users get nothing"),
    20: ("adversarial", "asdfjkl;qwer zxcv poiuy")
}

class EvaluationPrompts:
    @staticmethod
    def get_prompt(id: int) -> tuple[Optional[str], Optional[str]]:
        """Returns (prompt_type, prompt_text)"""
        return PROMPTS.get(id, (None, None))

    @staticmethod
    def get_all() -> list[tuple[int, str, str]]:
        """Returns list of (id, type, text)"""
        return [(pid, p_type, p_text) for pid, (p_type, p_text) in PROMPTS.items()]
