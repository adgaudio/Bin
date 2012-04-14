import urllib2
import BeautifulSoup

BASE_URL = "http://blip.tv/rss/flash/{}"
CHUNK_SIZE = 32768 * 16

def get_mp4_url(id=4898362):
    url = BASE_URL.format(id)
    page = urllib2.urlopen(url).read()
    data = BeautifulSoup.BeautifulSoup(page)

    part = data.fetch('media:content',
            attrs={'type':'video/mp4'},
            limit=1).pop()
    return part.attrMap['url']

def update_progress(current_position, total_size):
    print "{} of {} bytes ({}% complete)".format(
            current_position, total_size, current_position/total_size)
    return

def download(url, output_filepath, chunk_size=CHUNK_SIZE):
    with open(output_filepath, 'w') as f:
        stream = urllib2.urlopen(url)
        total_size = int(stream.headers['Content-Length'].strip())
        current_position = 0.0

        while True:
            if not stream:
                break
            part = stream.read(chunk_size)
            f.write(part)
            f.flush()

            current_position += len(part)
            update_progress(current_position, total_size)

def get_video(id=4898362):
    url = get_mp4_url(id)
    fp = url.split('/')[-1]
    download(url, fp)


if __name__ == '__main__':
    import sys
    id = sys.argv[1]
    get_video(id)
