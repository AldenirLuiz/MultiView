import requests

URL_SAMPLES = {
    "DVR": {
        "JFL": "rtsp://[USER]:[PASSWORD]@[IP]:[PORTA]/h264/ch[CHANNEL]/[STREAM]/av_stream",
        "Hikvision": "rtsp://[USER]:[PASSWORD]@[IP]:[PORTA]/Streaming/Channels/[CHANNEL]0[STREAM]",
        "Intelbras": "rtsp://[USER]:[PASSWORD]@[IP]:[PORTA]/cam/realmonitor?channel=[CHANNEL]&subtype=[STREAM]",
        "Luxvision": "rtsp://[USER]:[PASSWORD]@[IP]:[PORTA]/user=[USER]&password=[PASSWORD]&channel=[CHANNEL]&stream=[STREAM].sdp",
    },
    "CAMERA": {
        "Hikvision": "rtsp://[USER]:[PASSWORD]@[IP]:[PORTA]/Streaming/Channels/[STREAM]",
        "Intelbras": "rtsp://[USER]:[PASSWORD]@[IP]:[PORTA]/cam/realmonitor?channel=1&subtype=[STREAM]",
        "Luxvision": "rtsp://[USER]:[PASSWORD]@[IP]:[PORTA]/ch01/[STREAM]",
    },
    "OPT_DVR": {

        "JFL": {
            "STREAM": ["main", "sub"]
        },

        "Hikvision": {
            "STREAM": ["1", "2"]
        },

        "Intelbras": {
            "STREAM": ["0", "1"]
        },

        "Luxvision": {
            "STREAM": ["0", "1"]
        },
    }
}


class UrlBuilder:
    def __init__(self, brand:str, address:str, user:str, password:str, stream:str, port=554, device_type:str="DVR", channel:str="01"):
        self.brand = brand
        self.address = address
        self.user = user
        self.password = password
        self.port = port
        self.device_type = device_type.upper()
        self.protocol = "rtsp"
        self.channel = channel
        self.stream = stream

    def build(self):
        template = URL_SAMPLES[self.device_type][self.brand]

        return (
            template
            .replace("[USER]", self.user)
            .replace("[PASSWORD]", self.password)
            .replace("[IP]", self.address)
            .replace("[PORTA]", str(self.port))
            .replace("[CHANNEL]", str(self.channel))
            .replace("[STREAM]", str(self.stream))
        )

    def test_url(self):
        url = self.build()

        if url.startswith("rtsp://"):
            print("RTSP URL generated:")
            print(url)
            print("Use VLC, ffmpeg, OpenCV, or another RTSP client to test it.")
            return url

        response = requests.get(url, timeout=5)
        print(response.status_code)
        return response

if __name__ == "__main__":
    camera = UrlBuilder(
        brand="JFL",
        address="192.168.180.254",
        user="aldenir",
        password="lancer007",
        device_type="DVR",
        channel="01",
        stream="main",
    )

    print(camera.build())
    print(camera.test_url())