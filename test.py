if __name__ == "__main__":

    original_url = "https://raw.githubusercontent.com/username/repo/main/image.jpg"
    new_url = original_url.replace("https://raw.githubusercontent.com/", "https://cdn.jsdelivr.net/gh/").replace("username/repo/", "username/repo@")
    print(new_url)