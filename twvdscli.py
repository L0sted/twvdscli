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

dbs_app = typer.Typer()
app.add_typer(dbs_app, name='dbs', help='Control Managed databases')

servers_app = typer.Typer()
app.add_typer(servers_app, name='vds', help='Control VDS Servers, their snapshots and backups')

backups_app = typer.Typer()
servers_app.add_typer(backups_app, name='backup', help='Create/Delete backup')

snapshot_app = typer.Typer()
servers_app.add_typer(snapshot_app, name='snap', help='Create/Rollback/Delete snapshot')

class Dbaas:
    """
    DataBases As A Service
    """
    def list():
        url = 'https://public-api.timeweb.com/api/v1/dbs'
        result = requests.get(
            url=url,
            headers=reqHeader
        )
        if not result.ok:
            return None
        return result.json()
        
        

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

    @staticmethod
    def remove(vds_id):
        """
        Remove VDS
        """
        uri = "https://public-api.timeweb.com/api/v1/vds/{id}"
        result = requests.delete(
            uri.format(id=vds_id),
            headers=reqHeader
        )
        if not result.ok:
            return None
        else:
            return result.json()


class Backups:
    @staticmethod
    def create(vds_id):
        disk_id = Server.get_vds(vds_id)['server']['disk_stats']['disk_id']

        uri = "https://public-api.timeweb.com/api/v1/backups/vds/{id}/drive/{disk_id}"
        result = requests.post(
            uri.format(id=vds_id, disk_id=disk_id),
            headers=reqHeader
        )
        if result.ok:
            return result.json()
        else:
            return None

    @staticmethod
    def list(vds_id):
        disk_id = Server.get_vds(vds_id)['server']['disk_stats']['disk_id']
        uri = "https://public-api.timeweb.com/api/v1/backups/vds/{id}/drive/{disk_id}"
        result = requests.get(
            uri.format(id=vds_id, disk_id=disk_id),
            headers=reqHeader
        )
        if result.ok:
            return result.json()
        else:
            return None

    @staticmethod
    def remove(vds_id, backup_id):
        disk_id = Server.get_vds(vds_id)['server']['disk_stats']['disk_id']

        uri = "https://public-api.timeweb.com/api/v1/backups/{backup_id}/vds/{id}/drive/{disk_id}"
        result = requests.delete(
            uri.format(id=vds_id, disk_id=disk_id, backup_id=backup_id),
            headers=reqHeader
        )
        if result.ok:
            return result.json()
        else:
            return None


class Snapshots:
    @staticmethod
    def get(vds_id):
        uri = "https://public-api.timeweb.com/api/v1/restore-points/{vds_id}"
        result = requests.get(
            uri.format(vds_id=vds_id),
            headers=reqHeader
        )
        if result.ok:
            return result.json()
        else:
            return None

    @staticmethod
    def create(vds_id):
        uri = "https://public-api.timeweb.com/api/v1/restore-points/{vds_id}/create"
        result = requests.post(
            uri.format(vds_id=vds_id),
            headers=reqHeader
        )
        if result.ok:
            return result.json()
        else:
            return None

    @staticmethod
    def remove(vds_id):
        uri = "https://public-api.timeweb.com/api/v1/restore-points/{vds_id}/commit"
        result = requests.post(
            uri.format(vds_id=vds_id),
            headers=reqHeader
        )
        if result.ok:
            return result.json()
        else:
            return None

    @staticmethod
    def restore(vds_id):
        uri = "https://public-api.timeweb.com/api/v1/restore-points/{vds_id}/rollback"
        result = requests.post(
            uri.format(vds_id=vds_id),
            headers=reqHeader
        )
        if result.ok:
            return result.json()
        else:
            return None


@snapshot_app.command("get")
def get_snap(vds_id: Optional[int] = typer.Argument(None)):
    """
    Get snapshot
    """
    if vds_id is None:
        vds_list()
        vds_id = input("Enter VDS ID: ")
    result = Snapshots.get(vds_id)
    if result is None:
        print(typer.style("Error", fg=typer.colors.RED))
        sys.exit(1)
    else:
        x = PrettyTable()
        x.field_names = ["VDS ID", "ID", "Created" , "Expire"]
        x.add_row([vds_id, result['restore_point']['id'], result['restore_point']['created_at'], result['restore_point']['expired_at']])
        print(x)


@snapshot_app.command("create")
def create_snap(vds_id: Optional[int] = typer.Argument(None)):
    """
    Create snapshot
    """
    if vds_id is None:
        vds_list()
        vds_id = input("Enter VDS ID: ")

    result = Snapshots.create(vds_id)
    if result is None:
        print(typer.style("Error", fg=typer.colors.RED))
        sys.exit(1)
    else:
        print(typer.style("Success", fg=typer.colors.GREEN))


@snapshot_app.command("restore")
def rollback_snap(vds_id: Optional[int] = typer.Argument(None)):
    """
    Restore VDS from snapshot
    """
    if vds_id is None:
        vds_list()
        vds_id = input("Enter VDS ID: ")

    result = Snapshots.restore(vds_id)
    if result is None:
        print(typer.style("Error", fg=typer.colors.RED))
        sys.exit(1)
    else:
        print(typer.style("Success", fg=typer.colors.GREEN))


@snapshot_app.command("remove")
def remove_snap(vds_id: Optional[int] = typer.Argument(None)):
    """
    Remove snapshot
    """
    if vds_id is None:
        vds_list()
        vds_id = input("Enter VDS ID: ")

    result = Snapshots.remove(vds_id)
    if result is None:
        print(typer.style("Error", fg=typer.colors.RED))
        sys.exit(1)
    else:
        print(typer.style("Success", fg=typer.colors.GREEN))


@backups_app.command("create")
def create_backup(vds_id: Optional[int] = typer.Argument(None)):
    """
    Create backup of main disk
    """
    if vds_id is None:
        vds_list()
        vds_id = input("Enter VDS ID: ")
    result = Backups.create(vds_id)
    if result is None:
        print(typer.style("Error", fg=typer.colors.RED))
        sys.exit(1)
    else:
        print(typer.style("Success", fg=typer.colors.GREEN))


@backups_app.command("list")
def list_backup(vds_id: Optional[int] = typer.Argument(None)):
    """
    List backups
    """
    if vds_id is None:
        vds_list()
        vds_id = input("Enter VDS ID: ")
    result = Backups.list(vds_id)
    if result is None:
        print(typer.style("Error", fg=typer.colors.RED))
        sys.exit(1)
    else:
        x = PrettyTable()
        x.field_names = ["id", "Date", "Size", "Cost", "Mounted", "status"]
        for i in result['backups']:
            x.add_row([i['id'], i['c_date'], i['drive_size'], i['cost_backup'], i['mounted'], i['status']])
        print(x)


@backups_app.command("remove")
def remove_backup(vds_id: Optional[int] = typer.Argument(None), backup_id: int = typer.Option(...)):
    """
    Remove backup of main disk
    """
    if vds_id is None:
        vds_list()
        vds_id = input("Enter VDS ID: ")
    result = Backups.remove(vds_id, backup_id)
    if result is None:
        print(typer.style("Error", fg=typer.colors.RED))
        sys.exit(1)
    else:
        print(typer.style("Success", fg=typer.colors.GREEN))


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


@dbs_app.command("list")
def list_dbs():
    """
    Show list of VDSes
    ID, State, Name, IP, CPUs, Ram, Disk
    """
    list_of_dbaas = Dbaas.list()
    x = PrettyTable()
    x.field_names = ['id', 'state', 'name', 'ip', 'local_ip', 'password', 'type']
    if list_of_dbaas is None:
        print(typer.style("Error", fg=typer.colors.RED))
        sys.exit(1)
    for i in list_of_dbaas['dbs']:
        if i['status'] == 'started':
            state = typer.style("Running", fg=typer.colors.GREEN)
        #elif i['status'] == 'off':
        #    state = typer.style('Stopped', fg=typer.colors.RED)
        else:
            state = i['status']
        x.add_row([
            i['id'],
            state,
            i['name'],
            i['ip'],
            i['local_ip'],
            i['password'],
            i['type']
        ])
    print(x)

    

@servers_app.command("start")
def vds_start(vds_id: Optional[int] = typer.Argument(None)):
    """
    Start VDS
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
    Stop VDS
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
    Clone VDS
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


@servers_app.command("remove")
def vds_remove(vds_id: Optional[int] = typer.Argument(None)):
    """
    Remove VDS
    """
    if vds_id is None:
        vds_list()
        vds_id = input("Enter VDS ID: ")
    result = Server.remove(vds_id)
    if result is None:
        print(typer.style("Error", fg=typer.colors.RED))
        sys.exit(1)
    for frame in cycle(r'-\|/'):
        state = Server.get_vds(vds_id)
        if not state.get('server'):
            print(typer.style("\nDeleted", fg=typer.colors.RED))
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
        x.add_row([
            i['id'],
            state,
            i['name'],
            i['ip'],
            i['configuration']['cpu'],
            i['configuration']['ram'],
            i['configuration']['disk_size']
        ])
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


def main():
    apikey = get_api_key()
    if apikey is None:
        print(typer.style("Auth Error", fg=typer.colors.RED))
        sys.exit(1)
    reqHeader['Authorization'] += apikey
    app()


if __name__ == '__main__':
    reqHeader = {"Authorization": "Bearer "}
    main()
