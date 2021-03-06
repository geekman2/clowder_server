from django.db import connection
from django.db import models

class Base(models.Model):
    name = models.CharField(max_length=200)
    ip_address = models.GenericIPAddressField()
    company = models.ForeignKey('clowder_account.Company', null=True)
    create = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class Alert(Base):
    """
    An alert is an alarm.
    Alerts with a notify_at value are consider future alerts.
    Alerts without a notify_at are considered failing.
    """

    notify_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = (
            ('company', 'name'),
        )

class Ping(Base):
    """
    A ping is created every time a service contacts Clowder
    A ping has a value attached that is used for graphing.
    The value can be boolean or integer or float.
    A ping also has a status.
    If a status is not explicitly passed, then a -1 is assumed to be failing
    """

    value = models.FloatField()
    public = models.BooleanField(default=False)
    status_passing = models.BooleanField(default=True)

    class Meta:
        index_together = (
            ('company', 'name'),
        )

    def get_closest_alert(self):
        return None
        return Alert.objects.filter(
            name=self.name,
            ip_address=self.ip_address,
            company=self.company,
        ).order_by('notify_at').first()

    @classmethod
    def num_passing(cls, company_id):
        cursor = connection.cursor()
        cursor.execute('''
        SELECT COUNT(*) FROM (
          SELECT
            clowder_server_ping.name,
            rank() OVER (PARTITION BY clowder_server_ping.name ORDER BY clowder_server_ping.create DESC) as rank,
            status_passing
          FROM clowder_server_ping
          WHERE clowder_server_ping.company_id = %s
        ) AS q1
          WHERE status_passing = true
          AND rank = 1;
        ''', [company_id])
        result = cursor.fetchone()
        return result[0] if result else 0

    @classmethod
    def num_failing(cls, company_id):
        cursor = connection.cursor()
        cursor.execute('''
        SELECT COUNT(*) FROM (
          SELECT
            clowder_server_ping.name,
            rank() OVER (PARTITION BY clowder_server_ping.name ORDER BY clowder_server_ping.create DESC) as rank,
            status_passing
          FROM clowder_server_ping
          WHERE clowder_server_ping.company_id = %s
        ) AS q1
          WHERE status_passing = false
          AND rank = 1;
        ''', [company_id])
        result = cursor.fetchone()
        return result[0] if result else 0
