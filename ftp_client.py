# ftp_client.py
from ftplib import FTP

def ftp_client():
    ftp_server = "ftp.dlptest.com"
    username = "dlpuser"
    password = "rNrKYTX9g7z3RgJRmxWuGHbeu"

    try:
        ftp = FTP(ftp_server)
        ftp.login(user=username, passwd=password)
        print("Connected to FTP server.")

        # List directory contents
        print("\n=== Directory Listing ===")
        ftp.retrlines("LIST")

        # Upload a file
        with open("ftp.txt", "w") as f:
            f.write("This is a test upload file.")

        with open("ftp.txt", "rb") as f:
            ftp.storbinary("STOR test_upload.txt", f)
        print("\nFile uploaded successfully!")

        # Download the file
        with open("downloaded_test.txt", "wb") as f:
            ftp.retrbinary("RETR test_upload.txt", f.write)
        print("File downloaded successfully!")

        ftp.quit()

    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    ftp_client()
