from django.apps import AppConfig


class AgentCrmConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.agent_crm"
    def ready(self):
        import apps.agent_crm.signals
