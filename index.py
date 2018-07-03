import datetime
import pytz
import sys

from subprocess import Popen, PIPE


def convert_to_kst(input_datetime):
    tzname = input_datetime.tzname()
    if tzname == 'KST':
        return input_datetime
    elif tzname is None:
        raise ValueError("Timezone must be set.")
    else:
        return input_datetime.astimezone(pytz.timezone('Asia/Seoul'))


def convert_timestamp_to_kst(timestamp):
    return datetime.datetime.fromtimestamp(int(timestamp)).astimezone(pytz.timezone('Asia/Seoul'))


def get_week_num(input_datetime):
    input_datetime = convert_to_kst(input_datetime)
    isocalendar = input_datetime.isocalendar()
    return '{}W{}'.format(str(isocalendar[0])[2:], "%02d" % isocalendar[1])


def get_month_num(input_datetime):
    input_datetime = convert_to_kst(input_datetime)
    return '{}M{}'.format(str(input_datetime.year)[2:], str("%02d" % input_datetime.month))


def parse_repo_list():
    file = open('repo-list.txt', 'r')
    path_list = [line.rstrip('\n') for line in file.readlines()]
    return path_list


def get_commits(path):
    popen = Popen('cd {} && git rev-list --timestamp --all'.format(path), shell=True, stdout=PIPE)
    output = popen.stdout.read().decode('utf-8')
    return output.split('\n')


class CommitDateParser:
    def __init__(self):
        self.weekly = {}
        self.monthly = {}

    def _parse_commit(self, commit):
        if commit == '':
            return
        timestamp, _ = commit.split(' ')
        dt = convert_timestamp_to_kst(timestamp)
        week_num = get_week_num(dt)
        month_num = get_month_num(dt)
        self.weekly.setdefault(week_num, 0)
        self.weekly[week_num] += 1
        self.monthly.setdefault(month_num, 0)
        self.monthly[month_num] += 1

    def parse(self):
        repo_list = parse_repo_list()
        for repo in repo_list:
            commits = get_commits(repo)
            for commit in commits:
                self._parse_commit(commit)

    def print(self, num_line=None):
        sorted_weekly = sorted(self.weekly.items())
        sorted_monthly = sorted(self.monthly.items())
        if num_line is None:
            num_line = len(sorted_weekly)
        print("======== WEEKLY ========")
        for i in range(num_line):
            try:
                weekly = sorted_weekly[i]
                print('{}: {}'.format(weekly[0], weekly[1]))
            except IndexError:
                break
        print("=========================")
        print("======== MONTHLY ========")
        for i in range(num_line):
            try:
                monthly = sorted_monthly[i]
                print('{}: {}'.format(monthly[0], monthly[1]))
            except IndexError:
                break
        print("=========================")


if __name__ == "__main__":
    parser = CommitDateParser()
    parser.parse()
    try:
        lines = int(sys.argv[1])
    except (IndexError, ValueError):
        lines = None
    parser.print(lines)
