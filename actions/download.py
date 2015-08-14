#!/usr/bin/python
# coding=utf-8

import os
import sys
import logging

from ActionBase import register_action, ActionBase
from GoogleDriveService import *

logger = logging.getLogger(__name__)

@register_action(u'download', 'Download items from Google Drive')
class Download(ActionBase):
	def update_argparser(self, parser, argv):

		parser.add_argument(u'target',
				help=u"target path, can be files or folders")

		parser.add_argument(u'--output-folder', default=None,
				help=u"The local folder path to store downloaded files separated by '{0}'.".format(os.sep))

	def download_file(self, item, base_path = None):

		if base_path:
			file_path = os.sep.join([base_path.rstrip(os.sep), item[u'title']])
			if not os.path.exists(base_path):
				os.makedirs(base_path)
		else:
			file_path = os.sep.join([u'.', item[u'title']])

		logger.info(u'Donwloading a file: {0}'.format(item[u'title']))
		tmp_path = file_path + ".tmp"
		tmp_path = self.service.download_file(item[u'id'], tmp_path)
		if tmp_path:
			try:
				os.rename(tmp_path, file_path)
				logger.info(u"Download {0} to {1} successfully.".format(item[u'title'], file_path));
			except OSError, err:
				logger.warn(u"Cannot rename {0} to {1}.".format(item[u'title'], file_path));

	def download_folder(self, item, base_path = None):
		logger.info(u'Donwloading a folder: {0}'.format(item[u'title']))

		(dirs, files) = self.service.list(parent_id=item[u'id'])

		for f in files:
			self.download_file(f, os.sep.join([base_path, item[u'title']]))
		for d in dirs:
			self.download_folder(d, os.sep.join([base_path, item[u'title']]))

	def execute(self, options):

		logger.info(u"Processing DOWNLOAD")
		logger.debug(options)

		base_path = options.output_folder.rstrip(os.sep)
		if not os.path.exists(base_path):
			os.makedirs(base_path)

		item = self.service.get_item_by_path(options.target)
		if item == None:
			return -1

		if item[u'mimeType'] == GoogleDriveService.MIMETYPE_FOLDER:
			self.download_folder(item, base_path)
		else:
			self.download_file(item, base_path)
