#!/usr/bin/env python3.2

from os.path import dirname, exists, join

import builtins
import gettext

__all__ = ['aur', 'msg', 'package', 'pacman', 'repo']

def find_base():
	d = dirname(dirname(__file__))

	while not exists(join(d, 'local-repo')) and not exists(join(d, 'bin', 'local-repo')):
		d = dirname(d)

		if not exists(d):
			raise Exception('Could not find basepath')

	return d

BASE = find_base()

gettext.bindtextdomain('localrepo', join(BASE, 'share', 'locale'))
gettext.textdomain('localrepo')
builtins._ = gettext.gettext
