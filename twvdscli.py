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
# twvdscli dbs
dbs_app = typer.Typer()
app.add_typer(dbs_app, name='dbs', help='Control Managed databases')

# twvdscli vds
servers_app = typer.Typer()
app.add_typer(servers_app, name='vds', help='Control VDS Servers, their snapshots and backups')

# twvdscli vds backups
backups_app = typer.Typer()
servers_app.add_typer(backups_app, name='backup', help='Create/Delete backup')

# twvdscli vds snap
snapshot_app = typer.Typer()
servers_app.add_typer(snapshot_app, name='snap', help='Create/Rollback/Delete snapshot')

# twvdscli vds info
vds_info_app = typer.Typer()
servers_app.add_typer(vds_info_app, name='info', help='Get info about plans and os\'es')


class Dbaas:
    """
    DataBases As A Service
    """
    @staticmethod
    def list():
        url = 'https://public-api.timeweb.com/api/v1/dbs'
        result = requests.get(
            url=url,
            headers=reqHeader
        )
        if not result.ok:
            return None
        return result.json()

    @staticmethod
    def get(db_id):
        url = 'https://public-api.timeweb.com/api/v1/dbs/{db_id}'
        result = requests.get(
            url=url.format(db_id=db_id),
            headers=reqHeader
        )
        if not result.ok:
            return None
        return result.json()

    @staticmethod
    def create(passwd, name, db_type):
        url = 'https://public-api.timeweb.com/api/v1/dbs'
        if db_type == 'postgres':
            service_type = 357
        else:
            service_type = 341
        data = dict(host="%", login="user", password=passwd, name=name, type=db_type,
                    hash_type="caching_sha2", service_type=service_type)
        result = requests.post(
            url=url,
            json=data,
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
        x.field_names = ["VDS ID", "ID", "Created", "Expire"]
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


@dbs_app.command("create")
def dbs_create(passwd: str = typer.Option(..., help="DB password"),
               name: str = typer.Option(..., help="DB Name"),
               db_type: str = typer.Option(..., help="mysql5/mysql/postgres"),
               raw: bool = typer.Option(False, help="Get result as raw json")):
    """
    Create database
    """
    # service_type == 341 - mysql
    # service_type == 357 - pgsql
    result = Dbaas.create(passwd=passwd, name=name, db_type=db_type)
    if raw:
        print(result)
        return
    # We need to get id from result['db']['id']
    db_id = result['db']['id']
    for frame in cycle(r'-\|/'):
        state = Dbaas.get(db_id)
        if state:
            if state['db']['status'] == 'started':
                print(typer.style("\nCreated DB: " + name, fg=typer.colors.GREEN))
                break
        print('\r', frame, sep='', end='', flush=True)
        sleep(0.1)


@dbs_app.command("list")
def dbs_list(raw: bool = typer.Option(False, help="Get result as raw json")):
    """
    Show list of DBs:
    ID, State, Name, IP, local IP, Password, Type
    """
    list_of_dbaas = Dbaas.list()
    if raw:
        print(list_of_dbaas)
        return
    x = PrettyTable()
    x.field_names = ['id', 'state', 'name', 'ip', 'local_ip', 'password', 'type']
    if list_of_dbaas is None:
        print(typer.style("Error", fg=typer.colors.RED))
        sys.exit(1)
    for i in list_of_dbaas['dbs']:
        if i['status'] == 'started':
            state = typer.style("Running", fg=typer.colors.GREEN)
#        elif i['status'] == 'off':
        #    state = typer.style('Stopped', fg=typer.colors.RED)
        else:
            state = i['status']
        if i['type'] == 'mysql':
            type_of_db = 'MySQL 8'
        elif i['type'] == 'mysql5':
            type_of_db = 'MySQL 5.7'
        elif i['type'] == 'postgres':
            type_of_db = 'PostgreSQL 13'
        else:
            type_of_db = i['type']
        x.add_row([
            i['id'],
            state,
            i['name'],
            i['ip'],
            i['local_ip'],
            i['password'],
            type_of_db
        ])
    print(x)


@dbs_app.command("goto")
def dbs_connect(db_id: Optional[int] = typer.Argument(None)):
    """
    Connect to DB CLI
    """
    cmd_mysql = "mysql -u {login} -p{password} -h {ip} -P 3306 -D default_db"
    cmd_psql = "psql -d default_db -U  {login} -W -p 5432 -h {ip}"
    # Get DB ID if not specified
    if db_id is None:
        dbs_list()
        db_id = input("Enter DB ID: ")
    # Get type of DB, password, IP
    db_data = Dbaas.get(db_id)

    db_type = db_data['db']['type']
    db_pass = db_data['db']['password']
    db_ip = db_data['db']['ip']
    db_user = db_data['db']['login']
    if db_type == 'mysql' or db_type == 'mysql5':
        os.system(cmd_mysql.format(ip=db_ip, password=db_pass, login=db_user))
    elif db_type == 'postgres':
        print("Password: ", db_pass)
        os.system(cmd_psql.format(ip=db_ip, login=db_user))


@vds_info_app.command("plans")
def vds_plans(raw: bool = typer.Option(False, help="Get result as raw json"),
              sort_by: str = typer.Option(None, help="sort results by value/cpu/ram/disk")):
    uri = "https://public-api.timeweb.com/api/v1/presets"
    result = requests.get(uri, headers=reqHeader)

    if not result.ok:
        print('Error')
        sys.exit(1)
    # If raw - print raw result and exit
    if raw:
        print(result.text)
        sys.exit(0)

    # else print pretty
    x = PrettyTable()
    x.field_names = ['id', 'cpus', 'ram', 'disk', 'value', 'name', 'description']
    result = result.json()
    print("Total: "+ str(result['meta']['total']))
    # result = result
    for i in result['presets']:
        x.add_row([
            i['id'],
            i['cpu'],
            i['ram'],
            i['drive'],
            i['discount_value'],
            i['name'],
            i['description']
        ])
        if sort_by in ('cpus', 'ram', 'disk', 'value'):
            x.sortby = sort_by
        elif not sort_by is None:
            print("No such sort")
    print(x)


@vds_info_app.command("os")
def vds_oses(raw: bool = typer.Option(False, help="Get result as raw json")):
    uri = "https://public-api.timeweb.com/api/v1/os"
    result = requests.get(uri, headers=reqHeader)

    if not result.ok:
        print('Error')
        sys.exit(1)
    # If raw - print raw result and exit
    if raw:
        print(result.text)
        sys.exit(0)

    # else print pretty
    x = PrettyTable()
    x.field_names = ['id', 'fullname', 'family', 'name', 'latin', 'available']
    result = result.json()
    print("Total: "+ str(result['meta']['total']))
    # result = result
    for i in result['os']:
        x.add_row([
            i['id'],
            i['os_caption'],
            i['os_type'],
            i['os_name'],
            i['os_latin'],
            i['is_public']
        ])
    print(x)


@servers_app.command("create")
def vds_create(
        name: str = typer.Option(..., help="VDS Name"),
        os_id: int = typer.Option(..., help="OS ID"),
        preset: int = typer.Option(17, help="Preset ID"),
        comment: str = typer.Option("", help="Comment")
):
    # get user group
    group_uri = "https://public-api.timeweb.com/api/v1/accounts/{user}/group"
    # get username from saved base64
    config = configparser.ConfigParser()
    config.read(os.path.join(os.getenv('HOME'), '.config', 'twvdscli.ini'))
    based = config.get('api', 'key', fallback=None)
    based = base64.b64decode(based)
    based = str(based, 'utf-8')
    user = based.split(':')[0]

    group_id = requests.get(
        group_uri.format(user=user), headers=reqHeader
    )
    # finally get group id
    if group_id.ok:
        group_id = group_id.json()['groups'][0]['id']

    data = {
      "server": {
        "configuration": {
          "caption": name,
          # "disk_size": 5, # dont give a fuck
          # "network_bandwidth": 100, # dont give a fuck
          "os": os_id, # 47 - ubuntu 18.04
          # "xen_cpu": 2, # dont give a fuck
          # "xen_ram": 4096, # dont give a fuck
          "ddos_guard": False
        },
        "comment": comment,
        "group_id": group_id, # https://public-api.timeweb.com/api/v1/accounts/{user}/group
        "name": "string", # what is this for?
        "preset_id": preset, # you can not create vds without this, but how to create flexible vds? (preset example: 20)
        "install_ssh_key": "",
        "server_id": None,
        "local_networks": []
        }
    }

    response = requests.post(
        "https://public-api.timeweb.com/api/v1/vds",
        headers=reqHeader,
        json=data
    )

    if not response.ok:
        print(typer.style("Error", fg=typer.colors.RED))
        sys.exit(1)
    else:
        response = response.json()
    for frame in cycle(r'-\|/'):
        state = Server.get_vds(response['server']['id'])
        if state:
            if state['server']['status'] == 'on':
                print(typer.style("\nCreated: " + response['server']['configuration']['caption'], fg=typer.colors.GREEN))
                break
        print('\r', frame, sep='', end='', flush=True)
        sleep(0.1)


@servers_app.command("goto")
def vds_goto(vds_id: Optional[int] = typer.Argument(None),
             port: int = typer.Option(22, help="Specify non standart SSH port.")):
    """
    Connect via SSH to VDS
    """
    if vds_id is None:
        vds_list()
        vds_id = input("Enter VDS ID: ")

    vds = Server.get_vds(vds_id)
    ip = vds['server']['ip']

    os.system('ssh -p {port} root@{ip}'.format(port=port, ip=ip))


@servers_app.command("start")
def vds_start(vds_id: Optional[int] = typer.Argument(None), raw: bool = typer.Option(False, help="Get result as raw json")):
    """
    Start VDS
    """
    if vds_id is None:
        if raw:
            print(
                dict(
                    error="No VDS ID provided"
                )
            )
            return 1
        vds_list()
        vds_id = input("Enter VDS ID: ")
    result = Server.start(vds_id)
    if result is None:
        print(typer.style("Error", fg=typer.colors.RED))
        sys.exit(1)
    if raw:
        print(result)
        return
    for frame in cycle(r'-\|/'):
        state = Server.get_vds(vds_id)
        if state:
            if state['server']['status'] == 'on':
                print(typer.style("\nRunning", fg=typer.colors.GREEN))
                break
        print('\r', frame, sep='', end='', flush=True)
        sleep(0.1)


@servers_app.command("stop")
def vds_stop(vds_id: Optional[int] = typer.Argument(None), raw: bool = typer.Option(False, help="Get result as raw json")):
    """
    Stop VDS
    """
    if vds_id is None:
        if raw:
            print(
                dict(
                    error="No VDS ID provided"
                )
            )
            return 1
        vds_list()
        vds_id = input("Enter VDS ID: ")
    result = Server.stop(vds_id)
    if result is None:
        print(typer.style("Error", fg=typer.colors.RED))
        sys.exit(1)
    if raw:
        print(result)
    for frame in cycle(r'-\|/'):
        state = Server.get_vds(vds_id)
        if state:
            if state['server']['status'] == 'off':
                print(typer.style("\nStopped", fg=typer.colors.RED))
                break
        print('\r', frame, sep='', end='', flush=True)
        sleep(0.1)


@servers_app.command("clone")
def vds_clone(vds_id: Optional[int] = typer.Argument(None),
              raw: bool = typer.Option(False, help="Get result as raw json")):
    """
    Clone VDS
    """
    if vds_id is None:
        if raw:
            print(
                dict(
                    error="No VDS ID provided"
                )
            )
            sys.exit(1)
        vds_list()
        vds_id = input("Enter VDS ID: ")
    new_vds = Server.clone(vds_id)
    if new_vds is None:
        print(typer.style("Error", fg=typer.colors.RED))
        sys.exit(1)
    else:
        if raw:
            print(new_vds)
            return
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
def vds_remove(vds_id: Optional[int] = typer.Argument(None),
               raw: bool = typer.Option(False, help="Get result as raw json")):
    """
    Remove VDS
    """
    if vds_id is None:
        if raw:
            print(
                dict(
                    error="No VDS ID provided"
                )
            )
            sys.exit(1)
        vds_list()
        vds_id = input("Enter VDS ID: ")
    result = Server.remove(vds_id)
    if result is None:
        print(typer.style("Error", fg=typer.colors.RED))
        sys.exit(1)
    else:
        if raw:
            print(result)
            sys.exit(0)
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
