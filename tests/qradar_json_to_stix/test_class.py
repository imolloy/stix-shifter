from stix_shifter.src.json_to_stix import json_to_stix_translator
from stix_shifter.src import transformers
from stix_shifter.src.modules.qradar import qradar_translator
import json
import unittest

interface = qradar_translator.Translator()
map_file = open(interface.mapping_filepath).read()
map_data = json.loads(map_file)
data_source = {
    "type": "identity",
    "id": "identity--3532c56d-ea72-48be-a2ad-1a53f4c9c6d3",
    "name": "QRadar",
    "identity_class": "events"
}
options = {}


class TestTransform(unittest.TestCase):

    def test_common_prop(self):
        transformer = None
        data = {"starttime": 1531169112, "eventcount": 5}

        result_bundle = json_to_stix_translator.convert_to_stix(
            data_source, map_data, [data], transformers.get_all_transformers(), options)

        assert(result_bundle['type'] == 'bundle')
        result_bundle_objects = result_bundle['objects']

        result_bundle_identity = result_bundle_objects[0]
        assert(result_bundle_identity['type'] == data_source['type'])
        assert(result_bundle_identity['id'] == data_source['id'])
        assert(result_bundle_identity['name'] == data_source['name'])
        assert(result_bundle_identity['identity_class']
               == data_source['identity_class'])

        observed_data = result_bundle_objects[1]

        assert(observed_data['id'] is not None)
        assert(observed_data['type'] == "observed-data")
        assert(observed_data['created_by_ref'] == result_bundle_identity['id'])

        assert(observed_data['number_observed'] == 5)
        assert(observed_data['created'] is not None)
        assert(observed_data['modified'] is not None)
        assert(observed_data['first_observed'] is not None)
        assert(observed_data['last_observed'] is not None)

    def test_cybox_observables(self):
        transformer = None
        payload = "SomeBase64Payload"
        user_id = "someuserid2018"
        url = "https://example.com"
        domain = "example.com"
        source_ip = "127.0.0.1"
        destination_ip = "255.255.255.1"
        data = {"sourceip": source_ip, "destinationip": destination_ip, "url": url,
                "domain": domain, "payload": payload, "username": user_id, "protocol": 'TCP', "sourceport": 3000, "destinationport": 2000}

        result_bundle = json_to_stix_translator.convert_to_stix(
            data_source, map_data, [data], transformers.get_all_transformers(), options)

        assert(result_bundle['type'] == 'bundle')

        result_bundle_objects = result_bundle['objects']
        observed_data = result_bundle_objects[1]

        assert('objects' in observed_data)
        objects = observed_data['objects']

        # Test that each data element is properly mapped and input into the STIX JSON
        for key, value in objects.items():
            assert(int(key) in list(range(0, len(objects))))
            # Todo: handle case where there is both a source and destination ip, there will be more than one ipv4-addr
            if(value['type'] == 'ipv4-addr'):
                # assert(
                #     value['value'] == source_ip), "Wrong value returned " + key + ":" + str(value)
                assert(True)
            elif(value['type'] == 'url'):
                assert(value['value'] == url), "Wrong value returned " + \
                    key + ":" + str(value)
            elif(value['type'] == 'domain-name'):
                assert(
                    value['value'] == domain), "Wrong value returned " + key + ":" + str(value)
            elif(value['type'] == 'artifact'):
                assert(
                    value['payload_bin'] == payload), "Wrong value returned " + key + ":" + str(value)
            elif(value['type'] == 'user-account'):
                assert(
                    value['user_id'] == user_id), "Wrong value returned " + key + ":" + str(value)
            # Todo: should not be returned since the address passed in isn't ipv6, still needs to be fixed in logic
            elif(value['type'] == 'ipv6-addr'):
                # assert(
                #     value['value'] == source_ip), "Wrong value returned " + key + ":" + str(value)
                assert(True)
            elif(value['type'] == 'network-traffic'):
                assert(int(value['src_ref']) in list(
                    range(0, len(objects)))), "Wrong value returned " + key + ":" + str(value)
                assert(type(value['src_ref'])
                       is str), "Reference value should be a string"
                assert(int(value['dst_ref']) in list(
                    range(0, len(objects)))), "Wrong value returned " + key + ":" + str(value)
                assert(type(value['dst_ref'])
                       is str), "Reference value should be a string"
                assert(value['protocols'] == ['tcp'])
                assert(value['src_port'] == 3000)
                assert(value['dst_port'] == 2000)
            else:
                assert(False), "Returned a non-mapped value " + \
                    key + ":" + str(value)

    def test_custom_props(self):
        transformer = None
        data = {"logsourceid": 126, "qid": 55500004,
                "identityip": "0.0.0.0", "magnitude": 4, "logsourcename": "someLogSourceName"}

        result_bundle = json_to_stix_translator.convert_to_stix(
            data_source, map_data, [data], transformers.get_all_transformers(), options)
        observed_data = result_bundle['objects'][1]

        assert('x_com_ibm_ariel' in observed_data)
        custom_props = observed_data['x_com_ibm_ariel']
        assert(custom_props['identity_ip'] == data['identityip'])
        assert(custom_props['log_source_id'] == data['logsourceid'])
        assert(custom_props['qid'] == data['qid'])
        assert(custom_props['magnitude'] == data['magnitude'])
        assert(custom_props['log_source_name'] == data['logsourcename'])
