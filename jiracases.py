import sys
import requests
from requests.auth import HTTPBasicAuth
from zdesk import ZendeskError
from zdesk import Zendesk
sys.path.append('../')
import config as cfg

def jiracases(searchUrl, headers):
    data = requests.get(searchUrl, auth=headers).json()
    result_data = []
    zdo = Zendesk(**cfg.ZDC)

    for case in data['issues']:
        if 'customfield_0002' in case['fields'] and type(case['fields']['customfield_0002']) == str:
            article = case['fields']['customfield_0002'].replace("\n", "")
        else:
            article = "NA"

        if type(case['fields']['customfield_0001']) == str:
            ticketLink = "from ticket #https://SOME_URL/agent/tickets/" + \
                          case['fields']['customfield_0001'].split(',')[0]
        else:
            ticketLink = "with no ticket attached"

        if 'emailAddress' in case['fields']['reporter'] and type(case['fields']['reporter']['emailAddress']) == str:
            acct = case['fields']['reporter']['emailAddress']

#        zemail = zdo.search(f"type:user jira_username:{case['fields']['creator']['emailAddress']}")
        result_data.append({
            'agent_emails': acct,
            'date': case['fields']['created'][:-18],
            'subject': case['fields']['summary'].replace(',', ''),
            'body': f"Case #https://jira_URL/browse/{case['key']} {ticketLink}",
            'link': article,
            'type': "jira",
        })

    return result_data