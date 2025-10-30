from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from channels.exceptions import StopConsumer
from channels.generic.websocket import AsyncConsumer
from django.db.models import Q
import json
from datetime import datetime


class VideoCallConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        self.user = self.scope["user"]
        self.room_id = f"videocall_{self.user.id}"

        await self.channel_layer.group_add(
            self.room_id,
            self.channel_name
        )
        await self.send({
            "type": "websocket.accept"
        })

    async def websocket_receive(self, event):
        text_data = event.get("text", None)

        if text_data:
            data = json.loads(text_data)
            action = data.get("action", None)

            if action == "initiate_call":
                receiver_username = data.get("receiver_username", None)
                if not receiver_username:
                    response = {
                        'action': 'error',
                        'status_code': 400,
                        'message': 'Receiver username required'
                    }
                    await self.send({
                        "type": "websocket.send",
                        "text": json.dumps(response)
                    })
                    return
                status_code, video_call = await self.create_video_call(receiver_username)
                if status_code == 201:
                    response = {
                        "action": "call_initiated",
                        "status_code": status_code,
                        "video_call_id": video_call.id if video_call else None,
                        "message": "Send request to user for contacting..."
                    }
                    if video_call.status == "RINGING":
                        await self.channel_layer.group_send(
                            f"videocall_{video_call.receiver_id}",
                            {
                                "type": "chat_message",
                                "text": json.dumps({
                                    "action": "incoming_call",
                                    "video_call_id": video_call.id,
                                    "caller_username": video_call.caller.username
                                })
                            }
                        )
                elif status_code == 404:
                    response = {
                        'action': 'error',
                        'status_code': status_code,
                        'message': 'User not found'
                    }
                elif status_code == 409:
                    response = {
                        'action': 'error',
                        'status_code': status_code,
                        'message': 'User already in another call'
                    }
                else:
                    response = {
                        'action': 'error',
                        'status_code': status_code,
                        'message': 'Unknown error'
                    }
                await self.send({
                    "type": "websocket.send",
                    "text": json.dumps(response)
                })

            elif action == "cancel_call":
                video_call_id = data.get("video_call_id", None)
                if not video_call_id:
                    response = {
                        'action': 'error',
                        'status_code': 400,
                        'message': 'Video call ID required'
                    }
                    await self.send({
                        "type": "websocket.send",
                        "text": json.dumps(response)
                    })
                    return
                status_code, video_call = await self.change_video_call_status(video_call_id, "MISSED")
                if status_code == 200:
                    if self.user not in [video_call.caller, video_call.receiver]:
                        response = {
                            'action': 'error',
                            'status_code': 403,
                            'message': 'Permission denied'
                        }
                        await self.send({
                            "type": "websocket.send",
                            "text": json.dumps(response)
                        })
                        return
                    self.scope["session"]["video_call_id"] = None
                    await sync_to_async(self.scope["session"].save)()
                    response = {
                        "action": "call_canceled",
                        "status_code": status_code
                    }
                    await self.channel_layer.group_send(
                        f"videocall_{video_call.receiver_id}",
                        {
                            "type": "chat_message",
                            "text": json.dumps({
                                "action": "call_canceled",
                                "status_code": status_code
                            })
                        }
                    )
                elif status_code == 404:
                    response = {
                        'action': 'error',
                        'status_code': status_code,
                        'message': 'Video call not found'
                    }
                else:
                    response = {
                        'action': 'error',
                        'status_code': status_code,
                        'message': 'Unknown error'
                    }
                await self.send({
                    "type": "websocket.send",
                    "text": json.dumps(response)
                })

            elif action == "change_status":
                video_call_id = data.get("video_call_id", None)
                new_status = data.get("status", None)
                if not video_call_id or not new_status:
                    response = {
                        'action': 'error',
                        'status_code': 400,
                        'message': 'Video call ID and status required'
                    }
                    await self.send({
                        "type": "websocket.send",
                        "text": json.dumps(response)
                    })
                    return
                status_code, video_call = await self.change_video_call_status(video_call_id, new_status)
                if status_code == 200:
                    if self.user not in [video_call.caller, video_call.receiver]:
                        response = {
                            'action': 'error',
                            'status_code': 403,
                            'message': 'Permission denied'
                        }
                        await self.send({
                            "type": "websocket.send",
                            "text": json.dumps(response)
                        })
                        return
                    response = {
                        "action": "status_changed",
                        "status_code": status_code,
                        "new_status": new_status
                    }
                elif status_code == 404:
                    response = {
                        'action': 'error',
                        "status_code": status_code,
                        'message': 'Video call not found'
                    }
                else:
                    response = {
                        'action': 'error',
                        'status_code': status_code,
                        'message': 'Unknown error'
                    }
                await self.send({
                    "type": "websocket.send",
                    "text": json.dumps(response)
                })

            elif action == "start_call":
                video_call_id = data.get("video_call_id", None)
                if not video_call_id:
                    response = {
                        'action': 'error',
                        'status_code': 400,
                        'message': 'Video call ID required'
                    }
                    await self.send({
                        "type": "websocket.send",
                        "text": json.dumps(response)
                    })
                    return
                status_code, video_call = await self.start_video_call(video_call_id)
                if status_code == 200:
                    if self.user not in [video_call.caller, video_call.receiver]:
                        response = {
                            'action': 'error',
                            'status_code': 403,
                            'message': 'Permission denied'
                        }
                        await self.send({
                            "type": "websocket.send",
                            "text": json.dumps(response)
                        })
                        return
                    self.scope["session"]["video_call_id"] = video_call_id
                    await sync_to_async(self.scope["session"].save)()
                    response = {
                        "action": "call_started",
                        "status_code": status_code,
                        "video_call_id": video_call.id if video_call else None,
                        "message": "Call started"
                    }
                    await self.channel_layer.group_send(
                        f"videocall_{video_call.receiver_id}",
                        {
                            "type": "chat_message",
                            "text": json.dumps(response)
                        }
                    )
                    await self.channel_layer.group_send(
                        f"videocall_{video_call.caller_id}",
                        {
                            "type": "chat_message",
                            "text": json.dumps(response)
                        }
                    )
                else:
                    if status_code == 404:
                        response = {
                            'action': 'error',
                            'status_code': status_code,
                            'message': 'Video call not found'
                        }
                    else:
                        response = {
                            'action': 'error',
                            'status_code': status_code,
                            'message': 'Unknown error'
                        }
                    await self.send({
                        "type": "websocket.send",
                        "text": json.dumps(response)
                    })

            elif action == "end_call":
                video_call_id = data.get("video_call_id", None)
                if not video_call_id:
                    response = {
                        'action': 'error',
                        'status_code': 400,
                        'message': 'Video call ID required'
                    }
                    await self.send({
                        "type": "websocket.send",
                        "text": json.dumps(response)
                    })
                    return
                status_code, video_call = await self.end_video_call(video_call_id)
                if status_code == 200:
                    if self.user not in [video_call.caller, video_call.receiver]:
                        response = {
                            'action': 'error',
                            'status_code': 403,
                            'message': 'Permission denied'
                        }
                        await self.send({
                            "type": "websocket.send",
                            "text": json.dumps(response)
                        })
                        return
                    self.scope["session"]["video_call_id"] = None
                    await sync_to_async(self.scope["session"].save)()
                    response = {
                        "action": "call_ended",
                        "status_code": status_code,
                        "video_call_id": video_call.id if video_call else None,
                        "message": "Call ended"
                    }
                    await self.channel_layer.group_send(
                        f"videocall_{video_call.receiver_id}",
                        {
                            "type": "chat_message",
                            "text": json.dumps(response)
                        }
                    )
                    await self.channel_layer.group_send(
                        f"videocall_{video_call.caller_id}",
                        {
                            "type": "chat_message",
                            "text": json.dumps(response)
                        }
                    )
                else:
                    if status_code == 404:
                        response = {
                            'action': 'error',
                            'status_code': status_code,
                            'message': 'Video call not found'
                        }
                    else:
                        response = {
                            'action': 'error',
                            'status_code': status_code,
                            'message': 'Unknown error'
                        }
                    await self.send({
                        "type": "websocket.send",
                        "text": json.dumps(response)
                    })

            elif action == "caller_data":
                video_call_id = data.get("video_call_id", None)
                if not video_call_id:
                    response = {
                        'action': 'error',
                        'status_code': 400,
                        'message': 'Video call ID required'
                    }
                    await self.send({
                        "type": "websocket.send",
                        "text": json.dumps(response)
                    })
                    return
                status_code, video_call = await self.get_video_call(video_call_id)
                if status_code == 200:
                    if self.user != video_call.caller:
                        response = {
                            'action': 'error',
                            'status_code': 403,
                            'message': 'Permission denied'
                        }
                        await self.send({
                            "type": "websocket.send",
                            "text": json.dumps(response)
                        })
                        return
                    response = {
                        "action": "receiver_data",
                        "status_code": status_code,
                        "video_call_id": video_call.id if video_call else None,
                        "sdp": data.get("sdp", None),
                        "candidate": data.get("candidate", None),
                        "message": "Caller data received"
                    }
                    await self.channel_layer.group_send(
                        f"videocall_{video_call.receiver_id}",
                        {
                            "type": "chat_message",
                            "text": json.dumps(response)
                        }
                    )
                else:
                    if status_code == 404:
                        response = {
                            'action': 'error',
                            'status_code': status_code,
                            'message': 'Video call not found'
                        }
                    else:
                        response = {
                            'action': 'error',
                            'status_code': status_code,
                            'message': 'Unknown error'
                        }
                    await self.send({
                        "type": "websocket.send",
                        "text": json.dumps(response)
                    })

            elif action == "receiver_data":
                video_call_id = data.get("video_call_id", None)
                if not video_call_id:
                    response = {
                        'action': 'error',
                        'status_code': 400,
                        'message': 'Video call ID required'
                    }
                    await self.send({
                        "type": "websocket.send",
                        "text": json.dumps(response)
                    })
                    return
                status_code, video_call = await self.get_video_call(video_call_id)
                if status_code == 200:
                    if self.user != video_call.receiver:
                        response = {
                            'action': 'error',
                            'status_code': 403,
                            'message': 'Permission denied'
                        }
                        await self.send({
                            "type": "websocket.send",
                            "text": json.dumps(response)
                        })
                        return
                    response = {
                        "action": "caller_data",
                        "status_code": status_code,
                        "video_call_id": video_call.id if video_call else None,
                        "sdp": data.get("sdp", None),
                        "candidate": data.get("candidate", None),
                        "message": "Receiver data received"
                    }
                    await self.channel_layer.group_send(
                        f"videocall_{video_call.caller_id}",
                        {
                            "type": "chat_message",
                            "text": json.dumps(response)
                        }
                    )
                else:
                    if status_code == 404:
                        response = {
                            'action': 'error',
                            'status_code': status_code,
                            'message': 'Video call not found'
                        }
                    else:
                        response = {
                            'action': 'error',
                            'status_code': status_code,
                            'message': 'Unknown error'
                        }
                    await self.send({
                        "type": "websocket.send",
                        "text": json.dumps(response)
                    })

    async def websocket_disconnect(self, event):
        try:
            await self.channel_layer.group_discard(
                self.room_id,
                self.channel_name
            )
        except Exception as e:
            print(f"Error in group_discard: {e}")
        try:
            video_call_id = self.scope["session"].get("video_call_id")
            if video_call_id:
                status_code, video_call = await self.get_video_call(video_call_id)
                if status_code == 200:
                    await self.end_video_call(video_call_id)
                    try:
                        await self.channel_layer.group_send(
                            f"videocall_{video_call.caller.id}",
                            {"type": "chat_message", "text": json.dumps({"action": "disconnected"})}
                        )
                        await self.channel_layer.group_send(
                            f"videocall_{video_call.receiver.id}",
                            {"type": "chat_message", "text": json.dumps({"action": "disconnected"})}
                        )
                    except:
                        pass
                self.scope["session"]["video_call_id"] = None
                await sync_to_async(self.scope["session"].save)()
        except Exception as e:
            print(f"Error in cleanup: {e}")
        raise StopConsumer()

    async def chat_message(self, event):
        await self.send({
            "type": "websocket.send",
            "text": event["text"]
        })

    @database_sync_to_async
    def get_video_call(self, call_id):
        from .models import VideoCall
        try:
            video_call = VideoCall.objects.get(id=call_id)
            if self.user not in [video_call.caller, video_call.receiver]:
                return 403, None
            return 200, video_call
        except VideoCall.DoesNotExist:
            return 404, None

    @database_sync_to_async
    def create_video_call(self, receiver_username):
        from .models import VideoCall, User
        try:
            receiver = User.objects.get(username=receiver_username)
        except User.DoesNotExist:
            return 404, None
        if VideoCall.objects.filter(Q(receiver=receiver, status='CONNECTED') | Q(caller=receiver, status='CONNECTED')).exists():
            return 409, None
        video_call = VideoCall.objects.create(caller=self.user, receiver=receiver)
        self.scope["session"]["video_call_id"] = video_call.id
        self.scope["session"].save()
        return 201, video_call

    @database_sync_to_async
    def change_video_call_status(self, video_call_id, status):
        from .models import VideoCall
        try:
            video_call = VideoCall.objects.get(id=video_call_id)
            if self.user not in [video_call.caller, video_call.receiver]:
                return 403, None
            video_call.status = status
            video_call.save()
            return 200, video_call
        except VideoCall.DoesNotExist:
            return 404, None

    @database_sync_to_async
    def start_video_call(self, video_call_id):
        from .models import VideoCall
        try:
            video_call = VideoCall.objects.get(id=video_call_id)
            if self.user not in [video_call.caller, video_call.receiver]:
                return 403, None
            video_call.status = 'CONNECTED'
            video_call.start_time = datetime.now()
            video_call.save()
            return 200, video_call
        except VideoCall.DoesNotExist:
            return 404, None

    @database_sync_to_async
    def end_video_call(self, video_call_id):
        from .models import VideoCall
        try:
            video_call = VideoCall.objects.get(id=video_call_id)
            if self.user not in [video_call.caller, video_call.receiver]:
                return 403, None
            video_call.status = 'ENDED'
            video_call.call_end_time = datetime.now()
            video_call.save()
            return 200, video_call
        except VideoCall.DoesNotExist:
            return 404, None