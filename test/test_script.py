import logging
import traceback
import subprocess
import time
import signal

TEST_USER_NAME = "tunnelist"
REMOTE_PORT    = 2503

log            = None

def init_log():
    global log

    log_format  = "%(asctime)s - [%(levelname)10s] %(message)s"
    date_format = "%Y-%m-%d %H:%S:%S"
    logging.basicConfig(level=logging.DEBUG, format=log_format, datefmt=date_format)

    log = logging.getLogger(__name__)


def start_test_container():
    result = subprocess.run(["just", "start_test_container"], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Could not start test container:\n{result.stderr}")
    return result.stdout.strip()


def stop_container(id):
    log.info(f"Stopping container with ID {id}")
    result = subprocess.run(["just", "stop", id], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Could not stop container:\n{result.stderr}")
    return result.stdout.strip()


def start_containers():
    log.info("Start test source container")
    source_container_id = start_test_container()

    log.info("Start test target container")
    target_container_id = start_test_container()

    return source_container_id, target_container_id


def get_container_ip(cid):
    # https://stackoverflow.com/questions/17157721/how-to-get-a-docker-containers-ip-address-from-the-host
    result = subprocess.run(["just", "get_ip", cid], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Could not get container's IP address:\n{result.stderr}")

    return result.stdout.strip()


def create_test_user(cid):
    log.info(f"Create test user {TEST_USER_NAME} on container {cid}")
    result = subprocess.run(["just", "create_user", cid, TEST_USER_NAME], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Could not create test user:\n{result.stderr}{result.stdout}")
    log.debug(result.stdout.strip())


def create_ssh_key(cid):
    log.info(f"Create ssh key on user {TEST_USER_NAME} on container {cid}")
    result = subprocess.run(["just", "create_ssh_key", cid, TEST_USER_NAME], capture_output=True, text=True)
    log.info(f"Result stdout:\n{result.stdout}")
    
    if result.returncode != 0:
        raise RuntimeError(f"Failed to create ssh key:\n{result.stderr}")


def retrieve_ssh_key(cid):
    log.info(f"Retrieve SSH key for user {TEST_USER_NAME} on container {cid}")
    result = subprocess.run(["just", "retrieve_ssh_key", cid, TEST_USER_NAME], capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(f"Failed to retrieve ssh key:\n{result.stderr}{result.stdout}")
    return result.stdout.strip()


def add_key_to_container(cid, key):
    log.info(f"Register key {key} to container {cid}")
    result = subprocess.run(["just", "add_key_to_container", cid, TEST_USER_NAME, key], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Could not add key to container:\n{result.stderr}")


def copy_script(cid):
    log.info(f"Copy script to container {cid}")
    result = subprocess.run(["just", "copy_script", cid, TEST_USER_NAME], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Could not copy script:\n{result.stderr}")


def start_tunnel(cid, remote_port, remote_user, remote_host):
    log.info(f"Start tunnel on {cid} with:")
    log.info(f"- remote_port = {remote_port}")
    log.info(f"- remote_user = {remote_user}")
    log.info(f"- remote_host = {remote_host}")

    result = subprocess.run(["just", "start_tunnel", cid, TEST_USER_NAME, str(remote_port), remote_user, remote_host], capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(f"Failed to start ssh tunnel:\n{result.stderr}\n{result.stdout}")


def stop_tunnel(cid):
    log.info(f"Stopping tunnel on {cid}")

    result = subprocess.run(["just", "stop_tunnel", cid], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Failed to stop tunnel:\n{result.stderr}\n{result.stdout}")


def try_connection(cid, remote_port, remote_user, host):
    log.info("Try connection with:")
    log.info(f"- remote_port = {remote_port}")
    log.info(f"- remote_user = {remote_user}")
    log.info(f"- host        = {host}"       )

    result = subprocess.run(["just", "try_connection", cid, TEST_USER_NAME, str(remote_port), remote_user, host], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Failed connection check with return code {result.returncode}\n{result.stdout}\n{result.stderr}")

    log.info("Connection successful!")


def get_tunnel_logs(cid):
    log.info(f"Getting tunnel logs on {cid}")
    result = subprocess.run(["just", "get_tunnel_logs", cid, TEST_USER_NAME], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError("Failed to retrieve logs:\n{result.stderr}\n{result.stdout}")
    return result.stdout


if __name__ == "__main__":
    init_log()
    log.info("Hello world!")


    ## Start containers
    try:
        source_container_id, target_container_id = start_containers()

        log.info(f" - source_container_id = {source_container_id}")
        log.info(f" - target_container_id = {target_container_id}")

        try:
            source_ip = get_container_ip(source_container_id)
            target_ip = get_container_ip(target_container_id)

            log.info(f" - source_ip = {source_ip}")
            log.info(f" - target_ip = {target_ip}")

            create_test_user(source_container_id)
            create_test_user(target_container_id)

            create_ssh_key(source_container_id)
            create_ssh_key(target_container_id)

            pub_key_source = retrieve_ssh_key(source_container_id)
            pub_key_target = retrieve_ssh_key(target_container_id)

            log.info(f" - pub_key_source = {pub_key_source}")
            log.info(f" - pub_key_target = {pub_key_target}")

            add_key_to_container(source_container_id, pub_key_target)
            add_key_to_container(target_container_id, pub_key_source)

            copy_script(source_container_id)

            # Connect first time to target to register known_hosts key
            try_connection(source_container_id, 22, TEST_USER_NAME, target_ip)

            # Standard connection test
            start_tunnel(source_container_id, REMOTE_PORT, TEST_USER_NAME, target_ip)
            log.info("Waiting 5s")
            time.sleep(5)
            try_connection(target_container_id, REMOTE_PORT, TEST_USER_NAME, "localhost")
            stop_tunnel(source_container_id)
            

            # Altering target host identification, and ensuring that the tunnel script
            # detects it properly.


        finally:
            pass
            #stop_container(source_container_id)
            #stop_container(target_container_id)

    except Exception as exc:
        log.error("Error in test:")
        log.error(traceback.format_exc())
