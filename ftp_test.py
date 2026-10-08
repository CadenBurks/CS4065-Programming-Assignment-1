from ftp_client import FtpClient

client = FtpClient()
client.DEBUG = True

client.connect("caden", "burks")
client.get_file("ftp_test.txt")
client.disconnect()
