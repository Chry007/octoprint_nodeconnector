# coding=utf-8
from __future__ import absolute_import
from octoprint import events

import octoprint.util
import octoprint.plugin

class NodeconnectorPlugin(octoprint.plugin.SettingsPlugin,
                          octoprint.plugin.AssetPlugin,
                          octoprint.plugin.TemplatePlugin):

	INTERVAL = 10

	def __init__(self):
		print("NODECONNECTOR INITIALIZING")
		self.x_travel = 0
		self.y_travel = 0
		self.z_travel = 0
		self.e_travel = 0
		self.x_last_position = 0
		self.y_last_position = 0
		self.z_last_position = 0
		self.e_last_position = 0

		self._timer = None


	def initialize(self):
		self._timer = octoprint.util.RepeatedTimer(self.INTERVAL, self._worker)
		self._timer.start()

	def get_settings_defaults(self):
		return dict(
			# put your plugin's default settings here
		)

	##~~ AssetPlugin mixin

	def get_assets(self):
		# Define your plugin's asset files to automatically include in the
		# core UI here.
		return dict(
			js=["js/nodeconnector.js"],
			css=["css/nodeconnector.css"],
			less=["less/nodeconnector.less"]
		)

	##~~ Softwareupdate hook

	def get_update_information(self):
		# Define the configuration for your plugin to use with the Software Update
		# Plugin here. See https://docs.octoprint.org/en/master/bundledplugins/softwareupdate.html
		# for details.
		return dict(
			nodeconnector=dict(
				displayName="Nodeconnector Plugin",
				displayVersion=self._plugin_version,

				# version check: github repository
				type="github_release",
				user="Chry007",
				repo="OctoPrint-Nodeconnector",
				current=self._plugin_version,

				# update method: pip
				pip="https://github.com/Chry007/OctoPrint-Nodeconnector/archive/{target_version}.zip"
			)
		)

	def line_sent_handler(self, comm_instance, phase, cmd, cmd_type, gcode, subcode=None, tags=None, *args, **kwargs):

        # print("received: ")


  		# print("received: " + cmd)


		if(gcode == "G1"):
			commands = cmd.split()
			for command in commands:
				position = float(command[1:])
				if(command.startswith("X")):
					self.x_travel += abs(self.x_last_position - position)
					self.x_last_position = position
				if (command.startswith("Z")):
					self.z_travel += abs(self.z_last_position - position)
					self.z_last_position = position
				if (command.startswith("Y")):
					self.y_travel += abs(self.y_last_position - position)
					self.y_last_position = position
				if (command.startswith("E")):
					self.e_travel += abs(self.e_last_position - position)
					self.e_last_position = position
		pass


	def on_event(self, event, payload):
		if event == octoprint.events.Events.CONNECTED:
			self.x_travel = 0
			self.y_travel = 0
			self.z_travel = 0
			self.e_travel = 0
			self.x_last_position = 0
			self.y_last_position = 0
			self.z_last_position = 0
			self.e_last_position = 0


	def _worker(self):
		self._logger.info("X:" + str(self.x_travel) + ", Y: " + str(self.y_travel) + ", Z: " + str(self.z_travel) + " E: " + str(self.e_travel))
		self.x_travel = 0
		self.y_travel = 0
		self.z_travel = 0
		self.e_travel = 0


# If you want your plugin to be registered within OctoPrint under a different name than what you defined in setup.py
# ("OctoPrint-PluginSkeleton"), you may define that here. Same goes for the other metadata derived from setup.py that
# can be overwritten via __plugin_xyz__ control properties. See the documentation for that.
__plugin_name__ = "Nodeconnector Plugin"

# Starting with OctoPrint 1.4.0 OctoPrint will also support to run under Python 3 in addition to the deprecated
# Python 2. New plugins should make sure to run under both versions for now. Uncomment one of the following
# compatibility flags according to what Python versions your plugin supports!
#__plugin_pythoncompat__ = ">=2.7,<3" # only python 2
#__plugin_pythoncompat__ = ">=3,<4" # only python 3
__plugin_pythoncompat__ = ">=2.7,<4" # python 2 and 3

def __plugin_load__():
	global __plugin_implementation__
	__plugin_implementation__ = NodeconnectorPlugin()

	global __plugin_hooks__
	__plugin_hooks__ = {
		"octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information,
		"octoprint.comm.protocol.gcode.sent": __plugin_implementation__.line_sent_handler
	}
