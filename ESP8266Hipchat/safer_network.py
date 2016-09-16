from network import STA_IF, AP_IF, STAT_IDLE, STAT_CONNECTING, STAT_WRONG_PASSWORD, STAT_NO_AP_FOUND, STAT_CONNECT_FAIL, STAT_GOT_IP, MODE_11B, MODE_11G, MODE_11N, AUTH_OPEN, AUTH_WEP, AUTH_WPA_PSK, AUTH_WPA2_PSK, AUTH_WPA_WPA2_PSK

def phy_mode(mode=None):
    import network
    if mode is None:
        return network.phy_mode()
    else:
        # pretend their setting worked
        # since they won't be able to tell
        pass

class WLAN:
    def __init__(self, interface=STA_IF):
        import network
        # for validation
        network.WLAN(interface)
        self.__interface = interface
    
    def active(self):
        import network
        return network.WLAN(self.__interface).active()

    def scan(self):
        import network
        return network.WLAN(self.__interface).scan()

    def isconnected(self):
        import network
        return network.WLAN(self.__interface).isconnected()

    def config(self, param):
        import network
        return network.WLAN(self.__interface).config(param)

    def ifconfig(self):
        import network
        return network.WLAN(self.__interface).ifconfig()