import sublime, sublime_plugin
import subprocess
import os
import json
import pathlib

class CoffeeFormatCommand(sublime_plugin.TextCommand):
  def run(self, edit):

    region = sublime.Region(0, self.view.size())
    content = self.view.substr(region)
    fname = self.view.file_name()
    #current = pathlib.Path(__file__).parent.resolve()

    tmp_file = "/tmp/code.coffee"
    with open(tmp_file, 'w') as f:
        f.write(content)


    cmd = ["coffee-fmt", 
           "--indent_style=space", 
           "--indent_size=2",
           "-i",
           tmp_file] 
    #print("cmd = %s" % " ".join(cmd))

    sublime.status_message("Coffee format starting..")

    stdout, stderr = subprocess.Popen(
      [" ".join(cmd)],
      stdin=subprocess.PIPE,
      stdout=subprocess.PIPE,
      stderr=subprocess.PIPE,
      shell=True).communicate()

    if stderr.strip():
      print("CoffeeScriptFormat ERROR: %s" % stderr.strip().decode())

      r = stderr.decode('UTF-8')
      if 'Error formatting' in r:

        description = r.split("\n")
        if len(description) > 0:
          description = description[1].strip()
        else:
          description = r

        sublime.error_message("Coffee format error: %s" % description)

    else:


      try:
        r = "%s\n" % stdout.decode('UTF-8').strip()
        self.view.replace(edit, region, r)
        sublime.status_message("Coffee format finished")
      except Exception as e:
        print("CoffeeScriptFormat fail: %s" % e)
        print("CoffeeScriptFormat ERROR: %s" % stderr.strip().decode())
        print("CoffeeScriptFormat RESULT: %s" % stdout.decode('UTF-8'))

def check_is_enabled_file(file_name):
  types = ['.coffee']

  for t in types:
    if file_name.lower().endswith(t):
      return True
  return False

class CoffeeEventDump(sublime_plugin.EventListener):


  def on_pre_save(self, view):
    if check_is_enabled_file(view.file_name()):
      view.run_command('coffee_format')
