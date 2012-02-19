#!/usr/bin/env python3.2

from argparse import ArgumentParser
from localrepo.repo import Repo
from localrepo.msg import Msg
from localrepo.aur import Aur

class LocalRepo:
	def __init__(self, path):
		Msg.process('Loading local repo:', path)
		self.repo = Repo(path)

	def check(self):
		Msg.info(str(self.repo.size), 'packages found')
		Msg.process('Checking integrity')
		errors = self.repo.integrity_check()

		if not errors:
			Msg.info('No errors found')
			return

		for error in errors:
			Msg.error(error)

	def list(self):
		for pkg in self.repo.packages:
			Msg.info(pkg, self.repo.packages[pkg]['version'])

	def info(self, name):
		try:
			pkg = self.repo.package(name)
		except Exception as error:
			Msg.error(str(error))
			return False

		for i in pkg:
			Msg.info('{0:10} {1}'.format(i, pkg[i]))
		return True

	def search(self, q):
		results = self.repo.find_packages(q)

		if not results:
			Msg.info('No package found')
			return

		for pkg in results:
			Msg.info(pkg)

	def upgrade(self):
		Msg.info(str(self.repo.size), 'packages found')

		if not self.repo.packages:
			Msg.info('There is nothing to upgrade')
			return True

		Msg.process('Retrieving package infos from the AUR')

		try:
			packages = Aur.package_infos(self.repo.packages)
		except Exception as error:
			Msg.error(str(error))
			return False

		Msg.info(str(len(packages)), 'packages found')

		if not packages:
			Msg.info('There is nothing to upgrade')
			return True

		Msg.process('Updating local repo')
		updates = self.repo.update_packages(packages)

		if not updates:
			Msg.info('All packages are up to date')
			return True

		Msg.info('Updates are available')

		for pkg in updates:
			Msg.result('{0} ({1} -> {2})'.format(pkg, self.repo.package(pkg)['version'],
			           updates[pkg]['version']))

		if not Msg.yes('Update'):
			Msg.info('Bye')
			return True

		for pkg in updates:
			Msg.process('Upgrading package:', pkg)

			try:
				self.repo.add_package(pkg, updates[pkg])
			except Exception as error:
				Msg.error(str(error))
				return False

		return True

	def add(self, pkg):
		Msg.process('Retrieving package infos from the AUR')

		try:
			packages = Aur.package_infos([pkg])
		except Exception as error:
			Msg.error(str(error))
			return False

		if not packages:
			Msg.error('Package not found:', pkg)
			return False

		Msg.process('Adding package:', pkg)

		try:
			self.repo.add_package(pkg, packages[pkg])
		except Exception as error:
			Msg.error(str(error))
			return False

		return True

	def remove(self, pkg):
		Msg.process('Removing package:', pkg)

		try:
			self.repo.remove_package(pkg)
		except Exception as error:
			Msg.error(str(error))
			return False

		return True

if __name__ == '__main__':
	parser = ArgumentParser(description='a local repo helper')
	parser.add_argument('-c', '--check', action='store_true', dest='check', default=False,
	                    help='run an integrity check')
	parser.add_argument('-l', '--list', action='store_true', dest='list', default=False,
	                    help='list all packages of the repo')
	parser.add_argument('-i', '--info', action='store', dest='info', type=str,
	                    help='display package info', metavar='PKG')
	parser.add_argument('-s', '--search', action='store', dest='search', type=str,
	                    help='search for a package', metavar='QUE')
	parser.add_argument('-u', '--upgrade', action='store_true', dest='upgrade', default=False,
	                    help='upgrade all AUR packages in the repo')
	parser.add_argument('-a', '--add', action='store', dest='add', type=str,
	                    help='add a package from the AUR to the repo', metavar='PKG')
	parser.add_argument('-r', '--remove', action='store', dest='remove', type=str,
	                    help='remove a package from the repo', metavar='PKG')
	parser.add_argument('repopath', type=str, metavar='PATH', help='path to the local repo db')
	args = parser.parse_args()

	try:
		repo = LocalRepo(args.repopath)
	except Exception as error:
		Msg.error(str(error))
		exit(1)

	if args.check:
		repo.check()
	elif args.list:
		repo.list()
	elif args.info is not None:
		if not repo.info(args.info):
			exit(1)
	elif args.search is not None:
		repo.search(args.search)
	elif args.upgrade:
		if not repo.upgrade():
			exit(1)
	elif args.add is not None:
		if not repo.add(args.add):
			exit(1)
	elif args.remove is not None:
		if not repo.remove(args.remove):
			exit(1)
