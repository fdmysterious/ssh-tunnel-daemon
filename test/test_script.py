import logging
import traceback
import subprocess

TEST_USER_NAME="tunnelist"

log                 = None

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

        finally:
            pass
            #stop_container(source_container_id)
            #stop_container(target_container_id)

    except Exception as exc:
        log.error("Error in test:")
        log.error(traceback.format_exc())
