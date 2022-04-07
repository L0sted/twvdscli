#!/usr/bin/python3

import json
import sys

import requests
import typer
import os
import configparser
import base64

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


def get_balance():
    response = requests.get("https://public-api.timeweb.com/api/v1/accounts/finances", headers=reqHeader)
    if not response.ok:
        print(typer.style("Error", fg=typer.colors.RED))
        sys.exit(1)

    return response.json()


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
    # print('{0:7} {1:17} {5:16} {2:2} {3:5} {4:4}'.format('state', 'name', 'vcpus', 'memory', 'disk', 'ip'))
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
        print('{0:6} {1:15} {2:20} {3:16} {4:2} {5:5} {6:4} '.format(i['id'], state, i['name'], i['ip'], i['configuration']['cpu'], i['configuration']['ram'], i['configuration']['disk_size']))


def auth(login, passwd):
    """
    Convert login:pass into base64 and make a request

    :param login:
    :param passwd:
    :return:
    """
    based = base64.b64encode(str(login+":"+passwd).encode('utf-8'))
    headers = {"Authorization": "Basic " + based.decode('utf-8')}

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
        print(result)
        return result


def get_api_key():
    config = configparser.ConfigParser()
    config.read(os.path.join(os.getenv('HOME'), '.config', 'twvdscli.ini'))
    result = config.get('api', 'key', fallback=None)
    if result is None:
        login = input("Enter login ")
        passwd = input("Enter passwd ")
        result = auth(login, passwd)
        config.add_section('api')
        config.set('api', 'key', result)

        with open(os.path.join(os.getenv('HOME'), '.config', 'twvdscli.ini'), 'w') as configfile:
            config.write(configfile)

    return result


if __name__ == '__main__':
    apikey = get_api_key()
    reqHeader = {"Authorization": "Bearer " + apikey}

    app()
