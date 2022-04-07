#!/usr/bin/python3

import json
import sys

import requests
import typer
import os
import configparser
import base64
from prettytable import PrettyTable

app = typer.Typer()
servers_app = typer.Typer()
app.add_typer(servers_app, name='vds')


class Server:
    @staticmethod
    def get_list():
        url = 'https://public-api.timeweb.com/api/v2/vds'
        result = requests.get(
            url=url,
            headers=reqHeader
        )
        if not result.ok:
            return None
        return result.json()

    @staticmethod
    def start(vds_id):
        uri = "https://public-api.timeweb.com/api/v1/vds/{id}/{action}"
        result = requests.post(
            uri.format(id=vds_id, action='start'),
            headers=reqHeader
        )
        if not result.ok:
            return None
        else:
            return result.json()

    @staticmethod
    def stop(vds_id):
        uri = "https://public-api.timeweb.com/api/v1/vds/{id}/{action}"
        result = requests.post(
            uri.format(id=vds_id, action='shutdown'),
            headers=reqHeader
        )
        if not result.ok:
            return None
        else:
            return result.json()


@app.command("balance")
def get_balance():
    response = requests.get("https://public-api.timeweb.com/api/v1/accounts/finances", headers=reqHeader)
    if not response.ok:
        print(typer.style("Error", fg=typer.colors.RED))
        sys.exit(1)
    else:
        x = PrettyTable()
        x.field_names = ["Balance", "Monthly cost"]
        response = response.json()
        x.add_row([response['finances']['balance'], response['finances']['monthly_cost']])
        print(x)


@servers_app.command("start")
def vds_start(vds_id: int = typer.Argument(...)):
    result = Server.start(vds_id)
    if result is None:
        print(typer.style("Error", fg=typer.colors.RED))
        sys.exit(1)

    print(result)


@servers_app.command("stop")
def vds_stop(vds_id: int = typer.Argument(...)):
    result = Server.stop(vds_id)
    if result is None:
        print(typer.style("Error", fg=typer.colors.RED))
        sys.exit(1)

    print(result)


@servers_app.command("list")
def vds_list():
    list_of_servers = Server.get_list()
    x = PrettyTable()
    x.field_names = ['id', 'state', 'name', 'ip', 'cpus', 'ram', 'disk']
    if list_of_servers is None:
        print(typer.style("Error", fg=typer.colors.RED))
        sys.exit(1)
    for i in list_of_servers['servers']:
        if i['status'] == 'on':
            state = typer.style("Running", fg=typer.colors.GREEN)
        elif i['status'] == 'off':
            state = typer.style('Stopped', fg=typer.colors.RED)
        else:
            state = i['status']
        x.add_row([i['id'], state, i['name'], i['ip'], i['configuration']['cpu'], i['configuration']['ram'], i['configuration']['disk_size']])
        print(x)


def auth(based):
    """
    Get access token

    :param based:
    :return:
    """
    headers = {"Authorization": "Basic " + based}

    result = requests.post(
        'https://public-api.timeweb.com/api/v2/auth',
        json=dict(refresh_token="string"),
        headers=headers
    )
    if not result.ok:
        return None
    else:
        result = result.content.decode('utf-8')
        result = json.loads(result)
        result = result['access_token']
        return result


def get_api_key():
    config = configparser.ConfigParser()
    config.read(os.path.join(os.getenv('HOME'), '.config', 'twvdscli.ini'))
    based = config.get('api', 'key', fallback=None)
    if based is None:
        login = input("Enter login ")
        passwd = input("Enter passwd ")
        based = base64.b64encode(str(login + ":" + passwd).encode('utf-8'))
        based = based.decode('utf-8')

        config.add_section('api')
        config.set('api', 'key', based)

        with open(os.path.join(os.getenv('HOME'), '.config', 'twvdscli.ini'), 'w') as configfile:
            config.write(configfile)

    result = auth(based)
    return result


if __name__ == '__main__':
    apikey = get_api_key()
    if apikey is None:
        print(typer.style("Auth Error", fg=typer.colors.RED))
        sys.exit(1)
    reqHeader = {"Authorization": "Bearer " + apikey}

    app()
