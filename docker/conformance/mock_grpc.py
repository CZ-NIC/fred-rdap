#!/usr/bin/python3
"""Mock Fred gRPC services for conformance tests."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

import grpc
from fred_api.registry.contact.contact_info_types_pb2 import (ContactIdReply, ContactIdRequest, ContactInfoReply,
                                                              ContactInfoRequest, WarningLetter)
from fred_api.registry.contact.contact_state_types_pb2 import ContactStateReply, ContactStateRequest
from fred_api.registry.contact.service_contact_grpc_pb2_grpc import (ContactServicer as _ContactServicer,
                                                                     add_ContactServicer_to_server)
from grpc import RpcContext


class ContactServicer(_ContactServicer):
    def get_contact_info(self, request: ContactInfoRequest, context: RpcContext) -> ContactInfoReply:
        reply = ContactInfoReply()
        reply.data.contact_id.uuid.value = request.contact_id.uuid.value
        reply.data.contact_handle.value = request.contact_id.uuid.value
        reply.data.sponsoring_registrar.value = 'REGGIE'
        reply.data.events.registered.registrar_handle.value = 'REGGIE'
        reply.data.events.registered.timestamp.FromDatetime(datetime.now())
        reply.data.events.transferred.registrar_handle.value = 'REGGIE'
        reply.data.warning_letter.preference = WarningLetter.SendingPreference.Enum.to_send
        return reply

    def get_contact_id(self, request: ContactIdRequest, context: RpcContext) -> ContactIdReply:
        if request.contact_handle.value == 'KOCHANSKI':
            reply = ContactIdReply()
            reply.exception.contact_does_not_exist.CopyFrom(ContactIdReply.Exception.ContactDoesNotExist())
            return reply

        reply = ContactIdReply()
        reply.data.contact_id.uuid.value = request.contact_handle.value
        return reply

    def get_contact_state(self, request: ContactStateRequest, context: RpcContext) -> ContactStateReply:
        reply = ContactStateReply()
        reply.data.state.flags['linked'] = False
        return reply


def main() -> None:
    """Run the server."""
    server = grpc.server(ThreadPoolExecutor())
    add_ContactServicer_to_server(ContactServicer(), server)
    server.add_insecure_port('[::]:50050')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    main()
