import shutil

def zip_folder(folder_path, output_filename):
    shutil.make_archive(output_filename, 'zip', folder_path)

import socket

def list_ips():
    # Get the local host name
    hostname = socket.gethostname()

    # Get the IP addresses associated with the host
    ips = socket.getaddrinfo(hostname, None, socket.AF_INET)

    # Extract and return the IP addresses in a list
    return [ip[4][0] for ip in ips]

def display_menu(options):
    print("Selection Menu:")
    for i, option in enumerate(options, start=1):
        print(f"{i}. {option}")
    print(f"{len(options) + 1}. Exit")

def select_option():
    option = input("Enter the number of the desired option: ")
    return option

def write_ip_to_file(option):
    with open("../agent/server_ip.txt", "w") as file:
        file.write(option)

def select_host_ip():
    available_ips = list_ips()

    while True:
        display_menu(available_ips)
        chosen_option = select_option()

        if chosen_option.isdigit():
            chosen_option = int(chosen_option)
            if 1 <= chosen_option <= len(available_ips):
                selected_ip = available_ips[chosen_option - 1]
                print(f"IP para configurar no agente: {selected_ip}")
                write_ip_to_file(str(selected_ip))
                return selected_ip
            elif chosen_option == len(available_ips) + 1:
                print("Executando servidor sem configurar IP do servico no agente.")
                break
            else:
                print("Opcao invalida.")
        else:
            print("Opcao invalida.")
