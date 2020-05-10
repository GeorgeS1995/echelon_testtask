Echelon testtask

install requirements:
  - pip3 install -r ./requirements.txt

run:
  - cd ./api
  - flask run

Api example:

Get network interface information.
curl --location --request GET 'http://127.0.0.1:5000/api/v1/network'
Response:
200 OK
{
    "eth0": {
        "gateway": "192.168.0.1",
        "list_ipv4": [
            "192.168.0.10"
        ],
        "list_ipv6": [
            "fe80::145e:3590:55f6:83e3"
        ],
        "subnet_mask": "255.255.255.0"
    },
    "eth1": {
        "list_ipv4": [
            "169.254.130.104"
        ],
        "list_ipv6": [
            "fe80::4013:7a4f:862:8268"
        ],
        "subnet_mask": "255.255.0.0"
    },
    "lo": {
        "list_ipv4": [
            "127.0.0.1"
        ],
        "list_ipv6": [
            "::1"
        ],
        "subnet_mask": "255.0.0.0"
    }
}

Add ip to inner json file. IP will automatically be added to the interfaces with a suitable subnet.
curl --location --request POST 'http://127.0.0.1:5000/api/v1/network' \
--header 'Content-Type: application/json' \
--data-raw '{
	"ipv4": "192.168.0.19"
}'
Response:
201 CREATED

Delete ip from json file
curl --location --request DELETE 'http://127.0.0.1:5000/api/v1/network' \
--header 'Content-Type: application/json' \
--data-raw '{
	"ipv4": "192.168.0.19"
}'
Response:
204 NO CONTENT
