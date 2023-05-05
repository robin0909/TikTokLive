from TikTokLive import TikTokLiveClient
from TikTokLive.types.events import CommentEvent, ConnectEvent

# proxy='http://user-echotik-region-ph:112358@pr.roxlabs.cn:4600'
proxy = 'http://localhost:7890'

proxies = {
    'http://': proxy,
    'https://': proxy
}

# Instantiate the client with the user's username
client: TikTokLiveClient = TikTokLiveClient(unique_id="@giff.thiwashop", final_room_id="7229284279892642565",
                                            proxies=proxies, http_timeout=30)


# Define how you want to handle specific events via decorator
@client.on("connect")
async def on_connect(_: ConnectEvent):
    print("Connected to Room ID:", client.room_id)


# Notice no decorator?
async def on_comment(event: CommentEvent):
    print(f"{event.user.nickname} -> {event.comment}")


# Define handling an event via "callback"
client.add_listener("comment", on_comment)

if __name__ == '__main__':
    # Run the client and block the main thread
    # await client.start() to run non-blocking
    client.run()
