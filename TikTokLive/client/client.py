import logging
import traceback
from typing import Optional, List

from pyee import AsyncIOEventEmitter

from .base import WebcastPushConnection
from ..types import FailedParseMessage, TopViewer
from ..types.events import AbstractEvent, ConnectEvent, DisconnectEvent, ViewerUpdateEvent, JoinEvent, LikeEvent, \
    FollowEvent, ShareEvent, QuestionEvent, LiveEndEvent, \
    IntroMessageEvent, EmoteEvent, MicBattleStartEvent, MicBattleUpdateEvent, MoreShareEvent, UnknownEvent, \
    CommentEvent, GiftEvent, RankingUpdateEvent, UserRankingUpdateEvent


class TikTokLiveClient(WebcastPushConnection, AsyncIOEventEmitter):
    """
    TikTokLive Client responsible for emitting events asynchronously

    """

    def __init__(self, unique_id: str, **options):
        """
        Initialize the WebcastPushConnection for TikTokLive Webcast tracking

        :param unique_id: The unique id of the creator to connect to
        :param options: Extra options from the WebcastPushConnection

        """

        AsyncIOEventEmitter.__init__(self)
        WebcastPushConnection.__init__(self, unique_id, **options)

        self.__viewer_count: Optional[int] = None
        self.__top_viewers: List[TopViewer] = []
        self.add_listener('viewer_update', self._on_viewer_update)

    async def _on_viewer_update(self, event: ViewerUpdateEvent):
        """
        Set the viewer count when one is received via a viewer count update event.
        Also, set the top viewers!
        
        """

        self.__viewer_count = event.viewer_count or self.__viewer_count
        self.__top_viewers = event.top_viewers or self.__top_viewers

    async def _on_error(self, original: Exception, append: Optional[Exception]) -> None:
        """
        Send errors to the _on_error handler for handling, appends a custom exception

        :param original: The original Python exception
        :param append: The specific exception
        :return: None

        """

        _exc = original

        # If adding on to it
        if append:
            try:
                raise append from original
            except Exception as ex:
                _exc = ex

        # If not connected, just raise it
        if not self.connected:
            raise _exc

        # If connected and there is no handler
        if len(self.listeners("error")) < 1:
            self._log_error(_exc)
            return

        # If connected and there IS an error handler
        self.emit("error", _exc)

    @classmethod
    def _log_error(cls, exception: Exception) -> None:
        """
        Log an error

        :param exception: The exception
        :return: None

        """

        try:
            raise exception
        except:
            logging.error(traceback.format_exc())

    async def _on_connect(self) -> None:
        """
        Emit an event when we have connected

        """

        if self.connected:
            event: ConnectEvent = ConnectEvent()
            self.emit("connect", event)

    def _disconnect(self) -> None:
        """
        Wrap disconnection in a disconnect event

        """

        super(TikTokLiveClient, self)._disconnect()
        event: DisconnectEvent = DisconnectEvent()
        self.emit("disconnect", event)

    async def _handle_webcast_messages(self, webcast_response: dict) -> None:
        """
        Handle webcast messages using an event emitter
        :param webcast_response: The response

        """

        # Parse the Webcast messages into an event
        # Messages for which protobuf has not been finished still show up here & are handled as UnknownEvent events
        for message in webcast_response.get("messages", list()):
            # Once we disconnect, stop parsing events
            if self.websocket is None:
                break

            # Parse events & emit them
            try:
                event: AbstractEvent = self._parse_webcast_message(message)
                self.emit(event.name, event)
            except Exception as ex:
                await self._on_error(ex, FailedParseMessage("Failed parsing of a webcast message"))

    def _parse_webcast_message(self, webcast_message: dict) -> Optional[AbstractEvent]:
        """
        Parse a webcast message into an event and return to the caller

        :param webcast_message: The message to parse
        :return: The parsed object of base-type AbstractEvent

        """

        # Perform flattening (some events are highly nested)
        if "event" in webcast_message:
            webcast_message = {**webcast_message.get("event", dict()).get("details", dict()), **webcast_message}
            del webcast_message["event"]

        # Custom handler for livestream ending
        if webcast_message.get("type") == "WebcastControlMessage":
            if webcast_message.get("action") == 3:
                self._disconnect()
                event: AbstractEvent = LiveEndEvent()
                event.raw_data = webcast_message
                return event

        # If "enable_extended_gift_info" is enabled, provide extra detail
        if webcast_message.get("type") == "WebcastGiftMessage":
            webcast_message: dict
            webcast_message["detailed"] = self.available_gifts.get(webcast_message.get('id'))

        # For most events, we map the webcast message type
        mapping: Optional[AbstractEvent] = (
            {
                "WebcastGiftMessage": GiftEvent,
                "WebcastChatMessage": CommentEvent,
                "WebcastRoomUserSeqMessage": ViewerUpdateEvent,
                "WebcastMemberMessage": JoinEvent,
                "WebcastLikeMessage": LikeEvent,
                "WebcastRankUpdateMessage": RankingUpdateEvent,
                "WebcastHourlyRankMessage": RankingUpdateEvent,
                "WebcastQuestionNewMessage": QuestionEvent,
                "WebcastLiveIntroMessage": IntroMessageEvent,
                "WebcastEmoteChatMessage": EmoteEvent,
                "WebcastLinkMicBattle": MicBattleStartEvent,
                "WebcastLinkMicArmies": MicBattleUpdateEvent,
                "WebcastRankTextMessage": UserRankingUpdateEvent
            }.get(webcast_message.get('type'))
        )

        # Sometimes, we need to use the display_type attribute
        mapping: Optional[AbstractEvent] = mapping or (
            {
                "pm_main_follow_message_viewer_2": FollowEvent,
                "pm_mt_guidance_share": ShareEvent,
                "pm_mt_guidance_viewer_5_share": MoreShareEvent,
                "pm_mt_guidance_viewer_10_share": MoreShareEvent
            }.get(webcast_message.get('display_type'))
        )

        # Build the event from the webcast message
        event: AbstractEvent = (
            mapping.from_dict(webcast_message)
            if mapping else
            UnknownEvent.from_dict(webcast_message)
        )

        # Set the raw data & return the event
        event.raw_data = webcast_message

        # noinspection PyProtectedMember
        event._forward_client(self)
        return event

    @property
    def viewer_count(self) -> Optional[int]:
        """
        Return viewer count of user

        """

        return self.__viewer_count

    @property
    def top_viewers(self) -> List[TopViewer]:
        """
        An array of the top viewers in the stream measured by coins given

        """

        return self.__top_viewers
