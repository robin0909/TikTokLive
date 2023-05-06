import json
import sys
from TikTokLive import TikTokLiveClient
from TikTokLive.types.events import CommentEvent, ConnectEvent, LikeEvent, JoinEvent, FollowEvent, LiveEndEvent, \
    DisconnectEvent, ViewerUpdateEvent, ShareEvent, RankingUpdateEvent


class LiveStream:

    def __init__(self, unique_id: str, room_id: str, proxy: str):
        super(LiveStream, self).__init__()
        self.unique_id: str = unique_id
        self.room_id: str = room_id
        self.proxies = {
            'http://': proxy,
            'https://': proxy
        }
        self.client: TikTokLiveClient = TikTokLiveClient(unique_id=unique_id, final_room_id=room_id,
                                                         proxies=self.proxies, ws_timeout=30,
                                                         http_timeout=30)
        self.add_hook()

    def add_hook(self):
        client = self.client

        @client.on("connect")
        async def on_connect(_: ConnectEvent):
            self.room_id = client.room_id
            print(json.dumps(
                {"action": "connect", "unique_id": self.unique_id, "room_id": self.room_id,
                 "event": {"unique_id": self.unique_id}}))

        @client.on("comment")
        async def on_comment(event: CommentEvent):
            print(json.dumps({"action": "comment", "unique_id": self.unique_id, "room_id": self.room_id, "event": {
                "user": {"userId": event.user.user_id, "nickname": event.user.nickname,
                         "uniqueId": event.user.unique_id},
                "comment": event.comment
            }}))

        @client.on("like")
        async def on_like(event: LikeEvent):
            print(json.dumps({"action": "like", "unique_id": self.unique_id, "room_id": self.room_id, "event": {
                "user": {"userId": event.user.user_id, "nickname": event.user.nickname,
                         "uniqueId": event.user.unique_id},
                "likeCount": event.likes,
                "totalLikeCount": event.total_likes,
                "displayType": event.display_type,
                "label": event.label
            }}))

        @client.on("join")
        async def on_join(event: JoinEvent):
            print(json.dumps({"action": "join", "unique_id": self.unique_id, "room_id": self.room_id, "event": {
                "user": {"userId": event.user.user_id, "nickname": event.user.nickname,
                         "uniqueId": event.user.unique_id},
                "displayType": event.display_type,
                "label": event.label
            }}))

        @client.on("follow")
        async def on_follow(event: FollowEvent):
            print(json.dumps({"action": "follow", "unique_id": self.unique_id, "room_id": self.room_id, "event": {
                "user": {"userId": event.user.user_id, "nickname": event.user.nickname,
                         "uniqueId": event.user.unique_id},
                "displayType": event.display_type,
                "label": event.label
            }}))

        @client.on("viewer_update")
        async def on_viewer_count_update(event: ViewerUpdateEvent):
            print(json.dumps(
                {"action": "viewer_count_update", "unique_id": self.unique_id, "room_id": self.room_id, "event": {
                    "viewerCount": event.viewer_count
                }}))

        @client.on("share")
        async def on_share(event: ShareEvent):
            print(json.dumps({"action": "share", "unique_id": self.unique_id, "room_id": self.room_id, "event": {
                "user": {"userId": event.user.user_id, "nickname": event.user.nickname,
                         "uniqueId": event.user.unique_id},
                "displayType": event.display_type,
                "label": event.label
            }}))

        @client.on("ranking_update")
        async def on_weekly_ranking(event: RankingUpdateEvent):
            print(
                json.dumps({"action": "weekly_ranking", "unique_id": self.unique_id, "room_id": self.room_id, "event": {
                    "rankings": event.rank
                }}))

        @client.on("live_end")
        async def on_live_end(event: LiveEndEvent):
            print(json.dumps({"action": "live_end", "unique_id": self.unique_id, "room_id": self.room_id, "event": {}}))

        @client.on("disconnect")
        async def on_disconnect(event: DisconnectEvent):
            print(
                json.dumps({"action": "disconnect", "unique_id": self.unique_id, "room_id": self.room_id, "event": {}}))

    def run(self):
        self.client.run()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        LiveStream(sys.argv[1], sys.argv[2], sys.argv[3]).run()
    else:
        # LiveStream("arganiahq", "http://customer-82602c-country-MY:94f1fb20@proxy.ipipgo.com:31212").run()
        # LiveStream("sarwendahofficial", "http://user-echotik-region-id:112358@pr.roxlabs.cn:4600").run()
        LiveStream("fiyangrosir", "", "http://127.0.0.1:7890").run()
