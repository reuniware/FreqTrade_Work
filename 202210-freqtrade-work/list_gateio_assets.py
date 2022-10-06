#List all possible assets for trading in futures on gateio with freqtrade ;)
#pip install gate-api

from __future__ import print_function
import gate_api
from gate_api.exceptions import ApiException, GateApiException
# Defining the host is optional and defaults to https://api.gateio.ws/api/v4
# See configuration.py for a list of all supported configuration parameters.
configuration = gate_api.Configuration(
    host = "https://api.gateio.ws/api/v4"
)

api_client = gate_api.ApiClient(configuration)
# Create an instance of the API class
api_instance = gate_api.FuturesApi(api_client)
settle = 'usdt' # str | Settle currency

try:
    # List all futures contracts
    api_response = api_instance.list_futures_contracts(settle)
    #print(api_response)
    for line in api_response:
        print("\"" + line.name.replace("_", "/") + ":USDT\",")
except GateApiException as ex:
    print("Gate api exception, label: %s, message: %s\n" % (ex.label, ex.message))
except ApiException as e:
    print("Exception when calling FuturesApi->list_futures_contracts: %s\n" % e)
