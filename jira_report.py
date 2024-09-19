import csv

from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.utils.timezone import now

import jiracases
from mail.notifier import notify

import config as cfg

BASE_URL = "https://atlassian.net/rest/api/2/search?jql="
FIELDS = [
    "key",
    "summary",
    "reporter",
    "customfield_0001",  # TicketID
    "customfield_0002",  # Documentation
    "created"
]
FILTER = "00000"


class Command(BaseCommand):
    help = 'Prepares JIRA Cases CSV file for QA'

    def add_arguments(self, parser):
        parser.add_argument('--file', '-f', dest='fname', help="Report file name")
        parser.add_argument('--send-to', nargs='+', dest='send', help="Send report to")
        parser.add_argument('--cc', nargs='+', help="CC Email Address")

    def handle(self, *args, **options):
        self.stdout.write(f"[{now():%Y-%m-%d %H:%M:%S}] Creating JIRA report")
        url = BASE_URL + "filter=" + FILTER + "&fields=" + ','.join(FIELDS)
        filename = f"jira_{now().strftime('%Y%m%d')}.csv" if not options['fname'] else options['fname']
        try:
            data = jiracases(url, (cfg.JIRA_USER,cfg.JIRA_TOKEN))
        except Exception as err:
            notify('JIRA Report FAILED on jiracases() call',
                   render_to_string('mail/mail_failure_report.html', {'exception': err}),
                   to=['', ''])
            return

        if not data:
            notify('JIRA Report FAILED with empty data from JIRA',
                   render_to_string('mail/mail_failure_report.html'),
                   to=[''])
            return

        with open(filename, mode='w', newline='', encoding='utf-8') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=data[0].keys())
            writer.writeheader()
            for record in data:
                writer.writerow(record)

        if options['send']:
            notify(f"JIRA Report {now():%Y-%m-%d}",
                   render_to_string('mail/mail_mqa_report.html'),
                   to=options['send'], cc=options['cc'], attach=filename)
            self.stdout.write(f"  mail sent")

        self.stdout.write(f"[{now():%Y-%m-%d %H:%M:%S}] Done")
        return
