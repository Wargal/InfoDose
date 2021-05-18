import json
import sys

import requests

print_in_console = False

def get_dose_json(dept_number):
    response = requests.get(
        "https://vitemadose.gitlab.io/vitemadose/" + str(dept_number) + ".json"
    )
    json = response.json()
    return json


def get_centres(json):
    return json["centres_disponibles"]


def send_alert(content, e_title, e_desc, e_url, webhook_url):
    data = {"content": content, "username": "RapidoseInfo","avatar_url"=
            "embeds": [{"description": e_desc, "title": e_title, "url": e_url}]}
    result = requests.post(webhook_url, json=data)
    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        if print_in_console:
            print(err)
    else:
        if print_in_console:
            print("Payload delivered successfully, code {}.".format(result.status_code))


with open(
        "webhooks.json",
        "r",
) as f:
    webhooks = json.load(f)
    for i in range(1, 96):
        try:
            key = f'{i:02d}'
            webhook_url = webhooks[key]
            centres = get_centres(get_dose_json(f'{i:02d}'))
            for centre in centres:
                nom = centre["nom"]
                rdvs = centre["appointment_schedules"]
                for rdv in rdvs:
                    if rdv["name"] == "chronodose" and rdv["total"] != 0:
                        if print_in_console:
                            print(str(rdv["total"]) + " créneaux disponibles au centre " + nom)
                            print(centre["url"])
                        e_desc = str(rdv["total"]) + " créneaux disponibles"
                        content = "Dose de vaccin disponible"
                        send_alert(content, nom, e_desc, centre["url"], webhook_url)
        except:
            if print_in_console:
                e = sys.exc_info()[0]
                print(e)
            else:
                pass

