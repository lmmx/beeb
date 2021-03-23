from ..channel_ids import ChannelPicker


class RemoteMixIn:
    @property
    def channel(self):
        return ChannelPicker.by_id(self.channel_id)
