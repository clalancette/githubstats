#!/usr/bin/env python

# Copyright 2017 Open Source Robotics Foundation, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import argparse
import datetime
import operator
import dateutil.relativedelta

import github
import retrying

class RepoStatistics(object):
    def __init__(self, name, total_issues, closed_issues, num_commits, num_commit_comments, issue_comment_count, total_pr_comments):
        self.name = name
        self.total_issues = total_issues
        self.closed_issues = closed_issues
        self.num_commits = num_commits
        self.num_commit_comments = num_commit_comments
        self.issue_comment_count = issue_comment_count
        self.total_pr_comments = total_pr_comments

    def _sum(self):
        return self.total_issues + self.num_commits + self.num_commit_comments + self.issue_comment_count + self.total_pr_comments

    def __eq__(self, other):
        return self._sum() == other._sum()

    def __lt__(self, other):
        return self._sum() < other._sum()

    def __str__(self):
        return "Name: %s, total issues: %d, closed issues: %d, commits: %d, commit comments: %d, issue comments: %d, PR comments: %d, sum: %d" % (self.name, self.total_issues, self.closed_issues, self.num_commits, self.num_commit_comments, self.issue_comment_count, self.total_pr_comments, self._sum())

    def csv(self):
        return "%s,%d,%d,%d,%d,%d,%d,%d" % (self.name, self.total_issues, self.closed_issues, self.num_commits, self.num_commit_comments, self.issue_comment_count, self.total_pr_comments, self._sum())

    @staticmethod
    def header():
        return "Name,Total Issues,Closed Issues,Commits,Commit Comments,Issue Comments,PR Comments,Sum"

def valid_date(s):
    try:
        return datetime.datetime.strptime(s, "%Y-%m-%d")
    except ValueError:
        raise argparse.ArgumentTypeError("Not a valid date: '{0}'.".format(s))

parser = argparse.ArgumentParser("Get sorted count of issues opened in the last year from one or more github organizations.")
parser.add_argument("-o", "--organization", action='append', required=False, dest='organizations', default=[],
                    help='organization to fetch data from; can be passed more than once')
parser.add_argument("-p", "--password", action='store', required=True, dest='password',
                    help='password to use for github connection')
parser.add_argument("-s", "--since", action='store', required=False, dest='since', type=valid_date,
                    help='fetch data for repositories since this date in the format YYYY-MM-DD (default is 1 year ago)')
parser.add_argument("-u", "--username", action='store', required=True, dest='username',
                    help='username to use for github connection')
parser.add_argument("-r", "--repository", action='append', required=False, dest='repositories', default=[],
                    help='repository to fetch data from; can be passed more than once')
args = parser.parse_args()

if args.since is None:
    # OK, one year ago it is
    since = datetime.datetime.now() - dateutil.relativedelta.relativedelta(years=1)
else:
    # Take the date from the command-line
    since = args.since

gh = github.MainClass.Github(args.username, args.password)

# The Github API limits you to 5000 requests per hour.
wait_time_ms = 60*1000*60

def retry_if_gh_rate_limit(exception):
    if isinstance(exception, github.GithubException):
        if exception.status == 403:
            if exception.data['documentation_url'] == 'https://developer.github.com/v3/#rate-limiting':
                print("")
                print("-------> Github rate-limited, sleeping an hour until %s" % (datetime.datetime.now() + datetime.timedelta(minutes=60)).strftime("%Y-%m-%d %H:%M:%S"))
                return True
    return False

@retrying.retry(retry_on_exception=retry_if_gh_rate_limit, wait_fixed=wait_time_ms)
def get_organizations(gh, name):
    return gh.get_organization(name)

@retrying.retry(retry_on_exception=retry_if_gh_rate_limit, wait_fixed=wait_time_ms)
def get_repos(org):
    return org.get_repos()

@retrying.retry(retry_on_exception=retry_if_gh_rate_limit, wait_fixed=wait_time_ms)
def get_single_repo(gh, reponame):
    return gh.get_repo(reponame)

@retrying.retry(retry_on_exception=retry_if_gh_rate_limit, wait_fixed=wait_time_ms)
def get_repo_stats(repo):
    print("Getting issues for %s..." % (repo.full_name)),
    sys.stdout.flush()

    # Here, figure out the total number of issues since our start
    # date, along with the number of issues closed since then
    # and the number of comments on issues since then.
    all_issues_count = 0
    closed_issues_count = 0
    issue_comment_count = 0
    for issue in repo.get_issues(state='all', since=since):
        all_issues_count += 1
        if issue.state == 'closed':
            closed_issues_count += 1

        for comment in issue.get_comments():
            issue_comment_count += 1

    # Now figure out the number of commits to the repository since
    # our start date.
    num_commits = 0
    for commit in repo.get_commits(since=since):
        num_commits += 1

    # Now figure out the number of comments to commits since our
    # start date.
    num_commit_comments = 0
    for commit_comment in repo.get_comments():
        if commit_comment.created_at >= since:
            num_commit_comments += 1

    # Here we iterate through the pull requests, looking at any that
    # have been merged, closed, or updated since "since".  As far as
    # I can tell, comments on the pull request itself go into the "issue comment"
    # bucket, but comments on the commits themselves (i.e. a review of the
    # code) is in a separate bucket.  I'll also note that I haven't yet seen
    # where reviews of *entire* commits are stored, since they don't seem
    # to show up either in the issue comment bucket or the pull request
    # comment bucket.
    total_pr_comments = 0
    for pull in repo.get_pulls():
        merged = pull.merged_at is not None and pull.merged_at >= since
        closed = pull.closed_at is not None and pull.closed_at >= since
        updated = pull.updated_at is not None and pull.updated_at >= since
        if merged or closed or updated:
            for comment in pull.get_comments():
                total_pr_comments += 1

    print("done")

    return RepoStatistics(repo.full_name, all_issues_count, closed_issues_count, num_commits, num_commit_comments, issue_comment_count, total_pr_comments)

repo_stats = []

# First iterate through all of the organizations, getting the
# repositories in those organizations, and adding them to a
# dict.
for orgname in args.organizations:
    org = get_organizations(gh, orgname)

    for repo in get_repos(org):
        repo_stats.append(get_repo_stats(repo))

for reponame in args.repositories:
    repo = get_single_repo(gh, reponame)

    repo_stats.append(get_repo_stats(repo))

print
print("----------------------- Most active repositories since %s ------------------" % (since))
print(RepoStatistics.header())
for stat in sorted(repo_stats, reverse=True):
    print(stat.csv())
