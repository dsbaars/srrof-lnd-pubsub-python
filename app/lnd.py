import codecs
import os
from functools import lru_cache
from os.path import expanduser
from dotenv.main import dotenv_values
import codecs, base64

import grpc

from grpc_gen import lightning_pb2, router_pb2 as lnrouter
from grpc_gen import router_pb2_grpc as lnrouterrpc
from grpc_gen import lightning_pb2 as ln
from grpc_gen import lightning_bp2_grpc as lnrpc

config = dotenv_values(".env")


MESSAGE_SIZE_MB = 50 * 1024 * 1024

class Lnd:
    def __init__(self, lnd_dir, server):
        os.environ["GRPC_SSL_CIPHER_SUITES"] = "HIGH+ECDSA"
        lnd_dir = expanduser(lnd_dir)
        combined_credentials = self.get_credentials(lnd_dir)
        channel_options = [
            ("grpc.max_message_length", MESSAGE_SIZE_MB),
            ("grpc.max_receive_message_length", MESSAGE_SIZE_MB),
        ]
        grpc_channel = grpc.secure_channel(
            server, combined_credentials, channel_options
        )
        self.stub = lnrpc.LightningStub(grpc_channel)
        self.router_stub = lnrouterrpc.RouterStub(grpc_channel)
        
    def get_channel_graph(self):
        request = ln.GraphTopologySubscription()
        return self.stub.SubscribeChannelGraph(request)

    @staticmethod
    def get_credentials(lnd_dir):
        tls_certificate = open(os.path.expanduser(config['CERT']), 'rb').read()
        ssl_credentials = grpc.ssl_channel_credentials(tls_certificate)
        with open(config['MACAROON'], "rb") as f:
            macaroon = codecs.encode(f.read(), "hex")
        auth_credentials = grpc.metadata_call_credentials(
            lambda _, callback: callback([("macaroon", macaroon)], None)
        )
        combined_credentials = grpc.composite_channel_credentials(
            ssl_credentials, auth_credentials
        )
        return combined_credentials

    # TODO: handle invalid channel ids
    def get_edge(self, channel_id):
        return self.stub.GetChanInfo(ln.ChanInfoRequest(chan_id=channel_id))

    def get_node_channels(self, pubkey):
        return self.stub.GetNodeInfo(ln.NodeInfoRequest(
            
            pub_key=pubkey, include_channels=True))

    def get_node_alias(self, pub_key):
        return self.stub.GetNodeInfo(
            ln.NodeInfoRequest(pub_key=pub_key, include_channels=False)
        ).node.alias

    def get_node(self, pub_key):
        return self.stub.GetNodeInfo(
            ln.NodeInfoRequest(pub_key=pub_key, include_channels=False)
        ).node

    # Query route, should give fee estimation of balancingß
    # FIXME: Work in progress
    def query_route(self, dest_pub_key, amt_sat, source_pub_key, hops, outgoing_channel_id):
        routeHints = []
        hopHints = []

        for h in hops:
            hopHints = []
            hopHints.append(lightning_pb2.HopHint(node_id=h))
            routeHints.append(lightning_pb2.RouteHint(hop_hints=hopHints))

        return self.stub.QueryRoutes(
            ln.QueryRoutesRequest(
                pub_key=dest_pub_key,
                amt=amt_sat,
                outgoing_chan_id=int(outgoing_channel_id),
                # source_pub_key=source_pub_key,
                route_hints=routeHints
            )
        )

    # Build Balancing Route
    # FIXME: Work in progress
    def build_route(self, dest_pub_key, amt_sat, source_pub_key, hops, outgoing_channel_id):
        hopHints = []

        for h in hops:
            b = bytes.fromhex(h)
            hopHints.append(b)

        return self.router_stub.BuildRoute(
            lnrouter.BuildRouteRequest(
            #    pub_key=dest_pub_key,
                amt_msat=amt_sat*1000,
                outgoing_chan_id=int(outgoing_channel_id),
                # source_pub_key=source_pub_key,
                hop_pubkeys=hopHints
            )
        )