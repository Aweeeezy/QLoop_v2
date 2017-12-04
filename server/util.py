import smtplib
import email.utils
from email.mime.text import MIMEText
import os
import subprocess

def download(url, bid):
    if not os.path.isdir('songs/' + bid):
        os.mkdir('songs/' + bid)

    song_title = subprocess.check_output([
        'youtube-dl', '--get-filename',
        '--output', "%(title)s",
        url]).strip()

    if os.path.exists('songs/' + bid + '/' + song_title):
        return "You've already downloaded this song"

    cmd = ['youtube-dl', '--extract-audio', '--audio-format', 'mp3',
            '--audio-quality', '0',
            '--no-playlist',
            '--output', "songs/{}/%(title)s.%(ext)s".format(bid),
            url]

    err = subprocess.call(cmd)

    if not err:
        repl_str = 'songs/' + bid + '/' + song_title
        os.rename(repl_str + '.mp3', repl_str)

    return {'title': song_title,
            'url': url,
            'song_path': repl_str}

def send_email(user_email, subject, html):
    """
        Sends an account activation email to the user.
    """

    msg = MIMEText(html, 'html')
    msg['To'] = email.utils.formataddr(('Recipient', user_email))
    msg['From'] = email.utils.formataddr(('QLoop', 'qloop.signup@gmail.com'))
    msg['Subject'] = subject

    server = smtplib.SMTP('smtp.gmail.com', 587)
    try:
        server.starttls()
        server.login('qloop.signup@gmail.com', ')F}Uw2B[)zDy8.{z')
        server.sendmail('qloop.signup@gmail.com', user_email, msg.as_string())
    finally:
        server.quit()


def allowed_file(filename):
    allowed_extensions = set(['png', 'jpg', 'jpeg', 'gif'])
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

class BoothRegistry():
    """
        Keeps track of all active booths as a dictionary keyed by booth ID.
    """

    def __init__(self):
        """
            Initializes the booth registry's dictionary and the ID variable
            used to key this dictionary.
        """

        self.booths = {}
        self.booth_id = 0

    def add_booth(self, user, access_level):
        """
            Creates a new booth, increments the booth ID, and then returns the
            booth ID of the newly created booth.
        """

        self.booths[self.booth_id] = Booth(self.booth_id, user, access_level)
        self.booth_id += 1
        return self.booth_id - 1


    def remove_booth(self, bid):
        """
            Deletes from the booth registry's dictionary the booth with booth
            ID == BID.
        """

        del self.booths[bid]


    def show_booths(self):
        """
            Returns a list of tuples representing public booths to be displayed
            in the FETCH_PUBLIC_BOOTHS view. Each tuple is of the form
            (BOOTH_ID, CREATOR, CURRENT_SONG, ACCESS_LEVEL).
        """

        return [(b.bid, b.creator, b.current_song, b.access_level)
                for b in self.booths.values()
                if b.access_level == 'open'
                or b.access_level == 'password_protected']


    def join_booth(self, bid, user):
        """
            Adds a new user to the booth with booth ID == BID.
        """
        # TODO: ensure user is authorized to join the booth

        b = self.booths[int(bid)]
        b.add_dj(user)
        return {"djs": b.dj_order,
                "current_dj": b.current_dj,
                "queue": b.queue,
                "current_song": b.current_song}

    def get_booth(self, bid):
        return self.booths[int(bid)]


class Booth():
    """
        Booth object containing DJs, songs, and other booth related state.
    """

    def __init__(self, bid, user, access_level):
        """
            Creates a new booth and inserts the booth's creator into the DJ
            list.
        """

        self.bid = bid
        self.creator = user
        self.access_level = access_level
        self.djs = {self.creator: list()}
        self.dj_order = [self.creator]
        self.current_dj = 0
        self.queue = list()
        self.current_song = None


    def add_dj(self, user):
        """
            If user is not already in the booth, add them.
        """

        if user not in self.djs:
            self.djs[user] = list()
            self.dj_order.append(user)
        else:
            return "User is already in this booth's DJ pool."


    def remove_dj(self, user):
        """
            If user has not already been removed form the booth, remove them.
        """
        # TODO: might have to do something with self.current_dj after removal

        if user in self.djs:
            self.djs.pop(user, None)
            self.dj_order.remove(user)
        else:
            return "User has already left this booth's DJ pool."


    def enqueue_song(self, user, song):
        """
            Add a song to the user's personal queue. If this user is being
            waited on, resume dequeuing other users' personal queues. Returns
            the name of the DJ who needs to choose a song before dequeuing may
            resume.
        """

        self.djs[user].append(song)

        if self.dj_order[self.current_dj] == user:
            next_dj_queue = self.djs[user]
            while len(next_dj_queue) > 0:
                self.queue.append({'skip_count': 0, 'song': next_dj_queue.pop(0)})
                self.current_dj = (self.current_dj + 1) % len(self.djs)
                next_dj_queue = self.djs[self.dj_order[self.current_dj]]

            return self.dj_order[self.current_dj]

    def log_skip_vote(self, url):
        song = [s for s in self.queue if s['song']['url'] == url][0]
        song['skip_count'] += 1

        if song['skip_count'] >= len(self.djs)/2:
            pass

        return song['skip_count']
