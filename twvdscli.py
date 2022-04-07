#!/usr/bin/python3

import json
import sys
import requests
import typer
import os
import configparser
import base64
from prettytable import PrettyTable
from typing import Optional

# For spinning wheel
from itertools import cycle
from time import sleep


app = typer.Typer()
servers_app = typer.Typer()
app.add_typer(servers_app, name='vds')


class Server:
    """
    Not a server, but a backend.
    Everything that works directly with API is here.
    """

    @staticmethod
    def get_list():
        """
        Get list of VDSs'
        """
        url = 'https://public-api.timeweb.com/api/v2/vds'
        result = requests.get(
            url=url,
            headers=reqHeader
        )
        if not result.ok:
            return None
        return result.json()

    @staticmethod
    def get_vds(vds_id):
        """
        Get VDS info
        """
        url = "https://public-api.timeweb.com/api/v2/vds/{vds_id}".format(vds_id=vds_id)
        result = requests.get(
            url=url,
            headers=reqHeader
        )
        if not result.ok:
            return None
        return result.json()

    @staticmethod
    def start(vds_id):
        """
        Start VDS
        """
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
        """
        Stop VDS
        """
        uri = "https://public-api.timeweb.com/api/v1/vds/{id}/{action}"
        result = requests.post(
            uri.format(id=vds_id, action='shutdown'),
            headers=reqHeader
        )
        if not result.ok:
            return None
        else:
            return result.json()

    @staticmethod
    def clone(vds_id):
        """
        Clone VDS
        """
        uri = "https://public-api.timeweb.com/api/v1/vds/{id}/{action}"
        result = requests.post(
            uri.format(id=vds_id, action='clone'),
            headers=reqHeader
        )
        if not result.ok:
            return None
        else:
            return result.json()


@app.command("balance")
def get_balance():
    """
    Show balance and Monthly costs
    """
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
def vds_start(vds_id: Optional[int] = typer.Argument(None)):
    """
    Start VDS, show cute spinner until VDS starts
    """
    if vds_id is None:
        vds_list()
        vds_id = input("Enter VDS ID: ")
    result = Server.start(vds_id)
    if result is None:
        print(typer.style("Error", fg=typer.colors.RED))
        sys.exit(1)

    for frame in cycle(r'-\|/'):
        state = Server.get_vds(vds_id)
        if state:
            if state['server']['status'] == 'on':
                print(typer.style("\nRunning", fg=typer.colors.GREEN))
                break
        print('\r', frame, sep='', end='', flush=True)
        sleep(0.1)


@servers_app.command("stop")
def vds_stop(vds_id: Optional[int] = typer.Argument(None)):
    """
    Stop VDS, show cute spinner until VDS stops
    """
    if vds_id is None:
        vds_list()
        vds_id = input("Enter VDS ID: ")
    result = Server.stop(vds_id)
    if result is None:
        print(typer.style("Error", fg=typer.colors.RED))
        sys.exit(1)

    for frame in cycle(r'-\|/'):
        state = Server.get_vds(vds_id)
        if state:
            if state['server']['status'] == 'off':
                print(typer.style("\nStopped", fg=typer.colors.RED))
                break
        print('\r', frame, sep='', end='', flush=True)
        sleep(0.1)


@servers_app.command("clone")
def vds_clone(vds_id: Optional[int] = typer.Argument(None)):
    """
    Clone VDS, show cute spinner until VDS stops
    """
    if vds_id is None:
        vds_list()
        vds_id = input("Enter VDS ID: ")
    new_vds = Server.clone(vds_id)
    if new_vds is None:
        print(typer.style("Error", fg=typer.colors.RED))
        sys.exit(1)
    else:
        new_vds = new_vds['server']

    for frame in cycle(r'-\|/'):
        state = Server.get_vds(new_vds['id'])
        if state:
            if state['server']['status'] == 'on':
                print(typer.style("\nCloned: " + new_vds['configuration']['caption'], fg=typer.colors.GREEN))
                break
        print('\r', frame, sep='', end='', flush=True)
        sleep(0.1)


@servers_app.command("list")
def vds_list():
    """
    Show list of VDSes
    ID, State, Name, IP, CPUs, Ram, Disk
    """
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
    Get access token based on base64'ed login:password
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
    """
    Load base64'ed login:pass and get access token
    """
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
