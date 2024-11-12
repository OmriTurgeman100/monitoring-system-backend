import json

addresses = [
    "alphacorp 8.8.4.4", "securecloud 1.0.0.1", "fastdns 208.67.220.220", "nextgen 9.9.9.10",
    "loopback 127.0.0.2", "linuxhub 127.0.8.1", "techsoft 13.107.43.16", "cloudgiant 13.248.119.2",
    "skynet 20.45.17.4", "fruittech 17.253.145.11",
    "alphacorp2 8.8.8.8", "securecloud2 1.1.1.1", "fastdns2 208.67.222.222", "nextgen2 9.9.9.9",
    "loopback2 127.0.0.3", "linuxhub2 127.0.8.2", "techsoft2 13.107.44.16", "cloudgiant2 13.248.120.2",
    "skynet2 20.45.18.4", "fruittech2 17.253.145.12",
    "alphacorp3 8.8.3.3", "securecloud3 1.0.1.0", "fastdns3 208.67.219.219", "nextgen3 9.9.8.10",
    "loopback3 127.0.0.4", "linuxhub3 127.0.8.3", "techsoft3 13.107.45.16", "cloudgiant3 13.248.121.2",
    "skynet3 20.45.19.4", "fruittech3 17.253.145.13",
    "alphacorp4 8.8.2.2", "securecloud4 1.0.2.0", "fastdns4 208.67.218.218", "nextgen4 9.9.7.10",
    "loopback4 127.0.0.5", "linuxhub4 127.0.8.4", "techsoft4 13.107.46.16", "cloudgiant4 13.248.122.2",
    "skynet4 20.45.20.4", "fruittech4 17.253.145.14",
    "alphacorp5 8.8.1.1", "securecloud5 1.0.3.0", "fastdns5 208.67.217.217", "nextgen5 9.9.6.10",
    "loopback5 127.0.0.6", "linuxhub5 127.0.8.5", "techsoft5 13.107.47.16", "cloudgiant5 13.248.123.2",
    "skynet5 20.45.21.4", "fruittech5 17.253.145.15",
    "alphacorp6 8.8.6.6", "securecloud6 1.0.4.0", "fastdns6 208.67.216.216", "nextgen6 9.9.5.10",
    "loopback6 127.0.0.7", "linuxhub6 127.0.8.6", "techsoft6 13.107.48.16", "cloudgiant6 13.248.124.2",
    "skynet6 20.45.22.4", "fruittech6 17.253.145.16",
    "alphacorp7 8.8.7.7", "securecloud7 1.0.5.0", "fastdns7 208.67.215.215", "nextgen7 9.9.4.10",
    "loopback7 127.0.0.8", "linuxhub7 127.0.8.7", "techsoft7 13.107.49.16", "cloudgiant7 13.248.125.2",
    "skynet7 20.45.23.4", "fruittech7 17.253.145.17",
    "alphacorp8 8.8.9.9", "securecloud8 1.0.6.0", "fastdns8 208.67.214.214", "nextgen8 9.9.3.10",
    "loopback8 127.0.0.9", "linuxhub8 127.0.8.8", "techsoft8 13.107.50.16", "cloudgiant8 13.248.126.2",
    "skynet8 20.45.24.4", "fruittech8 17.253.145.18",
    "alphacorp9 8.8.5.5", "securecloud9 1.0.7.0", "fastdns9 208.67.213.213", "nextgen9 9.9.2.10",
    "loopback9 127.0.0.10", "linuxhub9 127.0.8.9", "techsoft9 13.107.51.16", "cloudgiant9 13.248.127.2",
    "skynet9 20.45.25.4", "fruittech9 17.253.145.19",
    "alphacorp10 8.8.10.10", "securecloud10 1.0.8.0", "fastdns10 208.67.212.212", "nextgen10 9.9.1.10",
    "loopback10 127.0.0.11", "linuxhub10 127.0.8.10", "techsoft10 13.107.52.16", "cloudgiant10 13.248.128.2",
    "skynet10 20.45.26.4", "fruittech10 17.253.145.20",
    "alphacorp11 8.8.11.11", "securecloud11 1.0.9.0", "fastdns11 208.67.211.211", "nextgen11 9.9.0.10",
    "loopback11 127.0.0.12", "linuxhub11 127.0.8.11", "techsoft11 13.107.53.16", "cloudgiant11 13.248.129.2",
    "skynet11 20.45.27.4", "fruittech11 17.253.145.21",
    "alphacorp12 8.8.12.12", "securecloud12 1.0.10.0", "fastdns12 208.67.210.210", "nextgen12 9.9.12.10",
    "loopback12 127.0.0.13", "linuxhub12 127.0.8.12", "techsoft12 13.107.54.16", "cloudgiant12 13.248.130.2",
    "skynet12 20.45.28.4", "fruittech12 17.253.145.22",
    "alphacorp13 8.8.13.13", "securecloud13 1.0.11.0", "fastdns13 208.67.209.209", "nextgen13 9.9.11.10",
    "loopback13 127.0.0.14", "linuxhub13 127.0.8.13", "techsoft13 13.107.55.16", "cloudgiant13 13.248.131.2",
    "skynet13 20.45.29.4", "fruittech13 17.253.145.23",
    "alphacorp14 8.8.14.14", "securecloud14 1.0.12.0", "fastdns14 208.67.208.208", "nextgen14 9.9.10.10",
    "loopback14 127.0.0.15", "linuxhub14 127.0.8.14", "techsoft14 13.107.56.16", "cloudgiant14 13.248.132.2",
    "skynet14 20.45.30.4", "fruittech14 17.253.145.24",
    "alphacorp15 8.8.15.15", "securecloud15 1.0.13.0", "fastdns15 208.67.207.207", "nextgen15 9.9.9.99",
    "loopback15 127.0.0.16", "linuxhub15 127.0.8.15", "techsoft15 13.107.57.16", "cloudgiant15 13.248.133.2",
    "skynet15 20.45.31.4", "fruittech15 17.253.145.25"
]

data = []

for item in addresses:
    title, ip = item.split(" ")

    body = {
        "title": title,
        "ip": ip
    }

    data.append(body)


# with open("data.json", "w") as file:
#     json.dump(data, file, indent=2)

    

with open("data.json", "r") as file:
    data = json.load(file)

    body = {
        "title": "1"
    }


