try:
    import urequests as requests
except ImportError:
    import requests
from node_type import (
    NODE_TYPES,
    ENCLOSURE,
    COOLER,
    HEATER,
    HUMIDIFIER,
    SPRINKLER,
    WATER
)
from validate_dict import (
    ValidateEnclosurePOST,
    ValidatedCoolerPOST,
    ValidateHeaterPOST,
    ValidateHumidifierPOST,
    ValidateSprinklerPOST,
    ValidateWaterPOST,
)


class PlantKeeper:

    def __init__(
            self,
            host='10.3.141.1',
            port=8001,
            user='',
            password=''
    ):

        assert isinstance(host, str)
        assert isinstance(port, int)
        assert isinstance(user, str)
        assert isinstance(password, str)

        self.node_type = False
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.header = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        self.power = False
        self.validator = False
        self.json = None

    @property
    def gateway(self):
        return (
                'http://'
                + self.host
                + ':'
                + str(self.port)
        )

    @property
    def api(self):
        return (
                'http://'
                + self.host
                + ':'
                + str(self.port)
                + '/api-v1/'
                + str(self.node_type)
                + '/'
        )

    def is_gateway_up(self):
        """
        Ensure gate way is up before starting main loop
        :return:
        """
        try:
            if requests.get(self.gateway).status_code == 200:
                return True
        except:
            return False

    def get_post_validator(self):
        if self.node_type == ENCLOSURE:
            self.validator = ValidateEnclosurePOST()
        elif self.node_type == COOLER:
            self.validator = ValidatedCoolerPOST()
        elif self.node_type == HEATER:
            self.validator = ValidateHeaterPOST()
        elif self.node_type == HUMIDIFIER:
            self.validator = ValidateHumidifierPOST()
        elif self.node_type == SPRINKLER:
            self.validator = ValidateSprinklerPOST()
        elif self.node_type == WATER:
            self.validator = ValidateWaterPOST()

    def set_node_type(self, node_type):
        assert isinstance(node_type, str)
        if node_type not in NODE_TYPES:
            raise ValueError(
                'Node type=' + node_type
                + ' not in ' + str(NODE_TYPES)
            )
        self.node_type = node_type
        self.get_post_validator()

    def post(self, _dict):
        assert isinstance(_dict, dict)

        if not self.node_type:
            raise ValueError('Node type not set')

        self.validator.validate(_dict)

        r = requests.post(
            self.api,
            json=_dict,
            headers=self.header
        )
        self.json = r.json()

        if r.status_code in [200, 201]:
            try:
                self.power = r.json()['power']
            except KeyError:
                self.power = 0
