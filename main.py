#!/usr/bin/env python

import datetime
import tempfile

import click
import git
from dateutil.relativedelta import relativedelta


@click.command()
@click.argument("url")
@click.option("--branch", default="main")
@click.option("--since-months", default=6)
def main(url, branch, since_months):
    with tempfile.TemporaryDirectory() as tempdir:
        print(f"Cloning {url} to {tempdir}")
        repo = git.Repo.clone_from(url, tempdir, branch=branch)

        print(f"Retrieving branch {branch}")
        branch = repo.heads[branch]
        if branch is None:
            print(f"No such branch: {branch}")
            exit(1)

        print(f"Retrieving commit authors from {branch}")
        target_date = datetime.datetime.utcnow() - relativedelta(months=since_months)
        print(f"Looking for commits since {target_date}")

        authors = {}
        done = False
        for commit in list(branch.commit.traverse()):
            dt = datetime.datetime.fromtimestamp(commit.committed_date)
            if not done and dt < target_date:
                print(f"Reached analysis constraint at commit date: {dt}")
                done = True

            if not done:
                auth = commit.author.email.split("@")[0]
                if auth in authors:
                    authors[auth]["count"] += 1
                    authors[auth]["emails"].add(commit.author.email)
                else:
                    authors[auth] = {"count": 1, "emails": set([commit.author.email])}

    for author in sorted(
        authors.keys(), key=lambda k: authors[k]["count"], reverse=True
    ):
        print(f"{author}:\t{authors[author]}")


if __name__ == "__main__":
    main()
