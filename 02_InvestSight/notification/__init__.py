"""
InvestSight Notification Package
"""
from .email import (
    EmailNotifier,
    EmailConfig,
    EmailTemplate,
    SMTPEmailSender,
    GraphEmailSender,
    send_email,
    send_daily_report,
    notifier as email_notifier,
)
from .teams import (
    TeamsNotifier,
    TeamsWebhookSender,
    TeamsGraphSender,
    send_teams,
    send_price_alert,
    notifier as teams_notifier,
)

__all__ = [
    # Email
    'EmailNotifier',
    'EmailConfig', 
    'EmailTemplate',
    'SMTPEmailSender',
    'GraphEmailSender',
    'send_email',
    'send_daily_report',
    'email_notifier',
    # Teams
    'TeamsNotifier',
    'TeamsWebhookSender',
    'TeamsGraphSender',
    'send_teams',
    'send_price_alert',
    'teams_notifier',
]
